# -*- coding: utf-8 -*-

{
    'name': 'DASHBORD',
    'version': '1.0',
    'author': 'Jean Eudes TAPSOBA',
    'website': 'http://www.hsnconsult.com',
    'summary': 'TABLEAUX DE BORD',
    'description': "Tableaux de bord",
    'category': 'Sale',
    'depends': [
        'base',
        'sale',
        'product',
    ],
    'data': [
        'views/dashbord_view.xml',
        'views/dashbordcli_view.xml',
        'views/dashbordquali_view.xml',
        'views/menuitem_view.xml',
        'data/dash_data.xml',
    ],
    'installable': True,
    'auto_install': False,
}

