# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class HrTagCareer(models.Model):

    _name = "hr.tagcareer"
    _description = "Carreras Universitarias"

    name = fields.Char('Name')
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
    
