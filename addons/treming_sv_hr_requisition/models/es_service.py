# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsHrService(models.Model):
    _name = "hr.service"
    
    code = fields.Integer(string ='Codigo: ')
    name = fields.Char(string = 'Nombre: ')
    
