from odoo import http
from odoo.tools.config import config
from odoo.http import request, Response
import requests
import json
import base64
import werkzeug

SHIPPING_LABEL_URL = 'https://fs.tokopedia.net/v1/order/%s/fs/%s/shipping-label'

class TokopediaShippingLabel(http.Controller):

    @http.route('/api/shipping/<int:sale_id>', auth='public', methods=['GET'])
    def get_shipping_label(self, sale_id=0):
        '''
            GET Shipping label
        '''
        sale_order = request.env['sale.order'].sudo().browse(sale_id)
        if not sale_order:
            return "Sale Order is not exist"

        try:
            url = SHIPPING_LABEL_URL % (sale_order.tp_order_id, sale_order.tp_fs_id)
            Auth = '%s %s' % (sale_order.tp_id.token_type, sale_order.tp_id.access_token)
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
            return response

    @http.route('/api/v1/file/<model_name>/<int:ref_id>/<view_pdf_name>', type='http', auth="public", website=True, sitemap=False)
    def open_pdf_file(self, model_name=None, ref_id=0, view_pdf_name=None, **kw):
        if model_name and ref_id and view_pdf_name:
            res_id = request.env[model_name].sudo().browse(ref_id)
            if res_id.shipping_label_data:
                docs = res_id.shipping_label_data
                base64_pdf = base64.b64decode(docs)
                pdf = base64_pdf
                return self.return_web_pdf_view(pdf)

    def return_web_pdf_view(self, pdf=None):
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', u'%s' % len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)