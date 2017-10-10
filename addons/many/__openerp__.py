# -*- coding: utf-8 -*-
{
    'name': "Aprendiendo Many",

    'summary': """Manage trainings""",

    'description': """
        Open Academy module for managing trainings:
            - training courses
            - training sessions
            - attendees registration
    """,

    'author': "Covantec R.L.",
    'website': "https://coderwall.com/team/covantec",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Test',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'web_gantt'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'many.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}