# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsHrPriority(models.Model):
    _name = "hr.priority"
    
    code = fields.Integer(string ='Codigo: ')
    name = fields.Char(string = 'Nombre: ')
    
