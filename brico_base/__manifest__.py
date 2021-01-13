# -*- coding: utf-8 -*-
{
    'name': "Brico Base",
    'summary': """All default modification for Batch pickings""",
    'description': """Add modification to Odoo 13 batch pickings""",
    'author': "Assabe POLO, Karizma Conseil",
    'website': "https://karizma-conseil.com/",
    'category': 'Uncategorized',
    'version': '13.0',
    'depends': ['base', 'stock', 'stock_picking_batch'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/security.xml',
        'views/views.xml',
        'data/batch_picking_activity.xml',
        'reports/report_batch_picking.xml',

    ],
}
