# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from openerp import api, fields, models, _
from algoritmo import to_word
import datetime as dt
import logging, re, time, cups, string, random, json
from odoo.tools import float_is_zero

_logger = logging.getLogger(__name__)

class ESAccountInvoice(models.Model):
    _inherit = "account.invoice"

    correlativo = fields.Char(required=False, string="N° de Documento", help="N° del documento fiscal")
    number = fields.Char(related='move_id.name', store=True, readonly=True, copy=False, string="Referencia")

    tipon = fields.Selection([("credito", "Crédito"), ("debito", "Débito")], string="Tipo de Nota", help="Tipo de Nota Rectificativa", required=False)

    entregado_por = fields.Char(string="Entregado por", help="Nombre del empleado quién entrega el documento fiscal")
    entpor_doc = fields.Char(string="DUI o NIT", help="N° de documento del empleado quién entrega el documento fiscal")
    recibido_por = fields.Char(string="Recibido por", help="Nombre del cliente quién recibe el documento fiscal")
    recpor_doc = fields.Char(string="DUI o NIT", help="N° de documento del cliente quién recibe el documento fiscal")
    third_parties = fields.Char(help="Cuenta de Terceros.")
    ranulada = fields.Text(string="Justificación", help="Indique la razón por la cual el documento esta siendo anulado")

    num_comprobante_cf = fields.Char(string="N° de Documento", help="Número de Documento")
    num_nota_credito = fields.Char(string="N° de Documento", help="N° de la Nota de Crédito o Débito")

    tipo_doc = fields.Many2one(required=False, string="Tipo de Documento", help="Tipo de documento emitido",
                               comodel_name='tipos.documentos', readonly=True, domain="[('mostrarf', '=', True)]")

    monto_atrasado = fields.Monetary(string='Total Atrasado',
                                     store=False, readonly=True, compute='_calcular_deudas')

    monto_total_adeudado = fields.Monetary(string='Total Adeudado',
                                           store=False, readonly=True, compute='_calcular_deudas')

    monto_gravado = fields.Monetary(string='Total Gravado',
                                    store=True, readonly=True, compute='_calcular_montos')

    monto_exento = fields.Monetary(string='Total Exento',
                                   store=True, readonly=True, compute='_calcular_montos')
    monto_no_sujeto = fields.Monetary(string='Total No Sujeto',
                                      store=True, readonly=True, compute='_calcular_montos')
    en_letras = fields.Text(string='Son: ', store=False, readonly=True, compute='_calcular_montos')
    en_letras_bruto = fields.Text(string='Son: ', store=False, readonly=True, compute='_calcular_montos')
    num_docf = fields.Char(string='Número', store=False, readonly=True, compute='generar_numero')

    date_invoice = fields.Date(string='Invoice Date',
                               readonly=True, states={'draft': [('readonly', False)]}, index=True,
                               help="Keep empty to use the current date", copy=False, default=time.strftime('%Y-%m-%d'))

    origin_doc_CCF = fields.Char(string='orginCCF',
                                 store=True, readonly=True, compute='_calcular_montos')
    subtotal = fields.Monetary(string='Subtotal',
                               store=True, readonly=True, compute='_calcular_montos')

    empleados_ids = fields.Many2many("hr.employee", string="Outsource", required=False, help="Listado de empleados asociados a la factura")
    residual = fields.Monetary(string='Importe Adeudado', compute='importe_adeudado', store=True, help="Importe adeudado")
    residual_signed = fields.Monetary(string='Amount Due in Invoice Currency', currency_field='currency_id',
                                      compute='importe_adeudado', store=True, help="Remaining amount due in the currency of the invoice.")
    residual_company_signed = fields.Monetary(string='Amount Due in Company Currency', currency_field='company_currency_id',
                                              compute='importe_adeudado', store=True, help="Remaining amount due in the currency of the company.")

    num_comprobante_cfx = fields.Char(help="Numero CCF", compute='_get_num_ccf', default="0", readonly=False, store=True)  # La vista desencadena esta campo calculado.
    numfp = fields.Char(string='Número', store=False, readonly=True, compute='_rep_num')

    iva = fields.Monetary(string='IVA', store=True, readonly=True, compute='compute_new_fields')
    ret_per = fields.Monetary(string='Retenido/Percibido', store=True, readonly=True, compute='compute_new_fields')
    new_subtotal = fields.Monetary(string='Monto con IVA', store=True, readonly=True, compute='compute_new_fields')

    #Cuando cambien los impuestos, como uno de esos impuestos puede ser el iva, debo de actualizar su valor y el de los demas campos que estoy agregando
    @api.depends("tax_line_ids")
    def compute_new_fields(self):
        sale_iva_tax_id = self.env.ref("treming_sv_billing.iva_venta").id
        purchase_iva_tax_id = self.env.ref("treming_sv_billing.iva_compra").id

        sales_retention_tax_id = self.env.ref("treming_sv_billing.iva_retenido_venta_gc").id
        sales_perception_tax_id = self.env.ref("treming_sv_billing.iva_percibido_venta_pc").id

        purchase_retention_tax_id = self.env.ref("treming_sv_billing.iva_retenido_compra_pc").id
        purchase_perception_tax_id = self.env.ref("treming_sv_billing.iva_percibido_compra_gc").id

        for record in self:
            for tax in record.tax_line_ids:
                if tax.tax_id.id in [sale_iva_tax_id, purchase_iva_tax_id]:
                    record.iva = tax.amount
                elif tax.tax_id.id in [sales_retention_tax_id, sales_perception_tax_id, purchase_retention_tax_id, purchase_perception_tax_id]:
                    record.ret_per = tax.amount

            record.new_subtotal = record.amount_untaxed + record.iva

    def _rep_num(self):
        for record in self:
            if record.num_nota_credito != False:
                record.numfp = record.num_nota_credito
            else:
                record.numfp = record.num_comprobante_cf
    try:
        @api.one
        @api.depends('num_comprobante_cfx', 'num_comprobante_cf')  # Indicamos que la variable que va utilizar la funcion posteriormente.
        @api.model
        def _get_num_ccf(self):
            if self.type == "in_refund":
                try:  # Manejamos cualquier tipo de excepcion que se presente, al ejecutar la siguiente sentencia.
                    sql = "update account_invoice SET num_comprobante_cf = (select b.num_comprobante_cf FROM account_invoice a INNER JOIN account_invoice b ON (b.move_name = a.origin) where a.id='" + str(self.id) + "') where id='" + str(self.id) + "';"
                    self.env.cr.execute(sql)
                except:
                    print str(".")
            else:
                self.num_comprobante_cfx = ''

        # Defino este metodo para validar que la cadena pasada como parametro solo contenga numeros
        @api.constrains("num_comprobante_cf")
        def ValidarNum_comprobante_cf(self):
            for record in self:
                # Si num_comprobante_cf es no vacio, entonces
                if record.num_comprobante_cf != False:
                    if re.match("^\w+$", record.num_comprobante_cf) != None:
                        return True
                    else:
                        raise ValidationError("El Número de Documento ingresado tiene un formato inválido")
    except:
        print str(".")

        origin_doc_CCF = fields.Char(string='orginCCF',
                                     store=True, readonly=True, compute='_calcular_montos')

    @api.one
    @api.depends("amount_total")
    def _calcular_montos(self):
        # _logger.info("--------------> CALCULANDO MONTOS<----------------------");
        # INICIALIZAMOS ACUMULADORES EN 0

        self.monto_exento = 0;
        self.monto_gravado = 0;
        self.monto_no_sujeto = 0;
        self.origin_doc_CCF = ''

        sql = ""
        if self.tipo_doc.nombre == "Consumidor Final":
            sql = ("select price_unit,quantity,price_subtotal_ci, tipov from account_invoice_line where invoice_id='" + str(self.id) + "';")
        else:
            sql = ("select price_unit,quantity,price_subtotal, tipov from account_invoice_line where invoice_id='" + str(self.id) + "';")
        # SQL QUERY QUE BUSCA LOS VALORES GRAVADOS, EXENTOS Y NO SUJETOS DE LA FACTURA

        sqlx = ("select account_invoice_line .price_unit, account_invoice_line.quantity, account_invoice_line.price_subtotal,"
                "account_invoice_line.tipov, account_invoice_line_tax.tax_id, account_tax.amount_type, account_tax.amount, account_tax.primary_tax from "
                "account_invoice_line  inner join account_invoice_line_tax on account_invoice_line_tax.invoice_line_id = account_invoice_line.id inner join "
                " account_tax on account_tax.id  =  account_invoice_line_tax.tax_id where account_invoice_line.invoice_id = " + str(self.id) + " and account_invoice_line.tipov = 'gravado' union all "
                                                                                                                                               "select account_invoice_line .price_unit, account_invoice_line.quantity, account_invoice_line.price_subtotal, account_invoice_line.tipov,  0,' ',0 , TRUE "
                                                                                                                                               "from account_invoice_line  "
                                                                                                                                               "where account_invoice_line.invoice_id = " + str(self.id) + " and account_invoice_line.tipov = 'exento' "
                                                                                                                                                                                                           "union all "
                                                                                                                                                                                                           " select account_invoice_line .price_unit, account_invoice_line.quantity, account_invoice_line.price_subtotal, account_invoice_line.tipov,  0,' ',0 , TRUE "
                                                                                                                                                                                                           "from account_invoice_line   "
                                                                                                                                                                                                           "where account_invoice_line.invoice_id = " + str(self.id) + " and account_invoice_line.tipov = 'no_sujeto' ")

        sql2 = ("select correlativo,prefijo from account_invoice where move_name='" + str(self.origin) + "'")
        # RECORREMOS LA LISTA DEVUELTA EN LA EJECUCIÓN DEL SQL
        # EJECUTAMOS SQL SQUERY
        self.env.cr.execute(sql)
        try:
            for item in self.env.cr.fetchall():
                if item[3] == 'gravado':  # SI ES GRAVADO SUMAMOS EL VALOR DEL PRODUCTO AL ACUMULADOR CORRESPONDIENTE.
                    self.monto_gravado = self.monto_gravado + item[2]
                if item[3] == 'exento':
                    self.monto_exento = self.monto_exento + item[2]
                if item[3] == 'no_sujeto':
                    self.monto_no_sujeto = self.monto_no_sujeto + item[2]
        except Exception, e:
            print (str(e))
            # _logger.info(str(e));

        # ##CALCULO DEL SUBTOTAL
        tax_primarios = 0
        tax_secundarios = 0
        self.subtotal = 0
        # EJECUTAMOS SQL SQUERY
        self.env.cr.execute(sqlx)
        try:
            # RECORREMOS LA LISTA DEVUELTA EN LA EJECUCIÓN DEL SQLX
            for item  in self.env.cr.fetchall():
                print str(item[7])
                if str(item[7]) == 'True':  # SI ES TRUE SUMAMOS EL VALOR DEL IMPUESTO AL ACUMULADOR CORRESPONDIENTE.
                    tax_primarios = tax_primarios + item[2] * (item[6] / 100)
                if str(item[7]) == 'False':
                    tax_secundarios = tax_secundarios + item[2] * (item[6] / 100)
        except Exception, e:
            print (str(e))
            # _logger.info(str(e));
        # El subtotal lo construimos con la sumatoria del valor del monto_grabado mas los impuestos primarios.

        self.subtotal = round(round(self.monto_gravado, 2) + round(tax_primarios, 2), 2)

        self.en_letras = to_word(int(self.amount_total))
        #centavos = int(str(self.amount_total).split('.')[1][:2])
        centavos = int(round((self.amount_total % 1)*100,2))
        # centavos = int((round(self.amount_total, 2) - int(round(self.amount_total, 2))) * 100)
        if centavos > 0:
            self.en_letras = self.en_letras.upper() + " CON " + str(int(centavos)) + "/100"
        else:
            self.en_letras = self.en_letras.upper() + " CON 00/100"

        # CONVERSION A LETRA EL TOTAL SIN IMPUESTO
        self.en_letras_bruto = to_word(int(self.amount_untaxed))
        # centavos = int((round(self.amount_untaxed, 2) - int(round(self.amount_untaxed, 2))) * 100)
        #centavos = int(str(self.amount_untaxed).split('.')[1][:2])
        centavos = int(round((self.amount_untaxed % 1)*100,2))
        if centavos > 0:
            self.en_letras_bruto = self.en_letras_bruto.upper() + " CON " + str(int(centavos)) + "/100"
        else:
            self.en_letras_bruto = self.en_letras_bruto.upper() + " CON 00/100"

        # EJECUTAMOS SQL SQUERY
        self.env.cr.execute(sql2)
        for item  in self.env.cr.fetchall():
            self.origin_doc_CCF += str(item[1]) + str(item[0])

    # Defino el estado de anulada
    STATE_SELECTION = [
        ('draft', 'Borrador'),
        ('open', 'Abrir'),
        ('paid', 'Pago'),
        ('cancel', 'Anulada')]

    state = fields.Selection(STATE_SELECTION, string="Estado", help="Aqui va la ayuda")

    # Defino estos tipos para que la funcion calculada
    amount_untaxed = fields.Float(digits=(12, 2), string="Monto no tributado", compute='actax', store=True)
    # Campo para contener la suma de impuestos primarios mas el monto no tributado
    amount_taxed_pri = fields.Float(digits=(12, 2), string="Subtotal", compute='actax', store=True)
    amount_tax = fields.Float(digits=(12, 2), string="Impuestos", compute='actax', store=True)
    # El total de venta es el subtotal mas los montos secundarios
    amount_total = fields.Float(digits=(12, 2), string="Total", compute='actax', store=True)

    fvencimiento = fields.Date(string="Fecha de Vencimiento", help="Fecha de vencimiento del documento pendiente de pago", compute='CalcularFV', store=True)
    ps_incio = fields.Date(string="Inicio de Servicio", help="Fecha de inicio del periodo de servicio")
    ps_fin = fields.Date(string="Fin de Servicio", help="Fecha de finalización del periodo de servicio")

    prefijo = fields.Char(required=False, help="Prefijo de documento", default="GEN", compute='prefix', store=True)

    # Defino una constraint para evitar que dos documentos tenga el mismo prefijo y correlativo
    # _sql_constraints = [('unique_prefijo_corr', 'unique(prefijo,correlativo)', 'Dos documentos no pueden tener el mismo prefijo y correlativo\nPor favor especifique otro correlativo')]

    def copy(self, default):
        if self.state == 'cancel':
            raise ValidationError("No se puede copiar un documento anulado")
        else:
            if self.num_comprobante_cf == False:
                num_cero = self.tipo_doc.secuencia.padding - len(str(self.tipo_doc.secuencia.number_next))
                ceros = ""
                for i in range(0, num_cero):
                    ceros += "0"
                valor = ceros + str(self.tipo_doc.secuencia.number_next)
                default.update({
                    'correlativo': valor, 'date_invoice': self.date_invoice
                })
            return super(ESAccountInvoice, self).copy(default)

    def cancel_custom(self):
        data_obj = self.env['ir.model.data']
        form_data_id = data_obj._get_id('treming_sv_billing', 'es_anular_confirmacion_view')
        form_view_id = False
        if form_data_id:
            form_view_id = data_obj.browse(form_data_id).res_id
        return{'name':'¿Esta seguro de que desea anular el documento?', 'view_type':'form', 'view_mode':'form', 'view_id':False, 'views':[(form_view_id, 'form'), ], 'res_model':'esinvoice.anular', 'type':'ir.actions.act_window', 'target':'new'}

    def id_generator(self, size=8, chars=string.ascii_uppercase + string.digits):
        return ''.join(random.choice(chars) for _ in range(size))

    def generar_numero(self):
        for record in self:
            if record.prefijo == False:
                record.prefijo = "PREFIJO"
            if record.correlativo == False:
                record.correlativo = "000"
            record.num_docf = record.prefijo + record.correlativo

    # Defino este metodo para la generación de reportes
    @api.multi
    def invoice_print_custom(self):
        reporte = self.tipo_doc.reporte.report_name
        self.ensure_one()
        self.sent = True
        return self.env['report'].get_action(self, reporte)

    def invoice_print_send(self):
        # Recupero el tipo de impresión asociado a la compañía
        timp = self.env.user.company_id.tipo_imp
        reporte = self.tipo_doc.reporte.report_name
        self.ensure_one()
        self.sent = True
        if timp == "pantalla":
            return {
                'type' : 'ir.actions.act_url',
                'url': '/web/binary/imprimir?nombre='+reporte+'&registro='+str(self.id),
                'target': 'new',
            }
        elif timp == "papel":
            # Se establece el id del registro a partir del cual se genera el reporte
            docids = []
            docids.append(self.id)
            archivo = self.env['report'].get_pdf(docids, reporte)
            # Se genera una cadena aleatoria de mayusculas y numeros para que sirva como nombre del archivo
            nombre = self.id_generator()
            # Para poder enviarlo a la impresora primero debe guardarlo en una ubicación X
            # Que se especifica por medio de un parametro
            obj = self.env["ir.config_parameter"].search([['key', '=', 'direpo']])[0]
            destino = obj.value + nombre + '.pdf'
            # Creo el archivo
            file_ = open(destino, 'w+')
            # Escribo la información del reportes
            file_.write(archivo)
            # Cierro el archivo
            file_.close()
            # Para imprimir
            conn = cups.Connection()
            printers = conn.getPrinters()
            # La documentacion de CUPS señala que la impresora establecida por defecto ocupa la primera posición: [0]
            # Pero en mi caso particular la impresora establecida como predeterminada aparece con el indice [1]
            # Recupera el nombre de la impresora de un parametro llamado impresora
            objeto = self.env["ir.config_parameter"].search([['key', '=', 'impresora']])[0]
            printer_name = objeto.value
            # Se envia a imprimir
            conn.printFile(printer_name, destino, "Documento Fiscal", {'copies':str(self.tipo_doc.copias)})

    # Para recuperar el prefijo y el correlativo desde la base de datos
    @api.one
    @api.depends("tipo_doc")
    def prefix(self):
        # Recupero el prefijo dependiendo del tipo de documento
        if self.num_comprobante_cf == False:
            if self.tipo_doc != False:
                # Para el elemento seleccionado recupero su prefijo
                if self.tipo_doc.secuencia == False:
                    raise ValidationError("El tipo de documento seleccionado no tiene una secuencia asignada")
                self.prefijo = self.tipo_doc.secuencia.prefix
                # Dependiendo de la longitud asi deben ser los ceros
                num_cero = self.tipo_doc.secuencia.padding - len(str(self.tipo_doc.secuencia.number_next))
                ceros = ""
                for i in range(0, num_cero):
                    ceros += "0"
                self.correlativo = ceros + str(self.tipo_doc.secuencia.number_next)

    @api.constrains("ps_incio", "ps_fin")
    def ValidarPS(self):
        for record in self:
            if record.ps_incio != False and record.ps_fin != False:
                # La fecha de fin no puede ser anterior a la fecha de incio
                a = dt.datetime.strptime(record.ps_incio, "%Y-%m-%d")
                b = dt.datetime.strptime(record.ps_fin, "%Y-%m-%d")
                if a > b:
                    raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin del periodo de servicio")

    # Cuando cambie la fecha de la factura o el termino de pago
    @api.depends("date_invoice", "payment_term_id")
    def CalcularFV(self):
        for record in self:
            if record.payment_term_id.id != False:
                if record.payment_term_id.id != 1:
                    # Verifico si la fecha de la factura esta vacia
                    if record.date_invoice != False:
                        # A la fecha de la factura le sumo el numero de dias
                        a = dt.datetime.strptime(record.date_invoice, "%Y-%m-%d")
                        b = a + dt.timedelta(days=record.payment_term_id.dias)
                        record.fvencimiento = b.strftime('%Y-%m-%d')

    @api.constrains("correlativo")
    def ValidarND(self):
        for record in self:
            if re.match("^\d{1,12}$", str(record.correlativo)) != None:
                return True
            else:
                raise ValidationError("El N° de Documento debe contener solo números")

    @api.depends("invoice_line_ids")
    @api.onchange("invoice_line_ids")
    def grancontribuyente(self):
        if self.amount_untaxed >= 100:
            retencion = (self.amount_untaxed * 0.01)
            self._compute_amount()
            self.amount_taxed_pri = self.amount_untaxed + retencion

    @api.depends("invoice_line_ids")
    @api.onchange("invoice_line_ids")
    def actax(self):
        impuestos = 0
        listap = []
        # Para cada producto en el detalle
        # Me da la impresion de que mete al registro y a su documento de origen
        cantidad = len(self)
        if cantidad == 1:
            # Si es un solo elemento hago lo siguiente
            for impuesto in self.tax_line_ids:
                sql = "select primary_tax from account_tax where id = " + str(impuesto.tax_id.id)
                self.env.cr.execute(sql)
                resultado = self.env.cr.fetchone()
                if resultado[0] == True:
                    listap.append(impuesto)
            impuestos = sum(line.amount for line in listap)
            # Llamo a la función nativa de Odoo para que calcule los impuestos
            self._compute_amount()
            self.amount_taxed_pri = self.amount_untaxed + impuestos
        elif cantidad > 1:
            for objeto in self:
                for impuesto in objeto.tax_line_ids:
                    sql = "select primary_tax from account_tax where id = " + str(impuesto.tax_id.id)
                    objeto.env.cr.execute(sql)
                    resultado = objeto.env.cr.fetchone()
                    if resultado[0] == True:
                        listap.append(impuesto)
                impuestos = sum(line.amount for line in listap)
                # Llamo a la función nativa de Odoo para que calcule los impuestos
                objeto._compute_amount()
                objeto.amount_taxed_pri = objeto.amount_untaxed + impuestos

    @api.one
    @api.depends("partner_id")
    def _calcular_deudas(self):
        self.monto_atrasado = 0
        self.monto_total_adeudado = 0
        sql = "select sum(amount_total) from account_invoice where fvencimiento < now() and state <> 'paid' and partner_id = " + str(self.partner_id.id)
        # EJECUTAMOS SQL SQUERY
        self.env.cr.execute(sql)
        try:
            for item  in self.env.cr.fetchall():
                self.monto_atrasado = item[0];
        except Exception, e:
            print (str(e));
        if self.monto_atrasado == None:
            self.monto_atrasado = 0
        self.monto_total_adeudado = self.amount_total + self.monto_atrasado

    def corregir_movimientos(self):
        #Los documentos para los cuales debo corregir sus movimientos son las notas de debito y credito
        #antes de hacer todo lo que sigue verifico el tipo del documento, y si no es una factura rectificativa entonces no haga nada
        if self.type not in ["out_invoice", "in_invoice"]:
            doc_origen = self.env["account.invoice"].search([["number", "=", self.origin]])
            #Si es una nota de débito para una factura de cliente va a aumentar el valor, por lo que los movimientos
            #deben tener sus valore de credit y debit como si fuera una venta
            nuevas_lineas = []
            if (doc_origen.type == "out_invoice" and self.tipo_doc.tipo == "debito") or (doc_origen.type == "in_invoice" and self.tipo_doc.tipo == "credito"):
                self.move_id.write({"state":"draft"})
                for linea in self.move_id.line_ids:
                    credito, debito = linea.credit, linea.debit
                    if linea.credit == 0:
                        val_debito = 0.0
                        val_credito = debito
                    elif linea.debit == 0:
                        val_debito = credito
                        val_credito = 0.0
                    nuevas_lineas.append([0,0,{"account_id":linea.account_id.id,"partner_id":linea.partner_id.id,"name":linea.name,
                                               "analytic_account_id":linea.analytic_account_id.id,"amount_currency":linea.amount_currency,
                                               "company_currency_id":linea.company_currency_id.id,"currency_id":linea.currency_id.id,
                                               "debit":val_debito,"credit":val_credito,"date_maturity":linea.date_maturity}])
                self.move_id.write({"line_ids":[[5]]})
                self.move_id.write({"line_ids":nuevas_lineas})
                self.move_id.write({"state":"posted"})
        return True

    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def importe_adeudado(self):
        for record in self:
            #En este caso simplemente lo establezco como reconciliado y con amount_residual 0 para que ya no aparezca y altero la funcion ue calcula
            #el Importe adeudado

            #Tanto las notas de credito como de debito tienen este atributo especificado
            domain = [('refund_invoice_id', '=', record.id)]
            #Ya tengo todas las notas que le corresponden a esta factura, y de esas puedo sacar los movimientos
            notas = record.env['account.invoice'].search(domain)
            #Recupero los movimientos que representan a los pagos
            pagos = record.env['account.move'].search([['ref', '=', record.number]])

            #Recupero los registros de diario que voy a necesitar
            #Los pagos se van registrar siempre en una de estas dos cuentas
            cuenta_banco = record.env['account.journal'].search([['code', '=', "BNK1"]])
            cuenta_efectivo = record.env['account.journal'].search([['code', '=', "CSH1"]])
            list_pago = [cuenta_banco.id, cuenta_efectivo.id]
            #Las notas de credito y debito van a Facturas de cliente y no tienen referencia
            cuenta_fcliente = record.env['account.journal'].search([['code', '=', "INV"]])
            cuenta_fproveedor = record.env['account.journal'].search([['code', '=', "FACTU"]])
            list_nota = [cuenta_fcliente.id, cuenta_fproveedor.id]
            mov_notas = []
            for linea in notas:
                mov_notas.append(linea.move_id.id)
            for linea in pagos:
                mov_notas.append(linea.id)
            #Ahora recupero las lineas de los movimientos que es lo que me interesa
            domain = [('move_id', 'in', mov_notas),('account_id', '=', record.account_id.id), ('partner_id', '=', record.env['res.partner']._find_accounting_partner(record.partner_id).id), ('reconciled', '=', True), ('amount_residual', '=', 0.0)]
            #record.env['account.move.line'].search(domain)
            lineas_mov = record.recuperar_movimientos("conciliados")
            #Para este caso necesito que las notas de debito sumen, las de credito resten al igual que los pagos
            #Se que los pagos si tiene valor de referencia
            importe_adeudado = record.amount_total
            for linea in lineas_mov:
                #Se trata de un pago
                if linea.journal_id.id in list_pago:
                    importe_adeudado-=abs(linea.debit or linea.credit)
                elif linea.journal_id.id in list_nota:
                    #Caso contrario es una nota de credito o debito
                    obj_factura = record.env["account.invoice"].search([["number", "=", linea.move_id.name]])
                    #Si la factura asociada al movimiento es de debito, y la factura actual es de cliente, entonces debito suma
                    #y credito disminuye
                    tipo_fact = obj_factura.tipo_doc.tipo
                    if record.type == "out_invoice":
                        if tipo_fact == "debito":
                            importe_adeudado+=abs(obj_factura.amount_total)
                        if tipo_fact == "credito":
                            importe_adeudado-=abs(obj_factura.amount_total)
                    elif record.type == "in_invoice":
                        if tipo_fact == "debito":
                            importe_adeudado-=abs(obj_factura.amount_total)
                        if tipo_fact == "credito":
                            importe_adeudado+=abs(obj_factura.amount_total)

            record.residual = importe_adeudado
            record.residual_signed = importe_adeudado
            record.residual_company_signed = importe_adeudado
            if importe_adeudado == 0 and record.state != 'draft' and record.amount_total != 0:
                #Si el importe adeudado llega a cero, debo establecer el documento como pagado
                record.write({"state":"paid"})

    @api.depends("payment_ids")
    def update_residual(self):
        print "Se ejecuta el método BLISTO"
        self.importe_adeudado()

    @api.multi
    def assign_outstanding_credit(self, credit_aml_id):
        self.ensure_one()
        credit_aml = self.env['account.move.line'].browse(credit_aml_id)
        obj_nota = self.env["account.invoice"].search([["number","=", credit_aml.move_id.name]])
        if (self.type == "out_invoice" and obj_nota.tipo_doc.tipo == "debito") or (self.type == "in_invoice" and obj_nota.tipo_doc.tipo == "credito"):
            #En este caso simplemente lo establezco como reconciliado y con amount_residual 0 para que ya no aparezca y altero la funcion ue calcula
            #el Importe adeudado
            credit_aml.write({"reconciled": True, "amount_residual":0.0})
            #Por algun motivo para el caso de las notas emitidas para facturas de proveedor no establece el importe adeudado a cero
            #por lo que hago lo siguiente
            self.importe_adeudado()
        else:
            if not credit_aml.currency_id and self.currency_id != self.company_id.currency_id:
                credit_aml.with_context(allow_amount_currency=True).write({
                    'amount_currency': self.company_id.currency_id.with_context(date=credit_aml.date).compute(credit_aml.balance, self.currency_id),
                    'currency_id': self.currency_id.id})
            if credit_aml.payment_id:
                credit_aml.payment_id.write({'invoice_ids': [(4, self.id, None)]})
            self.register_payment(credit_aml)
        #Por algun motivo, el pago ultimo para una factura de proveedor no se registra como reconciliada, asi que para asegurarme de
        #si se establece como reconciliada hago
        obj_nota.write({"residual":0.0,"residual_signed":0.0})

    @api.one
    @api.depends('payment_move_line_ids.amount_residual')
    def _get_payment_info_JSON(self):
        self.payments_widget = json.dumps(False)
        #Recupero todos los registros que esten asociados al movimiento de la factura
        lineas = self.recuperar_movimientos("conciliados")
        info = {'title': _('Aplicado en'), 'outstanding': False, 'content': []}
        currency_id = self.currency_id
        for payment in lineas:
            payment_currency_id = False
            if self.type in ('out_invoice', 'in_refund'):
                amount = sum([p.amount for p in payment.matched_debit_ids if p.debit_move_id in self.move_id.line_ids])
                amount_currency = sum([p.amount_currency for p in payment.matched_debit_ids if p.debit_move_id in self.move_id.line_ids])
                if payment.matched_debit_ids:
                    payment_currency_id = all([p.currency_id == payment.matched_debit_ids[0].currency_id for p in payment.matched_debit_ids]) and payment.matched_debit_ids[0].currency_id or False
            elif self.type in ('in_invoice', 'out_refund'):
                amount = sum([p.amount for p in payment.matched_credit_ids if p.credit_move_id in self.move_id.line_ids])
                amount_currency = sum([p.amount_currency for p in payment.matched_credit_ids if p.credit_move_id in self.move_id.line_ids])
                if payment.matched_credit_ids:
                    payment_currency_id = all([p.currency_id == payment.matched_credit_ids[0].currency_id for p in payment.matched_credit_ids]) and payment.matched_credit_ids[0].currency_id or False
            # get the payment value in invoice currency
            if payment_currency_id and payment_currency_id == self.currency_id:
                amount_to_show = amount_currency
            else:
                amount_to_show = payment.company_id.currency_id.with_context(date=payment.date).compute(amount, self.currency_id)

            payment_ref = payment.move_id.name
            if int(payment.debit) != 0:
                amount_to_show = payment.debit
            else:
                amount_to_show = payment.credit

            if self.type == "out_invoice" and (payment.invoice_id.tipon == "credito" or payment.payment_id.id != False):
                amount_to_show = -abs(amount_to_show)
            elif self.type == "out_invoice" and payment.invoice_id.tipon == "debito":
                amount_to_show = abs(amount_to_show)
            elif self.type == "in_invoice" and (payment.invoice_id.tipon == "debito" or payment.payment_id.id != False):
                amount_to_show = -abs(amount_to_show)
            elif self.type == "in_invoice" and (payment.invoice_id.tipon == "credito"):
                amount_to_show = abs(amount_to_show)

            if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                continue

            if payment.move_id.ref:
                payment_ref += ' (' + payment.move_id.ref + ')'

            info['content'].append({
                'name': payment.name,
                'journal_name': payment.journal_id.name,
                'amount': amount_to_show,
                'currency': currency_id.symbol,
                'digits': [69, currency_id.decimal_places],
                'position': currency_id.position,
                'date': payment.date,
                'payment_id': payment.id,
                'move_id': payment.move_id.id,
                'ref': payment_ref,
            })
        self.payments_widget = json.dumps(info)

    def recuperar_movimientos(self, estado):
        #Recupero todos los movimientos que le corresponde a esta factura
        domain = ['&',('refund_invoice_id', '=', self.id), ('state', '!=', 'cancel')]
        fact = self.env['account.invoice'].search(domain)
        #Ya tengo todas las notas que le corresponden a esta factura, ahora necesito los movimientos
        #Saco todos los number de las facturas recuperadas
        numeros = []
        for obj in fact:
            numeros.append(str(obj.number))
        #Ya con los numeros puede recuperar los movimientos
        domain = [('name', 'in', numeros)]
        mov = self.env['account.move'].search(domain)
        numeros = []
        for obj in mov:
            numeros.append(obj.id)
        #Ahora recupero las lineas que es lo que me interesa
        reconciliado = False
        amount_residual = ('amount_residual', '!=', 0.0)
        domain = [('move_id', 'in', numeros),('account_id', '=', self.account_id.id), ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id), ('reconciled', '=', reconciliado), amount_residual]
        lines = self.env['account.move.line'].search(domain)
        if estado == "conciliados":
            #Me interesan los movimientos tantos de pagos como de notas, que para este punto ya han sido conciliadas
            reconciliado = True
            amount_residual = ('amount_residual', '=', 0)
            domain = [('move_id', 'in', numeros),('account_id', '=', self.account_id.id), ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id), ('reconciled', '=', reconciliado), amount_residual]
            domain_pago = [('ref', '=',self.number),('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id), ('reconciled', '=', reconciliado), amount_residual]
            if self.type == "in_invoice":
                #Si es una factura de proveedor
                referencia = self.reference or self.number
                domain_pago = [('ref', '=',referencia),('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id), ('reconciled', '=', reconciliado), ("balance", ">", 0), amount_residual]
                domain = [('move_id', 'in', numeros),('account_id', '=', self.account_id.id), ('partner_id', '=', self.env['res.partner']._find_accounting_partner(self.partner_id).id), ('reconciled', '=', reconciliado), amount_residual]
            lines_fact = self.env['account.move.line'].search(domain)
            lines_pagos = self.env['account.move.line'].search(domain_pago)
            lines = lines_fact | lines_pagos
        return lines

    @api.one
    def _get_outstanding_info_JSON(self):
        self.outstanding_credits_debits_widget = json.dumps(False)
        if self.state == 'open':
            lines = self.recuperar_movimientos("pendientes")
            type_payment = _('Créditos y débitos pendientes')
            info = {'title': '', 'outstanding': True, 'content': [], 'invoice_id': self.id}
            currency_id = self.currency_id
            if len(lines) != 0:
                for line in lines:
                    # get the outstanding residual value in invoice currency
                    if line.currency_id and line.currency_id == self.currency_id:
                        amount_to_show = abs(line.amount_residual_currency)
                    else:
                        amount_to_show = line.company_id.currency_id.with_context(date=line.date).compute(abs(line.amount_residual), self.currency_id)
                    if float_is_zero(amount_to_show, precision_rounding=self.currency_id.rounding):
                        continue
                    #Dependiendo del tipo voy a recupera uno u otro campo
                    objeto = self.env["account.invoice"].search([['number', '=', line.move_id.name]])[0]
                    jname = ""
                    if objeto.type == "out_refund" or objeto.type == "out_invoice":
                        jname = objeto.num_docf
                    else:
                        jname = objeto.numfp
                    info['content'].append({
                        'journal_name': jname or line.ref,
                        'amount': amount_to_show,
                        'currency': currency_id.symbol,
                        'id': line.id,
                        'position': currency_id.position,
                        'digits': [69, self.currency_id.decimal_places],
                    })
                info['title'] = type_payment
                self.outstanding_credits_debits_widget = json.dumps(info)
                self.has_outstanding = True

    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'partner_id')
    def _compute_amount(self):
        #Verifico si los impuestos no se hallan vacios, porque de estarlo todo lo que sigue es inutil
        #Para el caso de la retención y percepción
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        #Primero verifico quien es y quien no es gran contribuyente
        #Del usuario actual saco la compañia actualmente seleccionada, y verifico si esa compañia es o no gran contribuyente
        if len(self.tax_line_ids) > 0:
            pfcomps = self.env.user.company_id.partner_id.property_account_position_id.name
            pfclis = self.partner_id.property_account_position_id.name
            quitar = []
            ninguno = False
            pfcomp = unicode(pfcomps)
            pfcli = unicode(pfclis)
            parampc = self.env["ir.config_parameter"].search([['key', '=', 'peq_contrib']])[0].value
            paramgc = self.env["ir.config_parameter"].search([['key', '=', 'gra_contrib']])[0].value
            tgc = paramgc
            tpc = parampc
            aplica = False
            if pfcomp == tgc and pfcli == tpc:
                #Entra en efecto el impuesto definido, que va a aumentar el total de la venta
                aplica = True
            elif pfcomp == tpc and pfcli == tgc:
                #Entra en efecto el impuesto definido, que le va a restar al total de la venta
                aplica = True
            else:
                ninguno = True

            #Esto solo aplica si el total sin impuestos es mayor o igual, para hacer la comparación debo recuperar el límite
            limite = self.partner_id.property_account_position_id.quantity_limit
            if aplica:
                if self.amount_untaxed >= limite:
                    #Esto me quiere decir que los impuestos no aplican, los debo quitar
                    ninguno = False
                else:
                    ninguno = True

            #Recupero de los parametros los nombres de los impuestos
            if self.type == "in_invoice" or self.type == "out_invoice":
                val1 = self.env["ir.config_parameter"].search([['key', '=', 'retenido']])[0].value
                val2 = self.env["ir.config_parameter"].search([['key', '=', 'percibido']])[0].value
                quitar.append(val1)
                quitar.append(val2)

            aux = []
            # Si en la factura de origen esta presente con un monto distinto de cero, entonces aqui también se debe calcular
            if self.type == "in_refund" or self.type == "out_refund":
                forigen = self.env["account.invoice"].search([['number','=',self.origin]])[0]
                for impuesto in forigen.tax_line_ids:
                    if impuesto.amount != 0:
                        aux.append(impuesto.name)
                for imp in self.tax_line_ids:
                    if imp.name not in aux:
                        quitar.append(imp.name)
                ninguno = True

            #Esto indica que debo quitar esos impuestos
            if ninguno == True:
                indice = []
                index = 0
                for impuesto in self.tax_line_ids:
                    if impuesto.name in quitar:
                        indice.append(index)
                    index+=1

                for valor in indice:
                    self.tax_line_ids[valor].amount = 0

            if self.tipo_doc.nombre == "Consumidor Final":
                dp = self.env["decimal.precision"].search([["name", "=", "Product Price"]])[0].digits
                #Si es consumidor final se que me da problemas al momento de cuadrar, asi que los impuestos los voy a calcular
                #manualente, para ello primero establezco todos los que esten presentes a 0
                for imp in self.tax_line_ids:
                    imp.amount = 0.0
                for detalle in self.invoice_line_ids:
                    acumulador = 0.0
                    detalle.price_ci = detalle.price_unit * 1.0
                    acumulador = detalle.price_subtotal
                    for impuesto in detalle.invoice_line_tax_ids:
                        #Si el impuesto es un porcentaje entonces lo calculo asi
                        monto_imp = 0.0
                        monto_asum = 0.0
                        #Debo de verificar si el impuesto aplica
                        #Aqui tengo que recupera los nombres de los impouestos de retencion y percepcion
                        if not((impuesto.name == quitar[0] or impuesto.name == quitar[1]) and ninguno == True):
                            if impuesto.amount_type == "percent":
                                val = round((impuesto.amount / 100.0),dp)
                                monto_imp = round(detalle.price_unit * val,dp)
                                monto_asum = round(detalle.price_subtotal * val,dp)
                            #Pero si el impuesto es una cantidad fija entonces solo se la debo sumar al precio
                            elif impuesto.amount_type == "fixed":
                                monto_imp = round(impuesto.amount,dp)
                                monto_asum = round(detalle.quantity * impuesto.amount,dp)
                                #Debo redondear antes de efectuar la multiplicación

                            for imp in self.tax_line_ids:
                                # Si se llaman igual entonces se que debo aplicarlo al general
                                if imp.name == impuesto.name:
                                    imp.amount += monto_asum
                        acumulador+=monto_asum
                        detalle.price_ci += monto_imp
                    nvalor = round(detalle.quantity * detalle.price_ci,dp)
                    detalle.price_subtotal_ci = nvalor
                    # Aplico los impuestos al precio subtotal

        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        if self.currency_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign

    @api.multi
    @api.returns('self')
    def refund(self, date_invoice=None, date=None, description=None, journal_id=None, tipon=None):
        new_invoices = self.browse()
        for invoice in self:
            # create the new invoice
            values = self._prepare_refund(invoice, date_invoice=date_invoice, date=date,
                                          description=description, journal_id=journal_id)
            # Debo establecer el tipo, y recuperar el prefijo e ID
            # Consulto a la BD para hallar el registro que corresponda al tipo de nota
            objtd = self.env["tipos.documentos"].search([["tipo", "=", tipon], ["activo", "=", True]])[0]
            values["tipo_doc"] = objtd.id
            values["tipon"] = tipon
            # Si ese campo esta vacio es porque es una factura de cliente, y de las de cliente si vamos a llevar correlativo
            if invoice.num_comprobante_cf == False:
                # Ahora que ya los recupere entonces establezco los valores
                # Dependiendo de la longitud asi deben ser los ceros
                num_cero = objtd.secuencia.padding - len(str(objtd.secuencia.number_next))
                ceros = ""
                for i in range(0, num_cero):
                    ceros += "0"
                values["correlativo"] = ceros + str(objtd.secuencia.number_next)
                # Defino el valor del resto de campos
                values["ps_incio"] = invoice.ps_incio
                values["ps_fin"] = invoice.ps_fin
                values["third_parties"] = invoice.third_parties
                values["entregado_por"] = invoice.entregado_por
                values["entpor_doc"] = invoice.entpor_doc
                values["recibido_por"] = invoice.recibido_por
                values["recpor_doc"] = invoice.recpor_doc
            else:
                values["reference"] = invoice.reference
                values["date_due"] = invoice.date_due
            refund_invoice = self.create(values)
            invoice_type = {'out_invoice': ('customer invoices refund'),
                            'in_invoice': ('vendor bill refund')}
            message = _("This %s has been created from: <a href=# data-oe-model=account.invoice data-oe-id=%d>%s</a>") % (invoice_type[invoice.type], invoice.id, invoice.number)
            refund_invoice.message_post(body=message)
            new_invoices += refund_invoice
        return new_invoices

    @api.multi
    def invoice_validate(self):
        for invoice in self:
            # refuse to validate a vendor bill/refund if there already exists one with the same reference for the same partner,
            # because it's probably a double encoding of the same bill/refund
            if invoice.type in ('in_invoice', 'in_refund') and invoice.reference:
                if self.search([('type', '=', invoice.type), ('reference', '=', invoice.reference), ('company_id', '=', invoice.company_id.id), ('commercial_partner_id', '=', invoice.commercial_partner_id.id), ('id', '!=', invoice.id)]):
                    # raise UserError(_("Duplicated vendor reference detected. You probably encoded twice the same vendor bill/refund."))
                    print str(".")
        return self.write({'state': 'open'})

    # Actualizo el valor de correlativo
    @api.multi
    def action_invoice_open(self):
        # if self.tipon == "credito":
        #     # Si es una nota de credito o debito su monto no puede ser superior al del documento original
        #     monto = self.refund_invoice_id.residual
        #     if self.amount_total > monto:
        #         raise ValidationError("El total de la nota de crédito no puede ser superior al monto adeudado del crédito fiscal")

        #Si es una factura de cliente o una rectificativa de cliente se deben validar ciertos aspectos
        if self.type == "out_invoice" or self.type == "out_refund":
            corr = 0
            try:
                corr = int(self.correlativo.lstrip("0"))
            except:
                raise ValidationError("El valor de correlativo debe ser un número entero")

            #Si es un entero, verifico que se halle dentro del rango
            #Recupero el inicial y final de la secuencia
            corrini = self.tipo_doc.secuencia.inicial
            corrfin = self.tipo_doc.secuencia.final
            long = self.tipo_doc.secuencia.padding
            if corr < corrini:
                raise ValidationError("El valor de correlativo debe ser igual o mayor al correlativo inicial de la secuencia: " + str(corrini))

            if corr > corrfin:
                raise ValidationError("El valor de correlativo debe ser igual o menor al correlativo final de la secuencia: "  + str(corrfin))

            if len(self.correlativo) != long:
                raise ValidationError("La longitud del correlativo debe ser de " + str(long) + " caracteres")

        # Es una factura rectificativa?
        if self.type in ("out_refund","in_refund"):
            #Si es una factura de proveedor, y es una nota de credito los valores deben ser positivos
            #o si es una factura de cliente y es una nota de debito
            if (self.type == "in_refund" and self.tipon == "credito") or (self.type == "out_refund" and self.tipon == "debito"):
                # Debo actualizar las lineas de factura para que tengan saldos positivos y también el total sin impuestos
                for detalle in self.invoice_line_ids:
                    valor = abs(detalle.price_subtotal_signed)
                    detalle.write({"price_subtotal_signed":valor})
                aus = abs(self.amount_untaxed_signed)
                ats = abs(self.amount_total_signed)
                atcs = abs(self.amount_total_company_signed)
                rcs = abs(self.residual_company_signed)
                rs = abs(self.residual_signed)
                self.write({"amount_untaxed_signed":aus, "amount_total_signed":ats, "amount_total_company_signed":atcs, "residual_company_signed":rcs, "residual_signed":rs})

        to_open_invoices = self.filtered(lambda inv: inv.state != 'open')
        if to_open_invoices.filtered(lambda inv: inv.state not in ['proforma2', 'draft']):
            raise UserError(_("Invoice must be in draft or Pro-forma state in order to validate it."))

        #Reviso cuales son los valores que contiene el to_open_invoices
        to_open_invoices.action_date_assign()
        to_open_invoices.action_move_create()
        objeto = to_open_invoices.invoice_validate()

        # Si es una factura de cliente o una rectificativa de cliente, actualizo los correlativos
        if self.type == "out_invoice" or self.type == "out_refund":
            # Actualizo los valores de correlativo
            sql = "SELECT number_next,number_increment,final FROM ir_sequence WHERE id = " + str(self.tipo_doc.secuencia.id)
            self.env.cr.execute(sql)
            resultado = self.env.cr.fetchone()
            # Ahora que ya los recupere entonces establezco los valores
            valor = 0
            #Si no estoy en el último, debo iterar o actualizar el correlativo
            if int(self.correlativo.lstrip("0")) != resultado[2]:
                if int(self.correlativo.lstrip("0")) == resultado[0]:
                    # Solo va a iterar
                    valor = resultado[0] + resultado[1]
                    # Debo verificar, si el que estoy guardando es el último no voy a iterar
                else:
                    # Caso contrario es un valor que debo actualizar
                    valor = int(self.correlativo) + resultado[1]
                # Ahora actualizo el valor presente ir_sequence
                sql = "UPDATE ir_sequence SET number_next = " + str(valor) + " WHERE id = " + str(self.tipo_doc.secuencia.id)
                self.env.cr.execute(sql)

        # Si es una factura de cliente y es consumidor final, debo de calcular los campos que necesito mostrar en el reporte
        if (self.type == "out_invoice" or self.type == "in_invoice") and self.tipo_doc.nombre == "Consumidor Final":
            if len(self.tax_line_ids) > 0:
                pfcomps = self.env.user.company_id.partner_id.property_account_position_id.name
                pfclis = self.partner_id.property_account_position_id.name
                quitar = []
                ninguno = False
                pfcomp = unicode(pfcomps)
                pfcli = unicode(pfclis)
                parampc = self.env["ir.config_parameter"].search([['key', '=', 'peq_contrib']])[0].value
                paramgc = self.env["ir.config_parameter"].search([['key', '=', 'gra_contrib']])[0].value
                tgc = paramgc
                tpc = parampc
                aplica = False
                if pfcomp == tgc and pfcli == tpc:
                    #Entra en efecto el impuesto definido, que va a aumentar el total de la venta
                    aplica = True
                elif pfcomp == tpc and pfcli == tgc:
                    #Entra en efecto el impuesto definido, que le va a restar al total de la venta
                    aplica = True
                else:
                    ninguno = True

                #Esto solo aplica si el total sin impuestos es mayor o igual, para hacer la comparación debo recuperar el límite
                limite = self.partner_id.property_account_position_id.quantity_limit
                if aplica:
                    if self.amount_untaxed >= limite:
                        #Esto me quiere decir que los impuestos no aplican, los debo quitar
                        ninguno = False
                    else:
                        ninguno = True

                #Recupero de los parametros los nombres de los impuestos
                val1 = self.env["ir.config_parameter"].search([['key', '=', 'retenido']])[0].value
                val2 = self.env["ir.config_parameter"].search([['key', '=', 'percibido']])[0].value
                quitar.append(val1)
                quitar.append(val2)
                #Esto indica que debo quitar esos impuestos
                if ninguno == True:
                    indice = []
                    index = 0
                    for impuesto in self.tax_line_ids:
                        if impuesto.name in quitar:
                            indice.append(index)
                        index+=1

                    for valor in indice:
                        self.tax_line_ids[valor].amount = 0

                if self.tipo_doc.nombre == "Consumidor Final":
                    precio_cimp = 0
                    dp = self.env["decimal.precision"].search([["name", "=", "Product Price"]])[0].digits
                    for detalle in self.invoice_line_ids:
                        precio_cimp = detalle.price_unit * 1.0
                        for impuesto in detalle.invoice_line_tax_ids:
                            #Si el impuesto es un porcentaje entonces lo calculo asi
                            monto_imp = 0.0
                            #Debo de verificar si el impuesto aplica
                            #Aqui tengo que recupera los nombres de los impouestos de retencion y percepcion
                            if not((impuesto.name == quitar[0] or impuesto.name == quitar[1]) and ninguno == True):
                                if impuesto.amount_type == "percent":
                                    val = round((impuesto.amount / 100.0),dp)
                                    monto_imp = round(detalle.price_unit * val,dp)
                                #Pero si el impuesto es una cantidad fija entonces solo se la debo sumar al precio
                                elif impuesto.amount_type == "fixed":
                                    monto_imp = round(impuesto.amount,dp)
                            precio_cimp += monto_imp
                        nvalor = round(detalle.quantity * precio_cimp,dp)
                        detalle.write({"price_ci":precio_cimp})
                        detalle.write({"price_subtotal_ci":nvalor})

        self.write({"residual_signed":self.amount_total_signed})
        #Ahora que ya ha sido validada ya existen las partidas asociadas, y las mismas deben ser corregidas
        self.corregir_movimientos()
        return objeto

    def prueba(self):
        return True

    @api.multi
    def action_invoice_sent(self):
        """ Open a window to compose an email, with the edi invoice template
            message loaded by default
        """
        self.ensure_one()
        plantilla = self.tipo_doc.plantilla
        template = plantilla
        compose_form = self.env.ref('mail.email_compose_message_wizard_form', False)
        ctx = dict(
            default_model='account.invoice',
            default_res_id=self.id,
            default_use_template=bool(template),
            default_template_id=template.id,
            default_composition_mode='comment',
            mark_invoice_as_sent=True,
            custom_layout="account.mail_template_data_notification_email_account_invoice"
        )
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form.id, 'form')],
            'view_id': compose_form.id,
            'target': 'new',
            'context': ctx,
        }
        fields.Many2one(required=False,string="Plantilla de Correo",comodel_name='mail.template', delegate=True)