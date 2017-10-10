# -*- coding: utf-8 -*-

from openerp import api, models, fields
from openerp.exceptions import ValidationError

class ESInvoiceAnular(models.TransientModel):
    _name = 'esinvoice.anular'
    
    justificacion = fields.Text(string="Justificación",help="Indique la razón por la cual el documento esta siendo anulado")
    
    def anular_factura(self):
        #Obtener el ID de la factura actual
        if self.justificacion == False:
            raise ValidationError("Debe especificar la razón")        
        domain = [('id', '=', self.env.context['active_id'])]
        doc = self.env['account.invoice'].search(domain)
        doc.write({"ranulada":self.justificacion,"state":"cancel"})
        #Se anulan todos los documentos que tengan como origen a este que esta siendo anulado
        domain = [('refund_invoice_id', '=', self.env.context['active_id'])]
        fact = self.env['account.invoice'].search(domain)
        zero_val = 0.0
        for doc in fact:
            doc.write({"ranulada":self.justificacion,"state":"cancel", "residual": zero_val, "residual_signed": zero_val, "residual_company_signed": zero_val})
