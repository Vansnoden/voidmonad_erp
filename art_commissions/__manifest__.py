# -*- coding: utf-8 -*-
{
    'name': "art_commissions",

    'summary': """
        A simple module for art commission management
    """,

    'description': """
        A simple module for art commission management
    """,

    'author': "@dess",
    'website': "http://www.monadeware.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['sale_management', 'website'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/backend/commission_views.xml',
        'views/backend/menu.xml',
        'views/frontend/commission_form.xml',
        'data/commission_products.xml',
        'data/commission_sequence.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
