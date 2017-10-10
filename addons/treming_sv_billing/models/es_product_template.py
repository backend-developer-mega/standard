# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsProductTemplate(models.Model):
    _inherit = "product.template"
    
    tipov = fields.Selection([("gravado","Gravado"),("exento","Exento"),("no_sujeto","No Sujeto")],required=True,
                            string="Tipo de Venta",help="Tipo de Venta que corresponde al articulo",default="gravado")
