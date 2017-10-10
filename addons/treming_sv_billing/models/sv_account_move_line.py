# -*- coding: utf-8 -*-
from odoo import api, fields, models

class SVAccountMoveLine(models.Model):
    _inherit = "account.move.line"

    @api.multi
    def remove_move_reconcile(self):
        """ Undo a reconciliation """
        if not self:
            return True
        rec_move_ids = self.env['account.partial.reconcile']
        for account_move_line in self:
            for invoice in account_move_line.payment_id.invoice_ids:
                if invoice.id == self.env.context.get('invoice_id') and account_move_line in invoice.payment_move_line_ids:
                    account_move_line.payment_id.write({'invoice_ids': [(3, invoice.id, None)]})
            rec_move_ids += account_move_line.matched_debit_ids
            rec_move_ids += account_move_line.matched_credit_ids
        if len(rec_move_ids) == 0:
            #Si la longitud de rec_move_ids es igual a cero se que cuando ejecute la funcion unlink no va
            #a pasar nada, entonces para que se rompa la conciliacion lo que hago es cambiar los valores de reconciled a False
            #y de amount residual que pasara de 0 al valor que tenga en total
            for account_move_line in self:
                account_move_line.write({"reconciled": False, "amount_residual": account_move_line.balance})
                #Para que se actualice el importe adeudado
                invoice_id = self.env.context.get('invoice_id')
                invoice_obj = self.env["account.invoice"].search([["id", "=", invoice_id]])
                invoice_obj.importe_adeudado()

        #El importe adeudado no se actualiza correctamente para las facturas de proveedor cuando se rompe una conciliacion
        #Por lo que si el tipo del documento es out_invoice entonces llamo el método importe_adeudo
        return rec_move_ids.unlink()