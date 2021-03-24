# -*- coding: utf-8 -*-

{
    'name': 'PRIX',
    'version': '1.0',
    'author': 'Jean Eudes TAPSOBA',
    'website': 'http://www.hsnconsult.com',
    'summary': 'LISTES DE PRIX',
    'description': "Listes de prix",
    'category': 'Sale',
    'depends': [
        'base',
        'sale',
        'product',
    ],
    'data': [
        'security/prix_security.xml',
        'security/ir.model.access.csv',
        'views/prix_view.xml',
        'views/report_listp.xml',
        'views/prix_report.xml',
    ],
    'installable': True,
    'auto_install': False,
}

