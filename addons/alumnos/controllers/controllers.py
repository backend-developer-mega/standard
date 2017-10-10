# -*- coding: utf-8 -*-
from odoo import http

# class Alumnos(http.Controller):
#     @http.route('/alumnos/alumnos/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"
# 
#     @http.route('/alumnos/alumnos/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('alumnos.listing', {
#             'root': '/alumnos/alumnos',
#             'objects': http.request.env['alumnos.alumnos'].search([]),
#         })
# 
#     @http.route('/alumnos/alumnos/objects/<model("alumnos.alumnos"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('alumnos.object', {
#             'object': obj
#         })