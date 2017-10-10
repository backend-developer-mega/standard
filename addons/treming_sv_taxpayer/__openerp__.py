# -*- coding: utf-8 -*-
{
    'name': "Contribuyentes de El Salvador",

    'summary': """
        Modulo para la adición de campos tributarios de El Salvador""",

    'description': """
        Adiciona campos tributarios de El Salvador al formulario de clientes
    """,

    'author': "Grupo Treming",
    'website': "http://www.treming.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        'data/datos.xml',
        'views/es_res_partner_view.xml',
        'views/es_res_company_view.xml',
    ],    
}
