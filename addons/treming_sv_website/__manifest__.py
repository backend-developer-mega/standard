# -*- coding: utf-8 -*-
{
    'name': "treming_sv_website",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['website','website_crm','website_hr_recruitment', 'website_blog','im_livechat'],



    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/assets.xml',
        'views/nav.xml',
        'views/home.xml',
        'views/footer.xml',
        'views/contactus.xml',
        'views/about-us.xml',
        'views/video-gallery.xml',




        'views/services-odoo/accounting.xml',
        'views/services-odoo/crm.xml',
        'views/services-odoo/invoicing.xml',
        'views/services-odoo/payroll.xml',



        'views/home/cod-lib.xml',
        'views/home/open.xml',
        'views/home/cost-eff.xml',
        'views/home/cust-par.xml',
        'views/home/hir.xml',
        'views/home/out.xml',
        'views/home/qua-cod.xml',
        'views/home/use-cen-des.xml',

        'views/outsourcing/outsourcing.xml',
        'views/head-hunter/head-hunter.xml',
        'views/training/training.xml',





        'views/odoo/odoo.xml',
        'views/odoo/odoo-10.xml',
        'views/odoo/odoo-app-dev.xml',
        'views/odoo/odoo-mod.xml',
        'views/odoo/odoo-video.xml',
        'views/odoo/odoo-com-vs-ent.xml',
        'views/odoo/odoo-sus-sto.xml',
        'views/odoo/odoo-whi-pap.xml',
        'views/odoo/odoo-custom.xml',
        'views/odoo/odoo-cont.xml',
        'views/odoo/odoo-dat-mig.xml',


        'views/iot/iot.xml',




        'views/mob-dev/mob-app-dev.xml',
        'views/mob-dev/mob-android-app.xml',
        'views/mob-dev/mob-app.xml',
        'views/mob-dev/mob-cas.xml',
        'views/mob-dev/mob-hybrid-app.xml',
        'views/mob-dev/mob-ios-app.xml',
        'views/mob-dev/mob-mvp.xml',
        'views/mob-dev/mob-por.xml',
        'views/mob-dev/mob-pro.xml',
        'views/mob-dev/mob-req.xml',
        'views/mob-dev/mob-ui.xml',


        'views/web-dev/web-dev.xml',
        'views/web-dev/web-bra.xml',
        'views/web-dev/web-cas.xml',
        'views/web-dev/web-e-com.xml',
        'views/web-dev/web-po.xml',
        'views/web-dev/web-req-ana.xml',
        'views/web-dev/web-req-quo.xml',
        'views/web-dev/web-seo.xml',
        'views/web-dev/web-tec.xml',
        'views/web-dev/web-tra.xml',
        'views/web-dev/web-por.xml',


        'views/sap/sap.xml',



        'views/jobs.xml',

        'views/website_quote_template_custon.xml',

        'views/technologies/ios.xml',
        'views/technologies/android.xml',
        'views/technologies/fe.xml',
        'views/technologies/bk.xml',

        'views/blog.xml',

        'data/data.xml',





    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

