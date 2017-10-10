# -*- coding: utf-8 -*-
{
    'name': "Facturación El Salvador",

    'summary': """
        Crea las adecuación para actualizar la Facturación a El Salvador""",

    'description': """
        Realiza las adecuaciones a la legislación de El Salvador
    """,

    'author': "Grupo Treming",
    'website': "http://www.treming.com",

    # Categories can be used to filter modules in modules listing .
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accountable',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','hr','mail','treming_sv_taxpayer'],

    # always loaded
    'data': [
        'reports/layout.xml',
        'reports/documents.xml',
        'reports/es_report_ccf.xml',
        'reports/es_report_nota_credito.xml',
        'reports/es_report_facturacf.xml',
        'reports/es_report_factura_exportacion.xml',
        'reports/es_report_iva_compras.xml',
        'reports/es_report_ventas_consumidores.xml',
        'reports/es_report_ventas_contribuyentes.xml',
        'views/es_account_tax_view.xml',
        'views/es_tipos_documentos_view.xml',
        'views/es_ir_sequence_view.xml',
        'views/es_account_payment_term.xml',
        'views/es_account_invoice_form_alter.xml',
        'views/es_base_view_currency_form.xml',
        'views/es_product_template.xml',
        'views/es_account_view_account_position_form.xml',
        'views/sv_account_invoice_report_view.xml',
        'views/sv_account_config_settings_view.xml',
        'views/es_account_invoice_view.xml',  #Agrega el campo num CCF en Vendor Bills; Agrega num nota credito cuando se hace un Reembolso; Facturas de Proveedor
        'wizard/es_report_ventas_view.xml',
        'wizard/es_anular_view.xml',
        'wizard/es_libros_iva_view.xml',
        'wizard/es_invoice_refund.xml',
        'security/ir.model.access.csv',
        'views/sv_account_invoice_form_second.xml',
        'data/datos.xml',
    ],
}
