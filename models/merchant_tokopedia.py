from odoo import models, fields, api, _
from odoo.tools.misc import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError
from . import order_data_dummy as odm
from datetime import datetime, timedelta
import base64
from base64 import b64encode
import sys
import os
import tzlocal
import pytz
import json
import requests
import pdfkit
import logging
_logger = logging.getLogger(__name__)

TOKEN_URL = 'https://accounts.tokopedia.com/token?grant_type=client_credentials'
BASE_URL = 'https://fs.tokopedia.net'

ORDER_STATUS_DICT = {
    0: 'Seller cancel order.',
    2: 'Order Reject Replaced.',
    3: 'Order Reject Due Empty Stock.',
    4: 'Order Reject Approval.',
    5: 'Order Canceled by Fraud',
    10: 'Order rejected by seller.',
    11: 'Order Pending Replacement.',
    15: 'Order canceled by system due buyer request.',
    100: 'Pending order.',
    103: 'Wait for payment confirmation from third party.',
    200: 'Payment confirmation.',
    220: 'Payment verified, order ready to process.',
    221: 'Waiting for partner approval.',
    400: 'Seller accept order.',
    450: 'Waiting for pickup.',
    500: 'Order shipment.',
    501: 'Status changed to waiting resi have no input.',
    520: 'Invalid shipment reference number (AWB).',
    530: 'Requested by user to correct invalid entry of shipment reference number.',
    540: 'Delivered to Pickup Point.',
    550: 'Return to Seller.',
    600: 'Order delivered.',
    601: 'Buyer open a case to finish an order.',
    690: 'Fraud Review',
    691: 'Suspected Fraud',
    695: 'Post Fraud Review',
    698: 'Finish Fraud Review',
    699: 'Order invalid or shipping more than 25 days and payment more than 5 days.',
    700: 'Order finished.',
    701: 'Order assumed as finished but the product not arrived yet to the buyer.',
}

ORDER_STATUS = [(i, ORDER_STATUS_DICT.get(i, 'Reserved by Tokopedia.')) for i in range(0, 1000) if i in [k for k in ORDER_STATUS_DICT.keys()]]

INTERVAL_GET_ORDER = [
    (3, "3 days before from current date"),
    (2, "2 days before from current date"),
    (1, "1 days before from current date"),
    (0, "Custom Interval Date")
]
class MerchantTokopedia(models.Model):
    _name = 'merchant.tokopedia'
    _inherit = ['mail.thread']
    _order = "fs_id"

    name = fields.Char(required=True)
    fs_id = fields.Integer('App ID', required=True)
    client_id = fields.Char('Client ID', required=True)
    client_secret = fields.Char('Client Secret',required=True)
    access_token = fields.Char('Access Token')
    expires_at = fields.Datetime(compute='_get_expires_at')
    expires_in = fields.Integer()
    token_type = fields.Char('Token Type')
    order_interval = fields.Selection(INTERVAL_GET_ORDER, default=3)
    order_from_date = fields.Datetime(default=datetime.now())
    order_to_date = fields.Datetime(default=datetime.now())
    active = fields.Boolean(default=True)

    shop_tokopedia_ids = fields.One2many('shop.tokopedia', 'merchant_tokopedia_id')
    ip_public = fields.Char(string="IP Public")
    whitelist_ids = fields.One2many('whitelist.tokopedia', 'merchant_tokopedia_id')

    result_message_sync_order = fields.Text()
    
    @api.depends('expires_in')
    def _get_expires_at(self, **kwargs):
        for rec in self:
            expires_at = datetime.now() + timedelta(seconds=rec.expires_in)
            rec.expires_at = expires_at.strftime(DEFAULT_SERVER_DATETIME_FORMAT)

    def get_access_token(self):
        self._get_access_token()

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.fs_id:
                result.append((record.id, "[%s] %s" % (record.fs_id, record.name)))

        return result

    def _get_access_token(self, **kwargs):
        for rec in self:
            if rec.client_id and rec.client_secret and isinstance(rec.id, int):
                try:
                    if rec.client_id and rec.client_secret:
                        r = requests.post(TOKEN_URL, headers={
                            'Authorization': 'Basic %s' % (b64encode(('%s:%s' % (rec.client_id, rec.client_secret)).encode('utf-8')).decode('utf-8')),
                            'Content-Length': '0',
                            'User-Agent': 'PostmanRuntime/7.26.1',
                        })
                        token_data = r.json() if r.status_code == 200 else {}

                        if token_data.get('access_token') and token_data.get('token_type'):
                            rec.access_token = token_data.get('access_token')
                            rec.token_type = token_data.get('token_type')
                            rec.expires_in = token_data.get('expires_in')

                        rec.message_post(body="%s" % (token_data))
                except Exception as e:
                    _logger.warn(e)

    @api.model
    def _cron_accounts_generate_access_token(self):
        tokopedia_accounts = self.search([])
        for account in tokopedia_accounts:
            account.get_access_token()

    def sync_shop(self):
        for rec in self:
            if rec.fs_id and rec.token_type and rec.access_token:
                try:
                    shop_info_url = "%s/v1/shop/fs/%s/shop-info" % (BASE_URL, rec.fs_id)
                    Auth = '%s %s' % (rec.token_type, rec.access_token)
                    headers = {
                        'Authorization': Auth
                    }
                    r = requests.get(shop_info_url, headers=headers)
                    r.raise_for_status()
                except Exception as ex:
                    response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
                    _logger.error(response)
                    message = "Failed sync shops: %s, response: %s" % (ex, response)
                    rec.message_post(body=message)
                else:
                    status_code = r.status_code
                    response = json.loads(r.text)
                    header = response.get('header')
                    data = response.get('data')
                    if data:
                        rec.shop_tokopedia_ids = [(5, 0, 0)]
                        shops_res = [{
                            'name': sd.get('shop_name'),
                            'shop_url': sd.get('shop_url'),
                            'shop_id': sd.get('shop_id')
                        } for sd in data]
                        shop_ids = [(0, 0, sr) for sr in shops_res]

                        rec.write({
                            'shop_tokopedia_ids': shop_ids
                        })
                        message = {
                            "header": header,
                            'shops': shops_res
                        }
                        rec.message_post(body="%s" % (message))
    
    def button_sync_all_order(self):
        for rec in self:
            if not rec.shop_tokopedia_ids:
                raise ValidationError(_("Can't sync order from tokopedia, at least there are 1 shop that was in active sync"))
            
            for shop in rec.shop_tokopedia_ids:
                shop.button_sync_order()

    def _cron_tokopedia_order(self):
        merchant_tokped = self.search([])
        for mt in merchant_tokped:
            try:
                mt.button_sync_all_order()
            except Exception as ex:
                mt.message_post(body="failed to sync tokopedia order from cron/scheduler: %s" % (ex))


    def insert_whitelist_ipaddress(self):
        self.sync_whitelist_ipaddress(**{'insert': self.ip_public})

    def delete_whitelist_ipaddress(self):
        self.sync_whitelist_ipaddress(**{'delete': self.ip_public})

    def get_whitelist_ipaddress(self):
        try:
            whitelist_url = "%s/v1/fs/%s/whitelist" % (BASE_URL, self.fs_id)
            Auth = '%s %s' % (self.token_type, self.access_token)
            headers = {
                'Authorization': Auth
            }
            r = requests.get(whitelist_url, headers=headers)
            r.raise_for_status()
        except Exception as ex:
            response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
            _logger.error(response)
            message = "Failed get IP whitelists: %s, response: %s" % (ex, response)
            self.message_post(body=message)
        else:
            status_code = r.status_code
            response = json.loads(r.text)
            header = response.get('header')
            data = response.get('data')
            if data:
                self.whitelist_ids = [(5, 0, 0)]
                whitelist_list = [(0, 0, {'name': wl}) for wl in data['ip_whitelisted']]
                self.write({
                    'whitelist_ids': whitelist_list
                })
                self.message_post(body="%s" % (response))
                self.ip_public = False

    def sync_whitelist_ipaddress(self, insert=False, delete=False):
        body = {}

        if not insert and not delete:
            raise ValidationError(_("Can't do whitelist request, Please define IP Public first"))

        if insert:
            body['insert'] = [insert]

        if delete:
            body['delete'] = [delete]

        try:
            whitelist_url = "%s/v1/fs/%s/whitelist" % (BASE_URL, self.fs_id)
            Auth = '%s %s' % (self.token_type, self.access_token)
            headers = {
                'Authorization': Auth
            }
            r = requests.post(whitelist_url, headers=headers, data=json.dumps(body))
            r.raise_for_status()
        except Exception as ex:
            response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
            _logger.error(response)
            message = "Failed sync IP whitelist: %s, response: %s" % (ex, response)
            self.message_post(body=message)
        else:
            status_code = r.status_code
            response = json.loads(r.text)
            header = response.get('header')
            data = response.get('data')
            if data:
                self.whitelist_ids = [(5, 0, 0)]
                whitelist_list = [(0, 0, {'name': wl}) for wl in data['ip_whitelisted']]
                self.write({
                    'whitelist_ids': whitelist_list
                })
                self.message_post(body="%s" % (response))
                self.ip_public = ""
            
class WhitelistTokopedia(models.Model):
    _name = 'whitelist.tokopedia'
    _order = "merchant_tokopedia_id"

    name = fields.Char(required=True, string="IP Public")
    merchant_tokopedia_id = fields.Many2one('merchant.tokopedia', ondelete='cascade')

class ShopTokopedia(models.Model):
    _name = 'shop.tokopedia'
    _order = "merchant_tokopedia_id"
    
    name = fields.Char(required=True)
    shop_url = fields.Char(required=True, string="Shop URL")
    shop_id = fields.Integer(required=True, string="Shop ID")
    merchant_tokopedia_id = fields.Many2one('merchant.tokopedia', ondelete='cascade')

    def _order_sync_date(self):
        result = {}
        format_date = "%Y-%m-%d %H:%M:%S.%f"
        mtp = self.merchant_tokopedia_id
        if mtp.order_interval:
            days = mtp.order_interval
            result['days_interval'] = days
        else:
            result['from_date'] = datetime.strptime(mtp.order_from_date.strftime(format_date), format_date) 
            result['to_date'] = datetime.strptime(mtp.order_to_date.strftime(format_date), format_date)

        return result

    @staticmethod
    def get_utc_datetime(dt, as_tz, dt_format=False):
        if not any([isinstance(dt, datetime), isinstance(dt, str)]):
            return False
        elif isinstance(dt, str):
            if not dt_format:
                return False
            dt = datetime.strptime(dt, dt_format)
        return pytz.timezone(as_tz).localize(dt).astimezone(pytz.UTC)

    @staticmethod
    def get_tp_dt_format(attr_name):
        dt_formats = {
            'create_time': '%Y-%m-%dT%H:%M:%S.%fZ',
            'payment_date': '%Y-%m-%dT%H:%M:%SZ'
        }
        return dt_formats.get(attr_name)

    def button_sync_order(self):
        order_date = self._order_sync_date()
        self.sync_order(**order_date)

    def sync_order(self, from_date=False, to_date=False, days_interval=False):
        from_date = from_date
        to_date = to_date
        processed_order=0
        try:
            date_end_sync = to_date
            if not date_end_sync:
                date_end_sync = datetime.today()

            date_start_sync = from_date
            if not date_start_sync:
                date_start_sync = date_end_sync - timedelta(days=days_interval)

            # Convert Timezone To UTC For Filtering. Because Timezone in Database is UTC
            server_timezone = tzlocal.get_localzone().zone
            dss_utc = pytz.timezone(server_timezone).localize(date_start_sync).astimezone(pytz.UTC)
            des_utc = pytz.timezone(server_timezone).localize(date_end_sync).astimezone(pytz.UTC)
            dss_utc_string = dss_utc.strftime("%Y-%m-%d %H:%M:%S")
            des_utc_string = des_utc.strftime("%Y-%m-%d %H:%M:%S")
            # +7 Hours For Parameter UNIX Timestamp in API Tokopedia. TO CONVERT THIS CAN NOT USE TIMEZONE and .timestamp(), because .timestamp() always in UTC+0
            dss_tokopedia = dss_utc + timedelta(hours=7)
            des_tokopedia = des_utc + timedelta(hours=7)
            timestamp_start_tokopedia = int(dss_tokopedia.timestamp())
            timestamp_end_tokopedia = int(des_tokopedia.timestamp())
            data_order = []
            created_new_customer = []
            cancel_request = []
            page = 1

            Auth = '%s %s' % (self.merchant_tokopedia_id.token_type, self.merchant_tokopedia_id.access_token)

            all_order_url = '%s/v2/order/list?fs_id=%s&shop_id=%s&from_date=%s&to_date=%s&page=%s&per_page=50' % (
                BASE_URL,
                self.merchant_tokopedia_id.fs_id,
                self.shop_id,
                timestamp_start_tokopedia,
                timestamp_end_tokopedia,
                page
            )
            r = requests.get(all_order_url, headers={
                # Call the get_access_token method instead of the attribute directly to prevent getting expired token.
                'Authorization': Auth
            })
            r.raise_for_status()
            response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
            result = response.get('header', {"status_code": r.status_code})
            if result:
                result["url"] = all_order_url
                result['date'] = {
                    "date_to": des_tokopedia.strftime("%A, %d %B %Y %H:%M:%S"),
                    "date_start": dss_tokopedia.strftime("%A, %d %B %Y %H:%M:%S")
                }
                data_results = response.get('data') if response.get('data') else []
                result['data_results'] = len(data_results)
                self.merchant_tokopedia_id.message_post(body="%s" % (result)) 
        except Exception as ex:
            response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
            _logger.error(response)
            message = "Failed sync tokopedia orders: %s, response: %s" % (ex, response)
            self.merchant_tokopedia_id.message_post(body=message)
        else:
            datas = response.get('data') if r.status_code == 200 else []
            
            # data_res = datas if datas else odm.all_orders_dummy['data']
            new_order_datas = []
            if datas:
                # new_order_datas = [new_order for new_order in datas if new_order.get('order_status') and new_order.get('order_status') in [220, 400]]
                new_order_datas = [new_order for new_order in datas if new_order.get('order_status') and new_order.get('order_status') in [400]]
            if new_order_datas:
                for data in new_order_datas:
                    tokopedia_order = self.env['sale.order'].sudo().search([('tp_order_id', '=', data.get('order_id', "None"))])
                    _logger.info(data)
                    if tokopedia_order:
                        # if tokopedia_order.tp_order_status in [220, 400]:
                        if tokopedia_order.tp_order_status in [400]:
                            try:
                            # Get Detail
                                get_existing_url = '%s/v2/fs/%s/order?order_id=%s' % (
                                    BASE_URL,
                                    self.merchant_tokopedia_id.fs_id,
                                    tokopedia_order.tp_order_id
                                )
                                r = requests.get(get_existing_url, headers={
                                    'Authorization': Auth
                                })
                                r.raise_for_status()
                            except Exception as ex:
                                response = json.loads(r.text) if r.status_code not in [403, 401] else {'status_code': r.status_code}
                                _logger.error(response)
                                message = "Failed sync tokopedia single existing order: %s, response: %s" % (ex, response)
                                self.merchant_tokopedia_id.message_post(body=message)
                            else:
                                detail_order = r.json() if r.status_code == 200 else {}
                                detail_order = detail_order['data']

                                if detail_order['cancel_request_info'] and not tokopedia_order.tp_cancel_request_reason:
                                    tokopedia_order.write({
                                        'tp_cancel_request_create_time': self.get_utc_datetime(detail_order['cancel_request_info']['create_time'], 'Asia/Jakarta', self.get_tp_dt_format('create_time')),
                                        'tp_cancel_request_reason': detail_order['cancel_request_info']['reason'],
                                        'tp_cancel_request_status': detail_order['cancel_request_info']['status']
                                    })
                                    cancel_request.append({
                                        'sale_number': tokopedia_order.name,
                                        'tokopedia_order': tokopedia_order.tp_order_id,
                                        'cancel_request': {
                                            'create_time': tokopedia_order.tp_cancel_request_create_time,
                                            'reason': tokopedia_order.tp_cancel_request_reason,
                                            'status': tokopedia_order.tp_cancel_request_status
                                        }
                                    })
                    else:
                        try:
                            single_order_url = '%s/v2/fs/%s/order?invoice_num=%s' % (
                                BASE_URL,
                                self.merchant_tokopedia_id.fs_id,
                                data.get('invoice_ref_num')
                            )
                            req = requests.get(single_order_url, headers={
                                # Call the get_access_token method instead of the attribute directly to prevent getting expired token.
                                'Authorization': Auth
                            })
                            req.raise_for_status()
                            response = json.loads(req.text) if req.status_code not in [403, 401] else {'status_code': req.status_code}
                        except Exception as ex:
                            response = json.loads(req.text) if req.status_code not in [403, 401] else {'status_code': req.status_code}
                            _logger.error(response)
                            message = "Failed sync tokopedia single order: %s, response: %s" % (ex, response)
                            self.merchant_tokopedia_id.message_post(body=message)
                        else:
                            datas_single = response.get('data') if req.status_code == 200 else {}
                            # if datas_single['order_status'] in [220, 400]:
                            if datas_single['order_status'] in [400]:
                                buyer_full_name = datas_single['buyer_info']['buyer_fullname'] if datas_single['buyer_info']['buyer_fullname'] else "Tokopedia Buyer [ID %s]" % (
                                    datas_single['buyer_info']['buyer_id']
                                )
                                customer_order_id = self.env['res.partner'].search(['|', ('name', '=', buyer_full_name), ('ref', '=', "TP%s" % (datas_single['buyer_info']['buyer_id']))])
                                if not customer_order_id:
                                    customer_order_id = self.env['res.partner'].create({
                                        'name': buyer_full_name,
                                        'ref': "TP%s" % (datas_single['buyer_info']['buyer_id']),
                                        'customer': True,
                                        'email': datas_single['buyer_info']['buyer_email'],
                                        'mobile': datas_single['buyer_info']['buyer_phone']
                                    })
                                    created_new_customer.append({
                                        'name': customer_order_id.name,
                                        'id': customer_order_id.id,
                                        'ref': customer_order_id.ref
                                    })
                                order_lines = datas_single['order_info']['order_detail']
                                sale_order_line = []
                                for line in order_lines:
                                    product_tmpl_id = self.env['product.template'].search(['|', ('default_code', '=', line['sku']), ('name', '=', line['product_name'])])
                                    if not product_tmpl_id:
                                        raise ValidationError(_("Product is not found by SKU '%s' or Name '%s'" % (line['sku'], line['product_name'])))

                                    product = self.env['product.product'].search([('product_tmpl_id', '=', product_tmpl_id[0].id)])

                                    sale_order_line.append((0, 0 ,{
                                        'tp_order_detail_id': line['order_detail_id'],
                                        'product_id': product.id,
                                        'product_uom_qty': line['quantity'],
                                        'price_unit': line['product_price']
                                    }))
                                
                                # invoice_datas = pdfkit.from_url(datas_single['invoice_url'], False)
                                # encoded_datas = base64.b64encode(invoice_datas)
                                vals = {
                                    'tp_id': self.merchant_tokopedia_id.id,
                                    'tp_order_status': datas_single['order_status'],
                                    'tp_order_id': datas_single['order_id'],
                                    'tp_fs_id': str(self.merchant_tokopedia_id.fs_id),
                                    'tp_seller_id': datas_single['seller_id'],
                                    'tp_shop_id': datas_single['shop_info']['shop_id'],
                                    'tp_shop_name': datas_single['shop_info']['shop_name'],
                                    'tp_shop_domain': datas_single['shop_info']['shop_domain'],
                                    'tp_shop_owner_email': datas_single['shop_info']['shop_owner_email'],
                                    'tp_buyer_id': datas_single['buyer_info']['buyer_id'],
                                    'tp_buyer_fullname': datas_single['buyer_info']['buyer_fullname'],
                                    'tp_buyer_email': datas_single['buyer_info']['buyer_email'],
                                    'tp_buyer_phone': datas_single['buyer_info']['buyer_phone'],
                                    'tp_invoice_number': datas_single['invoice_number'],
                                    'tp_invoice_url': datas_single['invoice_url'],
                                    # 'tp_invoice_data': encoded_datas,
                                    'tp_payment_number': datas_single['payment_info']['payment_ref_num'],
                                    'tp_payment_status': datas_single['payment_info']['payment_status'],
                                    'date_order': self.get_utc_datetime(datas_single['create_time'], 'Asia/Jakarta', self.get_tp_dt_format('create_time')),
                                    'partner_id': customer_order_id.id,
                                    'order_line': sale_order_line
                                }

                                if datas_single['cancel_request_info']:
                                    vals['tp_cancel_request_create_time'] = self.get_utc_datetime(datas_single['cancel_request_info']['create_time'], 'Asia/Jakarta', self.get_tp_dt_format('create_time'))
                                    vals['tp_cancel_request_reason'] = datas_single['cancel_request_info']['reason']
                                    vals['tp_cancel_request_status'] = datas_single['cancel_request_info']['status']

                                create_sale_order = self.env['sale.order'].create(vals)

                                create_sale_order.shipping_label_download()
                                create_sale_order.get_buyer_info()

                                date_order_result = {
                                    'sale_id': create_sale_order.id,
                                    'sale_number': create_sale_order.name,
                                    'tokopedia_order_id': create_sale_order.tp_order_id,
                                    'order_lines': [{
                                        'sku': ol['sku'],
                                        'quantity': ol['quantity'],
                                        'price': ol['product_price']
                                    } for ol in order_lines],
                                }

                                if create_sale_order.tp_cancel_request_status:
                                    cancel_request.append({
                                        'sale_number': create_sale_order.name,
                                        'tokopedia_order': create_sale_order.tp_order_id,
                                        'cancel_request_detail': {
                                            'reason': create_sale_order.tp_cancel_request_reason,
                                            'status': create_sale_order.tp_cancel_request_status
                                        }
                                    })

                                data_order.append(date_order_result)

            created_order_message = {
                'order_created': {
                    'total': len(data_order),
                    'order_details': data_order
                },
                'created_customer': created_new_customer,
                'order_cancel_request': cancel_request
            }

            self.merchant_tokopedia_id.message_post(body=created_order_message)
                        
                    
            