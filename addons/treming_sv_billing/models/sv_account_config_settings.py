# -*- coding: utf-8 -*-
from openerp import api, fields, models

class SvAccountConfigSettings(models.TransientModel):
    _inherit = 'account.config.settings'

    def perform_compute_new_fields(self):
        invoices = self.env["account.invoice"].search([["id", "!=", "0"]])
        for invoice in invoices:
            invoice.compute_new_fields()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }