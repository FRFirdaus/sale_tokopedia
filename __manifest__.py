# -*- coding: utf-8 -*-
{
	'name': "Sale Tokopedia",
	'summary': """
		Sale Tokopedia""",
	'description': """
		Sale Tokopedia Integration
	""",
	'author': "Fahmi Roihanul Firdaus",
	'website': "https://www.frayhands.com",
	'version': '0.1',
	'category': 'Uncategorized',
	'version': '0.1',
	'depends': ['mail', 'base', 'sale', 'purchase', 'stock'],
	'images': ['static/description/icon.png'],
	'data': [
		'security/group.xml',
        'security/ir.model.access.csv',
        'views/merchant_tokopedia_views.xml',
		'data/account_token.xml',
        'views/sale_views.xml',
		'views/sale_tokopedia_templates.xml',
		'wizard/tokopedia_sync_wizard.xml'
    ],
	'qweb': ['static/src/xml/systray.xml'],
}
