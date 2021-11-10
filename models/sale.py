from odoo import models, fields, api
from odoo.exceptions import ValidationError
from . import merchant_tokopedia as mp

import pdfkit
import base64
import json
import requests
import logging
_logger = logging.getLogger(__name__)

ACK_ORDER_URL = 'https://fs.tokopedia.net/v1/order/%s/fs/%s/ack'
PICKUP_REQUEST_URL = "https://fs.tokopedia.net/inventory/v1/fs/%s/pick-up"
SHIPPING_LABEL_URL = 'https://fs.tokopedia.net/v1/order/%s/fs/%s/shipping-label'

class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'

    tp_order_status = fields.Selection(mp.ORDER_STATUS)
    tp_order_id = fields.Char()
    tp_fs_id = fields.Char()
    tp_id = fields.Many2one('merchant.tokopedia')

    tp_seller_id = fields.Char()
    tp_shop_id = fields.Char()
    tp_shop_name = fields.Char()
    tp_shop_domain = fields.Char()
    tp_shop_owner_email = fields.Char()
    tp_shop_owner_phone = fields.Char()

    tp_buyer_id = fields.Char()
    tp_buyer_fullname = fields.Char()
    tp_buyer_email = fields.Char()
    tp_buyer_phone = fields.Char()

    tp_invoice_number = fields.Char()
    tp_invoice_url = fields.Char()
    tp_invoice_data = fields.Binary()

    tp_payment_number = fields.Char()
    tp_payment_status = fields.Char()

    tp_cancel_request_create_time = fields.Datetime('Create Time')
    tp_cancel_request_reason = fields.Char('Reason')
    tp_cancel_request_status = fields.Integer('Status')
    show_html_text = fields.Boolean()
    tp_text_shipping_html = fields.Text()
    tp_no_resi_shipping = fields.Char()
    
    shipping_label_data = fields.Binary()
    shipping_label_text = fields.Char()

    tokopedia_order = fields.Char(compute='_tokopedia_order_status')
    request_pickup_tokopedia = fields.Boolean(
        readonly=True,
        default=False
    )

    def get_buyer_info(self):
        try:
            shipping_text_html = self.tp_text_shipping_html

            no_resi_split = shipping_text_html.split("booking-code-text")
            no_resi_split_2 = no_resi_split[1].split(">")
            no_resi_split_3 = no_resi_split_2[1].split("<div")
            no_resi_final = no_resi_split_3[0].replace(" ", "")
            
            partner_fullname = shipping_text_html.split("Kepada:")
            partner_fullname_2 = partner_fullname[1].split("b>")
            partner_fullname_3 = partner_fullname_2[1].split("</")
            partner_fullname_4 = partner_fullname_3[0]
            partner_fullname_final = ' '.join([vals for vals in partner_fullname_4.split(" ") if vals])
            
            address_and_mobile_split = shipping_text_html.split("Kepada:")
            address_and_mobile_split_2 = address_and_mobile_split[1].split("<br />")
            address_dirty = address_and_mobile_split_2[3]
            mobile_dirty = address_and_mobile_split_2[4].split("</td>")
            self.tp_no_resi_shipping = no_resi_final
            self.partner_id.write({
                'name': partner_fullname_final,
                'street': ' '.join([vals for vals in address_dirty.split(" ") if vals]),
                'mobile': mobile_dirty[0].replace(" ", "")
            })
            self.tp_text_shipping_html = False
        except Exception as ex:
            self.message_post(body=ex)
        
    def shipping_label_view(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        raport_pdf_name = "Tokopedia shipping label for %s" % (self.tp_order_id)
        url = "/api/v1/file/%s/%s/%s" % (
            self._name,
            self.id,
            raport_pdf_name.replace(" ", "%20")
        )
        return {                   
            'name'     : 'Go to website',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'new',
            'url'      : url
        }

    def shipping_label_download(self):
        try:
            url = SHIPPING_LABEL_URL % (self.tp_order_id, self.tp_fs_id)
            Auth = '%s %s' % (self.tp_id.token_type, self.tp_id.access_token)
            headers = {
                'Authorization': Auth
            }
            r = requests.get(url, headers=headers)
            r.raise_for_status()
        except Exception as ex:
            response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
            _logger.error(response)
            message = "Failed get shipment label: %s, response: %s" % (ex, response)
            rec.message_post(body=message)
        else:
            status_code = r.status_code
            response = r.content
            shipping_label_data = pdfkit.from_string(str(response.decode('UTF-8')), False)
            encoded_datas = base64.b64encode(shipping_label_data)
            self.write({
                "tp_text_shipping_html": response,
                "shipping_label_data": encoded_datas,
                "shipping_label_text": "Shipping Label of %s" % (self.tp_order_id)
            })

    def button_show_ship_label(self):
        for rec in self:
            if rec.tp_id and rec.tp_fs_id and rec.tp_order_id and rec.tp_shop_id:
                url = rec.generate_url()
                return {                   
                    'name'     : 'Go to Invoice Tokopedia',
                    'res_model': 'ir.actions.act_url',
                    'type'     : 'ir.actions.act_url',
                    'target'   : 'new',
                    'url'      : url
                }

    def generate_url(self):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        result = "%s/api/shipping/%s" % (
            base_url,
            self.id
        )
        return result

    def button_tokopedia_request_picking(self):
        for rec in self:
            if rec.tp_id and rec.tp_fs_id and rec.tp_order_id and rec.tp_shop_id:
                try:
                    pickup_url = PICKUP_REQUEST_URL % (rec.tp_fs_id)
                    Auth = '%s %s' % (rec.tp_id.token_type, rec.tp_id.access_token)
                    payload = {
                        "order_id": int(rec.tp_order_id),
                        "shop_id": int(rec.tp_shop_id)
                    }
                    headers = {
                        'Authorization': Auth,
                        'Content-Type': 'application/json'
                    }
                    r = requests.post(pickup_url, data=json.dumps(payload), headers=headers)
                    r.raise_for_status()
                except Exception as ex:
                    response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
                    _logger.error(response)
                    message = "Failed sync pick-up request: %s, payload: %s, response: %s" % (ex, payload, response)
                    rec.message_post(body=message)
                else:
                    status_code = r.status_code
                    response = json.loads(r.text)
                    header = response.get('header')
                    data = response.get('data')
                    if data and header:
                        results = '''
                            <li>URL: %s</li>
                            <li>Order ID: %s</li>
                            <li>Shop ID: %s</li>
                            <li>Request Time: %s</li>
                            <li>Result: %s</li>
                            <li>Payload Request: %s</li>
                        ''' % (
                            pickup_url,
                            data['order_id'],
                            data['shop_id'],
                            data['request_time'],
                            data['result'],
                            json.dumps(payload, indent=2)
                        )
                        message = "<p><b>[%s][Request Pick-up] %s</b></p>: <ul>%s</ul>" % (
                            header['process_time'],
                            header['messages'],
                            results
                        )
                        rec.message_post(body=message)
                        rec.request_pickup_tokopedia = True
                        rec.tp_order_status = 450
            else:
                raise ValidationError(_(
                    "Can't Request Pick-up to Tokopedia \n\nPlease Check Order ID, Shop ID, FS/APP ID, and Odoo Tokopedia on Sale Order \none of them might be empty"
                ))

    def _tokopedia_order_status(self):
        for rec in self:
            rec.tokopedia_order = ""
            if rec.tp_order_id and rec.tp_order_status:
                rec.tokopedia_order = "[ID: %s] %s" % (rec.tp_order_id, mp.ORDER_STATUS_DICT[rec.tp_order_status])

    # @api.multi
    # def action_confirm(self):
    #     result = super(SaleOrderInherit, self).action_confirm()
    #     for rec in self:
    #         if rec.tp_order_id and rec.tp_id and rec.tp_order_status == 220:
    #             try:
    #                 sale_accept_url = ACK_ORDER_URL % (rec.tp_order_id, rec.tp_id.fs_id)
    #                 Auth = '%s %s' % (rec.tp_id.token_type, rec.tp_id.access_token)
    #                 headers = {
    #                     'Authorization': Auth,
    #                 }
    #                 r = requests.post(sale_accept_url, headers=headers)
    #                 r.raise_for_status()
    #             except Exception as ex:
    #                 response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
    #                 _logger.error(response)
    #                 message = "Failed sync accept order: %s, response: %s" % (ex, response)
    #                 rec.message_post(body=message)
    #             else:
    #                 status_code = r.status_code
    #                 response = json.loads(r.text)
    #                 header = response.get('header')
    #                 data = response.get('data') if status_code == 200 else {}
    #                 if data and header:
    #                     results = '''
    #                         <li>URL: %s</li>
    #                         <li>Data: %s</li>
    #                     ''' % (
    #                         sale_accept_url,
    #                         data
    #                     )
    #                     message = "<p><b>[%s][Accept Order] %s</b></p>: <ul>%s</ul>" % (
    #                         header['process_time'],
    #                         header['messages'],
    #                         results
    #                     )
    #                     rec.message_post(body=message)
    #                     rec.tp_order_status = 400

    #     return result

    def invoice_url_view(self):
        if not self.tp_invoice_url:
            raise ValidationError(_("Invoice URL is empty"))

        return {                   
            'name'     : 'Go to Invoice Tokopedia',
            'res_model': 'ir.actions.act_url',
            'type'     : 'ir.actions.act_url',
            'target'   : 'new',
            'url'      : self.tp_invoice_url
        }

class SaleOrderLineInherit(models.Model):
    _inherit = 'sale.order.line'

    tp_order_detail_id = fields.Integer(string="Order Detail ID")