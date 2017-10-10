# -*- coding: utf-8 -*-
from openerp import api, fields, models
from __builtin__ import str
from openerp.addons.account.models.account_invoice import AccountInvoice
from openerp.exceptions import ValidationError

class ESAccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    tipov = fields.Selection([("gravado","Gravado"),("exento","Exento"),("no_sujeto","No Sujeto")],required=False,
                             string="Tipo de Venta",help="Tipo de Venta que corresponde al articulo",default="gravado")
    
    price_ci = fields.Float(string='Precio con Impuesto', required=False)
        
    price_subtotal_ci = fields.Monetary(string='Subtotal con Impuestos', required=False)

    discount_subtotal = fields.Monetary(string='Descuento producto',
                                        store=True, readonly=True, compute='_compute_discount_product')

    price_subtotal_plus_discount = fields.Monetary(string='Subtotal mas descuento',
                                                   store=True, readonly=True, compute='_compute_discount_product')

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity')
    def _compute_discount_product(self):
        self.discount_subtotal = (self.price_unit * ((self.discount or 0.0) / 100.0)) * self.quantity
        self.price_subtotal_plus_discount = self.price_unit * self.quantity

    @api.constrains("invoice_line_tax_ids")
    def ValidarGravado(self):
        #Debo verificar si tiene documento de origen especificado, de ser asi no ejecuto las validaciones
        #porque en la orden de venta el detalle no tiene un campo de tipo de impuesto
        #Vamos a revisar cada producto y a establecer su valor de tipo de venta dependiendo de si tiene o no impuestos especificados
        for record in self:
            if len(record.invoice_line_tax_ids) > 0:
                record.tipov = "gravado"
            elif len(record.invoice_line_tax_ids) == 0:
                if record.tipov != "no_sujeto" and record.tipov != "exento":
                    record.tipov = "exento"
                
            # Si es gravado y tiene impuestos vacios
            if len(record.invoice_line_tax_ids) <= 0 and record.tipov == "gravado":
                raise ValidationError("El documento contiene articulos gravados sin impuestos especificados")
            elif len(record.invoice_line_tax_ids) > 0 and record.tipov  != "gravado":
                raise ValidationError("El documento contiene articulos exentos o no sujetos con impuestos especificados")
            
    @api.onchange("tipov")
    def VerificarTV(self):
        if self.tipov != False:
            # Si el tipo de venta es exento o no sujeto, se vacia impuesto
            if (self.tipov == "exento" or self.tipov == "no_sujeto"):
                # Vacio el impuesto
                self.invoice_line_tax_ids = False
                self.invoice_line_tax_ids = []
                # Elimina registros existentes en la tabla que relaciona impuestos y detalle que le corresponden al detalle actual
                # Como puede darse el caso de que el registro no tenga id porque no existe, entonces primero verifico que si exista
                # Si el ID es diferente de False es porque existe un registro asociado
                if (self._origin.id != False):
                    self.env.cr.execute("delete from account_invoice_line_tax where invoice_line_id = " + str(self._origin.id))
                    
    @api.onchange("product_id")
    def EstablecerTV(self):
        if self.product_id != False:
            self.tipov = self.product_id.tipov
            self.VerificarTV()
            self.VerificarCP()
        else:
            self.tipov = False
    
    @api.onchange("quantity")
    def VerificarCP(self):
        if self.product_id != False:
            # Cuando cambie el product id debo verificar el tipo de producto para saber si se permiten o no valores decimales
            if self.product_id.type == "service":
                #Si el tipo es servicio entonces solo se admiten cantidades enteras
                self.quantity = self.quantity