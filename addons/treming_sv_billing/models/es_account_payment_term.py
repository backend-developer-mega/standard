# -*- coding: utf-8 -*-
from openerp import models, fields, api

class ESAccountPaymentTerm(models.Model):
    _inherit = "account.payment.term"
    
    dias = fields.Integer(string="Dias",help="Número de dias disponibles para pagar",required=True,default=0)
