# -*- coding: utf-8 -*-
from odoo import http

# class TremingSvWebsiteV2.0(http.Controller):
#     @http.route('/treming_sv_website_v2.0/treming_sv_website_v2.0/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/treming_sv_website_v2.0/treming_sv_website_v2.0/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('treming_sv_website_v2.0.listing', {
#             'root': '/treming_sv_website_v2.0/treming_sv_website_v2.0',
#             'objects': http.request.env['treming_sv_website_v2.0.treming_sv_website_v2.0'].search([]),
#         })

#     @http.route('/treming_sv_website_v2.0/treming_sv_website_v2.0/objects/<model("treming_sv_website_v2.0.treming_sv_website_v2.0"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('treming_sv_website_v2.0.object', {
#             'object': obj
#         })