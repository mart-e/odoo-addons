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
    'depends' : ['cryptocurrency', 'account'],
    'data': [
        'views/asset.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': True,
}
