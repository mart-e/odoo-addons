# -*- coding: utf-8 -*-
{
    'name' : 'Crypto-currencies',
    'version' : '1.0',
    'summary': 'Manage crypto-currencies and convert',
    'description': """
Core mechanisms for the managing crypto-currencies.
Allow a higher decimal precision.
Track the current value of all your assets
    """,
    'category': 'Accounting',
    'depends' : ['decimal_precision', 'account'],
    'data': [
        'data/currency.xml',

        'views/asset.xml',
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
