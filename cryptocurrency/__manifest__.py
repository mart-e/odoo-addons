# -*- coding: utf-8 -*-
{
    'name' : 'Crypto-currencies',
    'version' : '1.0',
    'summary': 'Manage crypto-currencies and convert',
    'description': """
Core mechanisms for the managing crypto-currencies.
Allow a precision high enough and track assets value.
    """,
    'category': 'Accounting',
    'depends' : ['decimal_precision'],
    'data': [
        'data/currency.xml',
        'views/sync_wizard.xml',
    ],
    'demo': [
    ],
    'qweb': [
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
