# -*- coding: utf-8 -*-
{
    'name': "Requisición de Personal",

    'summary': """
        Modulo de gestion de requisiciones de personal.""",

    'description': """
        Administra las requisiciones de personal.
    """,

    'author': "Grupo Treming",
    'website': "https://www.treming.com",

    # Categories can be used to filter modules in modules listing
    'category': 'Employees',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['hr_recruitment'],

    # always loaded
    'data': [
        #'reports/layout.xml',
        #'reports/documents.xml',
        #'reports/es_report_quotation.xml',
        'security/user_groups.xml',
        'security/ir.model.access.csv',
        'views/es_hr_requisition.xml',
        'views/es_hr_applicant.xml',
        'views/es_hr_employee.xml',
        'views/es_hr_requisition_workflow.xml',
        'views/es_hr_recruitment.xml',
        'views/es_hr_responsable.xml',
        'views/es_priority.xml',
        'views/es_hr_module.xml',
        'demo/demo.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}
