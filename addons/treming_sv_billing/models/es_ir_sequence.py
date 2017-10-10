# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsAccountTax(models.Model):
    _inherit = "ir.sequence"
    
    inicial = fields.Integer(string='Inicial', help ='Correlativo inicial de la secuencia', required=False, default = 0)
    final = fields.Integer(string='Final', help ='Correlativo final de la secuencia', required=False, default = 0)
    
    @api.constrains("inicial", "final", "number_increment", "number_next", "padding")
    def ValidarIF(self):
        for record in self:
            if int(record.number_increment) < 0 or int(record.number_next) < 0 or int(record.padding) < 0:
                    raise ValidationError("La longitud de la secuencia, el incremento y el correlativo actual deben ser números positivos")
                
            if record.inicial != 0 or record.final != 0:
                if int(record.final) < 0 or int(record.inicial) < 0:
                    raise ValidationError("Los correlativos inicial y final deben ser números positivos")
                if int(record.final) <= int(record.inicial):
                    raise ValidationError("El correlativo final debe ser mayor al inicial")
                
                corr = record.number_next
                if corr < int(record.inicial):
                    raise ValidationError("El valor de correlativo debe ser igual o mayor al correlativo inicial de la secuencia")
            
                if corr > int(record.final):
                    raise ValidationError("El valor de correlativo debe ser igual o menor al correlativo final de la secuencia")
