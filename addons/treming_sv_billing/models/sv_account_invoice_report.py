# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class SvAccountInvoiceReport(models.Model):
    _inherit = "account.invoice.report"

    iva = fields.Float(string="IVA", readonly=True)
    amount_unt = fields.Float(string='Monto sin impuestos', readonly=True)
    retention_perception = fields.Float(string='Retenido/Percibido', readonly=True)
    amount_with_iva = fields.Float(string='Monto con IVA', readonly=True)
    amount_ts = fields.Float(string='Total', readonly=True)
    residuo = fields.Float(string='Importe Adeudado', readonly=True)

    def _select(self):
        select_str = """
            SELECT sub.id, sub.date, sub.product_id, sub.partner_id, sub.country_id, sub.account_analytic_id,
                sub.payment_term_id, sub.uom_name, sub.currency_id, sub.journal_id,
                sub.fiscal_position_id, sub.user_id, sub.company_id, sub.nbr, sub.type, sub.state,
                sub.weight, sub.volume,
                sub.categ_id, sub.date_due, sub.account_id, sub.account_line_id, sub.partner_bank_id,
                sub.product_qty, sub.price_total as price_total, sub.amount_untaxed as amount_unt, sub.iva as iva,
                sub.ret_per as retention_perception, sub.new_subtotal as amount_with_iva, sub.price_average as price_average, sub.amount_total_signed as amount_ts,
                COALESCE(cr.rate, 1) as currency_rate, sub.residuo as residuo, sub.residual as residual, sub.commercial_partner_id as commercial_partner_id
        """
        return select_str

    def _sub_select(self):
        select_str = """
                SELECT ail.id AS id,
                    ai.date_invoice AS date,
                    ail.product_id, ai.partner_id, ai.payment_term_id, ail.account_analytic_id,
                    u2.name AS uom_name,
                    ai.currency_id, ai.journal_id, ai.fiscal_position_id, ai.user_id, ai.company_id, ai.amount_untaxed, ai.iva, ai.ret_per, ai.new_subtotal,
                    ai.amount_total_signed, 1 AS nbr,
                    ai.type, ai.state, pt.categ_id, ai.date_due, ai.account_id, ail.account_id AS account_line_id,
                    ai.partner_bank_id, ai.residual_signed as residuo,
                    SUM ((invoice_type.sign * ail.quantity) / u.factor * u2.factor) AS product_qty,
                    SUM(ail.price_subtotal_signed) AS price_total,
                    SUM(ABS(ail.price_subtotal_signed)) / CASE
                            WHEN SUM(ail.quantity / u.factor * u2.factor) <> 0::numeric
                               THEN SUM(ail.quantity / u.factor * u2.factor)
                               ELSE 1::numeric
                            END AS price_average,
                    ai.residual_company_signed / (SELECT count(*) FROM account_invoice_line l where invoice_id = ai.id) *
                    count(*) * invoice_type.sign AS residual,
                    ai.commercial_partner_id as commercial_partner_id,
                    partner.country_id,
                    SUM(pr.weight * (invoice_type.sign*ail.quantity) / u.factor * u2.factor) AS weight,
                    SUM(pr.volume * (invoice_type.sign*ail.quantity) / u.factor * u2.factor) AS volume
        """
        return select_str