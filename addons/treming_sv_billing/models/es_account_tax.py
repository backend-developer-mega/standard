# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsAccountTax(models.Model):
    _inherit = "account.tax"
    
    primary_tax = fields.Boolean(index=True, default=False, string='Impuesto Primario')  #Campo para espesificar si este impuesto esta al nivel primario como es el caso del IVA
    