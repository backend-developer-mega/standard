# -*- coding: utf-8 -*-
from openerp import api, fields, models

class ESTiposDocumentos(models.Model):
    _name = "tipos.documentos"
    _rec_name = "nombre"
    
    nombre = fields.Char(required=True,string="Nombre",help="Nombre del Tipo de Documento")
    descripcion = fields.Text(required=True,string="Descripción",help="Descripción del Tipo de Documento")
    activo = fields.Boolean(required=True,string="Activo",help="Establece si el documento esta disponible para su uso",default=False)
    secuencia = fields.Many2one(required=False,string="Secuencia",comodel_name='ir.sequence', delegate=True)
    reporte = fields.Many2one(required=False,string="Reporte",comodel_name='ir.actions.report.xml', delegate=True)
    plantilla = fields.Many2one(required=False,string="Plantilla de Correo",comodel_name='mail.template', delegate=True)
    mostrarf = fields.Boolean(required=True,string="Mostrar en Facturación",help="Establece si el documento se mostrara en el menú de tipo de documento en facturación",default=False)
    tipo = fields.Selection([('factura', 'Factura'),('debito', 'Débito'),('credito', 'Crédito')],required=True)
    copias = fields.Integer(string="Copias a Imprimir", help="Es el número de copias que se imprime cuando el documento es enviado a la impresora", required=True, default=3)
