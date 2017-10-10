# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsHrLanguages(models.Model):
    _name = "hr.languages"
    
    #level idioma
    #levelLanguages = [('0','Basico'),('1','Intermedio'),('2','Avanzado')]
    name = fields.Char(string = 'Nombre: ')
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
    #selectLevel = fields.Selection(levelLanguages,string="Nivel", default=levelLanguages[0][0])
    
    
