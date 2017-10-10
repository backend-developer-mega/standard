# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsAccountTax(models.Model):
    _inherit = "account.fiscal.position"
    
    gran_contribuyente = fields.Boolean(index=True, default=False, string='Gran Contribuyente: ') 
    quantity_limit = fields.Float(digits=(12, 2),string="Limite")