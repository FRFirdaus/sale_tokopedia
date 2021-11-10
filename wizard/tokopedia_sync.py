from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import datetime

INTERVAL_GET_ORDER = [
    (3, "3 days before from current date"),
    (2, "2 days before from current date"),
    (1, "1 days before from current date"),
    (0, "Custom Interval Date")
]

class MerchantTokopedia(models.TransientModel):
    _name = 'merchant.tokopedia.wizard'

    merchant_tokopedia_id = fields.Many2one('merchant.tokopedia')

    fs_id = fields.Integer('App ID', readonly=True)
    client_id = fields.Char('Client ID', readonly=True)
    client_secret = fields.Char('Client Secret', readonly=True)
    access_token = fields.Char('Access Token', readonly=True)
    expires_at = fields.Datetime(readonly=True)
    expires_in = fields.Integer(readonly=True)
    token_type = fields.Char('Token Type', readonly=True)
    order_interval = fields.Selection(INTERVAL_GET_ORDER, default=3)
    order_from_date = fields.Datetime(default=datetime.now())
    order_to_date = fields.Datetime(default=datetime.now())

    shop_tokopedia_ids = fields.One2many('shop.tokopedia.wizard', 'merchant_tokopedia_wizard_id')

    @api.onchange('merchant_tokopedia_id')
    def onchange_merchant_tokopedia(self):
        if self.merchant_tokopedia_id:
            self.fs_id = self.merchant_tokopedia_id.fs_id
            self.client_id = self.merchant_tokopedia_id.client_id
            self.client_secret = self.merchant_tokopedia_id.client_secret
            self.access_token = self.merchant_tokopedia_id.access_token
            self.token_type = self.merchant_tokopedia_id.token_type
            self.expires_at = self.merchant_tokopedia_id.expires_at
            self.expires_in = self.merchant_tokopedia_id.expires_in
            
            self.shop_tokopedia_ids = [(5, 0, 0)]
            self.shop_tokopedia_ids = [(0, 0, {
                'shop_tokopedia_id': shop.id,
                'name': shop.name,
                'shop_url': shop.shop_url,
                'shop_id': shop.shop_id,
                'sync_active': True
            }) for shop in self.merchant_tokopedia_id.shop_tokopedia_ids]

    def _order_sync_date_wizard(self):
        result = {}
        format_date = "%Y-%m-%d %H:%M:%S.%f"
        mtp = self
        if mtp.order_interval:
            days = mtp.order_interval
            result['days_interval'] = days
        else:
            result['from_date'] = datetime.strptime(mtp.order_from_date.strftime(format_date), format_date) 
            result['to_date'] = datetime.strptime(mtp.order_to_date.strftime(format_date), format_date)

        return result

    def order_sync_tokopedia(self):
        if not self.merchant_tokopedia_id:
            raise ValidationError(_("Merchant tokopedia must be set"))

        active_sync = self.shop_tokopedia_ids.filtered(lambda x: x.sync_active)
        if not active_sync:
            raise ValidationError(_("Can't sync order from tokopedia, at least there are 1 shop that was in active sync"))

        for shop in active_sync:
            order_date = self._order_sync_date_wizard()
            shop.action_sync_order_wizard(order_date)

class ShopTokopediaWizard(models.TransientModel):
    _name = 'shop.tokopedia.wizard'
    
    shop_tokopedia_id = fields.Integer()
    name = fields.Char()
    shop_url = fields.Char(string="Shop URL")
    shop_id = fields.Integer(string="Shop ID")
    sync_active = fields.Boolean(string="Sync")
    merchant_tokopedia_wizard_id = fields.Many2one('merchant.tokopedia.wizard', ondelete='cascade')

    def action_sync_order_wizard(self, order_date):
        shop = self.env['shop.tokopedia'].browse(self.shop_tokopedia_id)
        shop.sync_order(**order_date)
