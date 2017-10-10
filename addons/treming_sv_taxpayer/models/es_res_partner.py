# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.exceptions import Warning
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp
import re
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT as DF

class ESRestPartner(models.Model):
    _inherit = 'res.partner'

    razon_social = fields.Char(help="Razon Social")
    dui = fields.Char(help="Documento Único de Identidad")
    pasaporte = fields.Char(help="Pasaporte")
    razon_social = fields.Char(help="Razon Social")
    giro = fields.Text(help="Giro")
    nit_sv = fields.Char(help="Número de Identificación Tributaria")
    nrc_sv = fields.Char(help="Número de Registro de Contribuyente")
    street = fields.Text()
    total_invoice = fields.Float(digits=(12, 2),required=False,readonly=True)
    total_invoicex = fields.Float(digits=(12, 2),required=False,string="Total de Facturas", compute='totalex', store=False)

    # Esto se hace para que el valor que este seleccionado por defecto sea individual y no compañia
    @api.model
    def _get_default_value(self):
        return False

    # Defino validacion de formato para NIT, NRC y Email
    @api.constrains("email")
    def ValidarEmail(self):
        for record in self:
            # Si Email es no vacio, entonces
                if record.email != False:
                    print str("")
#                     if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", record.email) != None:
#                         return True
#                     else:
#                         raise ValidationError("El Email ingresado tiene un formato inválido")

    @api.constrains("nit_sv")
    def ValidarNIT(self):
        for record in self:
            # Si NIT es no vacio, entonces
            if record.nit_sv != False:
                if re.match("^\d{4}-\d{6}-\d{3}-\d{1}$", record.nit_sv) != None:
                    return True
                else:
                    raise ValidationError("El NIT ingresado tiene un formato inválido")
                
    @api.constrains("dui")
    def ValidarDUI(self):
        for record in self:
            # Si DUI es no vacio, entonces
            if record.dui != False:
                if re.match("^\d{8}-\d{1}$", record.dui) != None:
                    return True
                else:
                    raise ValidationError("El DUI ingresado tiene un formato inválido")

    #Defino validacion para que razon social sea un campo obligatorio cuando se este guardando una empresa
    @api.constrains("razon_social")
    def ValidarRSocial(self):
        for record in self:
            # Si es una compañia la razon social no puede quedar vacia
            if record.razon_social == False and record.is_company == True:
                raise ValidationError("La razón social es obligatoria")

    @api.onchange('giro', 'razon_social', 'nit_sv', 'nrc_sv')  # El metodo onchage nos permite desencadenar una serie de instrucciones cuando los campos que ha sido pasado por paremetros son modificados en la vista.
    def _check_change(self):
        try:
            if self.name == "" + str(self.name):  # Validamos que las actulizaciones solo se realicen cuando se hace modificaciones a los datos de la compañia principal.
                model = self.env['res.company']  # Indicamos el modelo, que tiene los campos que necesitamos actulizar.
                domain = [('name', '=', '' + str(self.name))]  # Domain se utiliza para filtar los registro que tiene la tabla de res_partner, de manera que solo obtengamos un solo registro.
                ids = model.search(self.env.cr, self.env.uid, domain, context=self.env.context)  # Obtenemos los ids de los objetos creados y cargados en memoria actualmente por Odoo, del formulario que se esta visualizando en tiempo real, para utilizarlos posteriormente.

                # Actualizar el giro.
                valor = {'giro': '' + str(self.giro)}  # Indicamos la columna de la tabla y el nuevo valor que tendra.
                model.write(self.env.cr, self.env.uid, ids, valor, context=self.env.context)  # Ejecutamos el update.

                # Actualizar el razon_social.
                valor = {'razon_social': '' + str(self.razon_social)}
                model.write(self.env.cr, self.env.uid, ids, valor, context=self.env.context)

                # Actualizar el NIT.
                valor = {'nit_c': '' + str(self.nit_sv)}
                model.write(self.env.cr, self.env.uid, ids, valor, context=self.env.context)

                # Actualizar el NRC.
                valor = {'company_registry': '' + str(self.nrc_sv)}
                model.write(self.env.cr, self.env.uid, ids, valor, context=self.env.context)
        except:
            print str("Manejando excepcion")
            
    @api.multi
    def totalex(self):
        for objeto in self:
            sql = "select SUM(amount_total_signed) from account_invoice where partner_id = " + str(objeto.id)
            objeto.env.cr.execute(sql)
            resultado = objeto.env.cr.fetchone()
            try:
                valor = round(resultado[0],2)
            except TypeError:
                valor = 0.00
            objeto.total_invoicex = valor
            objeto.total_invoice = valor
            objeto.write({'total_invoice':valor})

    @api.depends('total_invoicex')  # El metodo onchage nos permite desencadenar una serie de instrucciones cuando los campos que ha sido pasado por paremetros son modificados en la vista.
    def actoin(self):
        self.total_invoice = self.total_invoicex
