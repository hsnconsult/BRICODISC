# -*- coding: utf-8 -*-
{
    'name': "Kzm Stock Reports",

    'summary': """
        This module is about renaming stock picking reports""",

    'description': """
    
    """,

    'author': "Karizma",
    'website': "https://karizma-conseil.com/",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/reports_inherit.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        # 'demo/demo.xml',
    ],
}
