# -*- coding: utf-8 -*-

import datetime
from openerp import api, models, fields
from openerp.exceptions import ValidationError
from gevent.hub import sleep

class ESInvoiceLibrosIva(models.TransientModel):
    _name = 'account.libros.iva'
    
    anyo = fields.Char(required=True, help="Año Fiscal", string="Año",default=datetime.datetime.now().year)
    mes_selection = [
        ('1', 'Enero'),
        ('2', 'Febrero'),
        ('3', 'Marzo'),
        ('4', 'Abril'),
        ('5', 'Mayo'),
        ('6', 'Junio'),
        ('7', 'Julio'),
        ('8', 'Agosto'),
        ('9', 'Septiembre'),
        ('10', 'Octubre'),
        ('11', 'Noviembre'),
        ('12', 'Diciembre'),
        ]

    mes = fields.Selection(mes_selection, string="Mes", help="Mes Fiscal",required=True,default="11")
    
    libro_selection = [
        ('compras', 'Compras'),
        ('ventacf', 'Ventas a Consumidor Final'),
        ('ventac', 'Ventas a Contribuyentes'),
    ]
    
    libro = fields.Selection(libro_selection, string="Libro", help="Tipo de libro a ser generado",required=True,default="compras")
    
    @api.multi
    def generar_libro(self):
        if int(self.anyo) > 9999 or int(self.anyo) < 1900:
            raise ValidationError("El año ingresado es inválido")
        mes = ""
        if len(self.mes) == 1:
            mes = "0" + self.mes
        else:
            mes = self.mes
        fecha1 = self.anyo+"-"+mes+"-01"
        fecha2 = ""
        if self.mes == "12":
            fecha2 = self.anyo+"-"+self.mes+"-31"
        else:
            msig = int(self.mes)+1
            if len(str(msig)) == 1:
                msig = "0" + str(msig)
            fecha2 = self.anyo+"-"+str(msig)+"-01"
        datas = {}
        res = {}
        #Recupero el id del usuario actual
        yo = "1"
        sub1 = sub2 = sub3 = sql = reporte = ""
        if self.libro == "compras":
            sub1 = "COALESCE((select sum(price_subtotal) from account_invoice_line ail where ail.invoice_id = ai.id and tipov = 'exento'),0)"
            sub2 = "COALESCE((select sum(price_subtotal) from account_invoice_line ail where ail.invoice_id = ai.id and tipov = 'gravado'),0)"
            sub3 = "COALESCE((select sum(price_subtotal) from account_invoice_line ail where ail.invoice_id = ai.id and tipov = 'no_sujeto'),0)" 
            sql = ("select row_number() over (order by ai.date_invoice nulls last) as rownum, ai.date_invoice, ai.num_comprobante_cf, rp.nrc_sv, "
                   "rp.nit_sv, rp.dui, rp.name, exentas("+yo+",rp.id,ai.id,1) as exentas_locales, "
                   "exentas("+yo+",rp.id,ai.id,2) as exentas_importaciones, "
                   "gravadas("+yo+",rp.id,ai.id,1) as gravadas_locales, gravadas("+yo+",rp.id,ai.id,2) as gravadas_importaciones, "
                   "imp_fiscal(ai.id) as imp_fiscal, iva("+yo+",ai.partner_id,ai.id,1) as retenido, iva("+yo+",ai.partner_id,ai.id,2) as percibido, "
                   "(("+sub1+") + ("+sub2+") - iva("+yo+",ai.partner_id,ai.id,1) + iva("+yo+",ai.partner_id,ai.id,2)) as total, ("+sub3+") as no_sujetas from account_invoice ai "
                   "inner join res_partner rp on ai.partner_id = rp.id "
                   "where (ai.type = 'in_invoice' or ai.type = 'in_refund') and ai.date_invoice >= '"+fecha1+"'"
                   " and ai.date_invoice < '"+fecha2+"'" 
                   " order by ai.date_invoice ")
            reporte = "treming_sv_billing.es_report_iva_compras"
        self.env.cr.execute(sql)
        resultado = self.env.cr.fetchall()
        datas["registros"] = resultado
        #Ahora viene la parte del calculo de los totales
        datas["reporte"] = reporte
        return self.env['report'].get_action( [], reporte, data=datas)
