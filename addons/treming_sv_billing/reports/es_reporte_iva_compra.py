# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models

class ESReporteIvaCompra(models.AbstractModel):
    _name = 'report.treming_sv_billing.es_report_iva_compras'

    @api.model
    def render_html(self, docids, data=None):
        docargs = {            
            'data': dict(
                data
            ),
        }
        return self.env['report'].render(data["reporte"], docargs)