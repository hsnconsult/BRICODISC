# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Hsnpos',
    'version': '1.1',
    'summary': 'POS HSN',
    'sequence': 200,
    'description': """
POS Perso
====================
    """,
    'category': 'Accounting',
    'website': 'http://www.hsnconsult.com',
    'depends': ['sale', 'base', 'account', 'iwel'],
    'data': [
        'views/hsnpos_views.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False
}
