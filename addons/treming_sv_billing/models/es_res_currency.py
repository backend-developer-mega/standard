# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsAccountTax(models.Model):
    _inherit = "res.currency"
    
    description_currency = fields.Char(string="Descripción de la Moneda: ")