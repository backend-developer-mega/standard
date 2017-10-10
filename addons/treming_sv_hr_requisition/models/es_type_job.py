# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsHrTypeJob(models.Model):
    _name = "hr.typejob"
    
    code = fields.Integer(string ='Codigo: ')
    name = fields.Char(string = 'Nombre: ')
    
