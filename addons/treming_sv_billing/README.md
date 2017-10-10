En el caso de presentarse el siguiente error:

File "/odoo/odoo-server/odoo/models.py", line 5559, in __getitem__
    value = self._recs.env.cache[field][self._recs.id]
KeyError: 34

ó

File "/odoo/odoo-server/odoo/models.py", line 5559, in __getitem__
    value = self._recs.env.cache[field][self._recs.id
]
KeyError: 22

SOLUCION:
/# cd /odoo/odoo-server/treming/treming_sv_billing/models/
/# rm es_account_payment.py
/# rm es_account_payment.pyc
/# nano es_account_payment.py

Agregar el codigo fuente 

/--------------------------------------------------------------------------------------------------------------------------
/*

/# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError, UserError
from openerp import api, fields, models, _
class EsAccountPayment(models.Model):
    _inherit = "account.payment"
    @api.one
    @api.depends('invoice_ids', 'amount', 'payment_date', 'currency_id')
    def _compute_payment_difference(self):
        if len(self.invoice_ids) == 0:
            return
        if self.invoice_ids[0].type in ['out_refund']:
            self.payment_difference = self.amount - self.invoice_ids[0].residual
        elif self.invoice_ids[0].type in ['out_invoice', 'in_invoice']:
            self.payment_difference = self.invoice_ids[0].residual - self.amount
        else:
            self.payment_difference = self._compute_total_invoices_amount() - self.amount
    @api.multi
    def post(self):
        """ Create the journal items for the payment and update the payment's state to 'posted'.
            A journal entry is created containing an item in the source liquidity account (selected journal's default_debit or default_credit)
            and another in the destination reconciliable account (see _compute_destination_account_id).
            If invoice_ids is not empty, there will be one reconciliable move line per invoice to reconcile with.
            If the payment is a transfer, a second journal entry is created in the destination journal to receive money from the transfer account.
        """
        for rec in self:
            if rec.state != 'draft':
                raise UserError(_("Only a draft payment can be posted. Trying to post a payment in state %s.") % rec.state)
            if any(inv.state != 'open' for inv in rec.invoice_ids):
                raise ValidationError(_("The payment cannot be processed because the invoice is not open!"))
            # Use the right sequence to set the name
            if rec.payment_type == 'transfer':
                sequence_code = 'account.payment.transfer'
            else:
                if rec.partner_type == 'customer':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.customer.invoice'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.customer.refund'
                if rec.partner_type == 'supplier':
                    if rec.payment_type == 'inbound':
                        sequence_code = 'account.payment.supplier.refund'
                    if rec.payment_type == 'outbound':
                        sequence_code = 'account.payment.supplier.invoice'
            rec.name = self.env['ir.sequence'].with_context(ir_sequence_date=rec.payment_date).next_by_code(sequence_code)
            # Create the journal entry
            amount = rec.amount * (rec.payment_type in ('outbound', 'transfer') and 1 or -1)
            move = rec._create_payment_entry(amount)
            # In case of a transfer, the first journal entry created debited the source liquidity account and credited
            # the transfer account. Now we debit the transfer account and credit the destination liquidity account.
            if rec.payment_type == 'transfer':
                transfer_credit_aml = move.line_ids.filtered(lambda r: r.account_id == rec.company_id.transfer_account_id)
                transfer_debit_aml = rec._create_transfer_entry(amount)
                (transfer_credit_aml + transfer_debit_aml).reconcile()
            rec.write({'state': 'posted', 'move_name': move.name})
            # Para las factuas en las que he aplicado notas de debito o credito, ya cuando hago el pago final que deja el importe adeudado a cero
            # la linea de movimiento que refleja el pago se crea con reconciled igual a False
            # a diferencia de cuando pago el 100% de una factura a la que solo le aplique pagos, pero no notas
            # Para solventar esa situación hago lo siguiente
            #Recupero el registro de account invoice para determinar si es un pago a proveedor o de cliente
            id_inv = int(self.env.context["active_id"])
            obj_inv = self.env["account.invoice"].search([["id", "=", id_inv]])
            #Por defecto asume que es un pago de cliente
            balance = ["balance", "<", 0]
            cash_basis = ["credit_cash_basis", ">", 0]
            if obj_inv.type == "in_invoice":
                balance = ["balance", ">", 0]
                cash_basis = ["debit_cash_basis", ">", 0]
            movimiento = self.env["account.move.line"].search(["&","&",["payment_id", "!=", False],balance,cash_basis], order="id DESC", limit=1)
            movimiento.write({"reconciled":True, "amount_residual":0.0})
            for inv in rec.invoice_ids:
                inv.importe_adeudado()

*/
/------------------------------------------------------------------------------------------------------------------------

Siguiendo con la linea de comandos:
/# chmod 777 es_account_payment.py
/# service odoo-server start

Listo !!!