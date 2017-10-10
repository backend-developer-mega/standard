# -*- coding: utf-8 -*-
from openerp import http
from openerp.addons.web.controllers.main import serialize_exception, content_disposition

from odoo.http import Controller, route, request
import odoo.addons.report.controllers.main as main

class Binary(main.ReportController):
    @http.route('/web/binary/imprimir', type='http', auth="user")
    @serialize_exception
    def download_document(self, nombre, registro, **kw):
        objeto = request.env["account.invoice"].search([['id','=',registro]])[0]
        docids = []
        docids.append(int(registro))
        archivo = objeto.env['report'].get_pdf(docids, nombre)
        return request.make_response(archivo, [('Content-Type', 'application/pdf'), ('Content-Disposition', 'inline; filename="documento.pdf"')])