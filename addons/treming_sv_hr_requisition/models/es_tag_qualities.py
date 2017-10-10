# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class HrTagQualities(models.Model):

    _name = "hr.tagqualities"
    _description = "Cualidades del candidato"

    name = fields.Char('Name')
    color = fields.Integer('Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]
    
