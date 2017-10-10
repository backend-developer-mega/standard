# -*- coding: utf-8 -*-
from openerp import http

# class Esinvoice(http.Controller):
#     @http.route('/esinvoice/esinvoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/esinvoice/esinvoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('esinvoice.listing', {
#             'root': '/esinvoice/esinvoice',
#             'objects': http.request.env['esinvoice.esinvoice'].search([]),
#         })

#     @http.route('/esinvoice/esinvoice/objects/<model("esinvoice.esinvoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('esinvoice.object', {
#             'object': obj
#         })