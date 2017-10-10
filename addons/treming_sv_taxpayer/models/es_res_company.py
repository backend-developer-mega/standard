# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.exceptions import Warning
from openerp.tools.translate import _
from openerp.exceptions import ValidationError

class ESRestCompany(models.Model):
    _inherit = 'res.company'

    razon_social = fields.Char(help="Razon Social")
    giro = fields.Text(help="Giro")
    nit_c = fields.Char(help="Número de Identificación Tributaria")
    msj_facturas = fields.Text(help="Mensaje General")
    tipo_imp = fields.Selection([("papel", "Papel"), ("pantalla", "Pantalla")], string="Modalidad de Impresión", 
        help=" * 'Papel' mandara el documento a la impresora especificada en el parametro de sistema: impresora.\n"
             " * 'Pantalla' muestra el documento en pantalla como un archivo PDF.\n"
             , required=True, default = 'pantalla')
    
    #Defino validacion para que razon social sea un campo obligatorio cuando se este guardando una empresa
    @api.constrains("razon_social")
    def ValidarRSocial(self):
        for record in self:
            #Si es una compañia la razon social no puede quedar vacia
            if record.razon_social == False:
                raise ValidationError("La razón social es obligatoria")

    @api.onchange('giro','razon_social','company_registry','nit_c') # El metodo onchage nos permite desencadenar una serie de instrucciones cuando los campos que ha sido pasado por paremetros son modificados en la vista.
    def _check_change(self):
            model = self.env['res.partner']   #Indicamos el modelo, que tiene los campos que necesitamos actulizar.
            domain = [('name','=',''+str(self.name))] #Domain se utiliza para filtar los registro que tiene la tabla de res_partner, de manera que solo obtengamos un solo registro.
            ids = model.search(domain) #Obtenemos los ids de los objetos creados y cargados en memoria actualmente por Odoo, del formulario que se esta visualizando en tiempo real, para utilizarlos posteriormente.
            #Actualizar el giro.

            valor = {'giro': self.giro}  #Indicamos la columna de la tabla y el nuevo valor que tendra.
            model.write(valor) #Ejecutamos el update.

            #Actualizar el razon_social.
            valor = {'razon_social': self.razon_social}
            model.write(valor)

            #Actualizar el NIT.
            valor = {'nit_sv': self.nit_c}
            model.write(valor)

            #Actualizar el NRC.
            valor = {'nrc_sv': self.company_registry}
            model.write(valor)
