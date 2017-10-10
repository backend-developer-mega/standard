# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsHrLevelAcademic(models.Model):
    _name = "hr.levelacademic"
    
    code = fields.Integer(string ='Codigo: ')
    name = fields.Char(string = 'Nombre: ')
    
