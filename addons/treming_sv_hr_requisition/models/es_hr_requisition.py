# -*- coding: utf-8 -*-

#from openerp import models, fields, api
from datetime import timedelta
from datetime import date
from openerp.exceptions import ValidationError
from openerp import models, fields, api, exceptions
import simplejson as json
import datetime as dt
#from duplicity.tempdir import default

class EsHrRequistion(models.Model):
    _name = 'hr.requisition'
    _inherit = ['mail.thread']

    #Lista de estados
    state = fields.Selection([
        ('draft',"No asignado"),
        ('confirmed',"En proceso"),
        ('done', "Finalizado"),
        ])


    #Lista Genero
    genderList = [('0','Femenino'),('1','Masculino'),('2','Indiferente')]
    #Lista estado civil
    civilStatusList = [('0','Soltero'),('1','Casado'),('2','Indiferente')]
    #Lista vehiculo
    vehicleList = [('0','Indispensable'),('1','Deseable'),('2','No Necesita')]
    #Lista capacitaciones
    trainingList = [('0','No'),('1','Si')]
    #Detalle de prioridades
    AVAILABLE_PRIORITIES = [
        ('0', 'Baja'),
        ('1', 'Normal'),
        ('2', 'Alta'),
        ('3', 'Muy Alta'),
        ]

    ##CAMPOS DE DE LA VISTA -----------------------------------------------------------------------------------------------------------------------

    #####DATOS DEL SOLICITANTE
    #Servicio solicitado
    service = fields.Many2one(string="Servicio solicitado: ", help="Espesificar el servicio solicitado.", comodel_name='hr.service')
    #Nombre de la empresa
    businessname = fields.Char(string="Nombre de la empresa")
    partner_id = fields.Many2one('res.partner', string='Cliente', track_visibility='onchange', index=True,
        help="Selecione le nombre del cliente de la lista.")

    #Para BI
    partner_id_count = fields.Integer(
        string="Partner count", compute='_get_partner_id_count', store=True)
    #Funcion para BI
    @api.depends('partner_id')
    def _get_partner_id_count(self):
        for r in self:
            r.partner_id_count = len(r.partner_id)

    #Contacto de la empresa
    contactBusinessName = fields.Char(string="Nombre y Apellido")
    #Cargo
    contactBusinessPosition = fields.Char(string="Cargo")
    #Telefono
    contactBusinessTelephone = fields.Char(string="Teléfono")
    #Email
    contactBusinessEmail = fields.Char(string="Email")

    #####INFORMACION DEL PUESTO
    #Numero de vacantes
    no_of_recruitment = fields.Integer(string="Cantidad de Plazas", default=1)
    #Nombre de la plaza
    jobname = fields.Many2one(string="Nombre de la plaza",comodel_name="hr.job")
    #jobname = fields.Char(string="Nombre de la plaza")
    #Actividades espesificas del puesto
    descriptionPosition = fields.Html(string="Actividades espesificas del puesto")
    #Tipo de plaza
    typeJob = fields.Many2one(string="Tipo de plaza", help="Espesificar el tipo de plaza", comodel_name="hr.typejob")
    #Espesificar la duracion si es temporal
    #Fecha de inicio
    datestart = fields.Date(string="Inicio")
    #Fecha fin
    dateend = fields.Date(string="Fin")
    #Fecha deseable de inicio
    dateDesirableStart = fields.Date(string="Fecha deseable de inicio")
    #Salario a ofertar
    salaryOffer = fields.Float(string="Salario a ofertar", default=0.0)
    #Horario de trabajo
    scheduleJob = fields.Char(string="Horarios de trabajo")
    #Direccion donde estara asignado
    addressAssigned = fields.Text(string="Dirección")

    #####BENEFICIOS
    #Lista de beneficios
    listBenefits = fields.Many2many('hr.tagbenefits', 'tagbenefits_lead_tag_rel', 'tagbenefits_lead_id', 'tagbenefits_tag_id', string="Beneficios")
    #Observaciones y comentarios adicionales al Puesto o del Proyecto que se desempeñará
    commentsAdditional = fields.Text(string="Comentarios adicionales", help="Observaciones y comentarios adicionales al Puesto o del Proyecto que se desempeñará")

#     #Comisiones
#     commissions = fields.Boolean(string="Comisiones", default=False)
#     #Viáticos
#     food = fields.Boolean(string="Viáticos")
#     #Política de incremento
#     politicsIncrease = fields.Boolean(string="Política de incremento", default=False)
#     #Prestaciones de ley
#     benefitsLaw = fields.Boolean(string="Prestaciones de ley", default=False)
#     #Depreciación
#     depreciation = fields.Boolean(string="Depreciación", default=False)
#     #Seguro Médico
#     insuranceDoctor = fields.Boolean(string="Seguro Médico", default=False)
#     #Celular
#     CellPhone = fields.Boolean(string="Celular", default=False)
#     #Bonos
#     bonds = fields.Boolean(string="Bonos", default=False)
#     #Seguro de vida
#     insuranceLife = fields.Boolean(string="Seguro de vida", default=False)
#     #Capacitación
#     training = fields.Selection(trainingList, string="Capacitación", default=trainingList[0][0])
#     #Otros beneficios
#     otherBenefits = fields.Text(string="Otros beneficios")



    #####INFORMACION DEL PERSONAL A CONTACTAR
    #Edad inicial
    ageStart = fields.Integer(string="Edad")
    #Edad fin
    ageEnd = fields.Integer(string="a")
    #Genero
    gender = fields.Selection(genderList, string="Género", default=genderList[2][0])
    #Estado Civil
    civilStatus = fields.Selection(civilStatusList, string="Estado Civil", default=civilStatusList[2][0])
    #Nivel Académico
    levelAcademic = fields.Many2one(string="Nivel Académico", comodel_name="hr.levelacademic")
    #Carrera Universitaria
    tag_ids = fields.Many2many('hr.tagcareer', 'tagcareer_lead_tag_rel', 'tagcareer_lead_id', 'tagcareer_tag_id', string='Carrera Universitaria', help="Establecer las carreras universitarias")
    #Idiomas
    languages = fields.Many2many('hr.languages', 'languages_lead_tag_rel', 'languages_lead_id', 'languages_tag_id', string="Idiomas")
    #Experiencia Laboral (Años)
    experienceJob = fields.Char(string="Experiencia Laboral (Años)")
    #Conocimientos específicos
    knowledgeSpecific = fields.Text(string="Conocimientos específicos")
    #Cualidades específicas del Candidato: (Aptitudes, Características, Competencias)
    tag_ids_qualities = fields.Many2many('hr.tagqualities', 'tagqualities_lead_tag_rel', 'tagqualities_lead_id', 'tagqualities_tag_id', string='Cualidades espesificas', help="Establecer las cualidades espesificas")
    #Vehiculo
    vehicle = fields.Selection(vehicleList,string="Vehículo", default=vehicleList[2][0])
    #Otras Observaciones
    otherObservations = fields.Text(string="Otras Observaciones")

    #####PARA USO INTERNO
    #Analista asignada o Nombre del solicitante
    #how_request = fields.Char(string ='Quien solicita: ',store=True, readonly=False)
    how_request = fields.Many2one('res.users', string='Salesperson', index=True, default=lambda self: self.env.user)

    #priority = fields.Many2one(string="Prioridad: ", help="Tipo de prioridad",
    #                           comodel_name='hr.priority')
    #Prioridad de la requisicion.
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Puntuacion', index=True, default=AVAILABLE_PRIORITIES[0][0])

    #Campo de responsables
    responsable_ids = fields.One2many('hr.responsable', 'requisition_id', string="Responsables")

    #Agregar Notas
    note = fields.Text(string="Notas")

    #Numero de Reclutados
    #no_of_recruitment = fields.Integer(string="Plazas", default=1)
    #Numero de contratados
    no_of_hired_employee = fields.Integer(string="Contratados", default=0)


    ##CAMPOS DE SEGUNDO PLANO ---------------------------------------------------------------------------------------------------------------------



    #Barra de progreso
    taken_job = fields.Float(string="Progreso", compute='_taken_job')

    #Nombre de la requisicion
    name = fields.Char(string="name")
    fullname = fields.Char()

    #Estado del requerimiento
    active = fields.Boolean(default=True)
    activeS = fields.Boolean(default=True)
    #Fecha fin de terminacion del requerimiento.
    start_date = fields.Date(default=date.today())
    finalize_date = fields.Date()

    #jobAssignedResponsible = fields.Selection([('noAsignado', 'Sin Asignar'),('asignado','Asignado')], default='noAsignado', string='Delegado')
    #valor = fields.Boolean(default=False, compute='_calcular_valor')

    nameRequistionLabel = fields.Char()

    #Vista rapida en el boton del total de contratados
    viewFlashCalculeButton = fields.Char(default='0/0', compute='_calcular_contratadosvsrequisition')

    #Control de ls sumatoria de asignados a responsables
    sumarAssigned = fields.Integer(default=0)

    #Valor old de no_of_recruitment
    old_no_of_recruitment = fields.Integer(default=0)

    #Hechar llave por dentro
    openStateOldRecruitment = fields.Boolean(default=True)







    ##FUNCIONES GENERALES ---------------------------------------------------------------------------------------------------------------------


    def _onchange_partner_id_values(self, partner_id):
        """ Retorna los nuevos valores cuando partner_id es cambiado """
        if partner_id:
            partner = self.env['res.partner'].browse(partner_id)
            partner_name = partner.parent_id.name
            if not partner_name and partner.is_company:
                partner_name = partner.name
            #print partner.name
            #print partner.is_company
            label = str(partner_name)
            if str(partner_name) != str(partner.name):
                if str(partner_name) == "False":
                    label = str(partner.name)
                else:
                    label = str(partner_name)+', '+str(partner.name)

            return {
                'businessname': partner_name,
                'contactBusinessName': partner.name if not partner.is_company else False,
                #'title': partner.title.id,
                #'street': partner.street,
                #'street2': partner.street2,
                #'city': partner.city,
                #'state_id': partner.state_id.id,
                #'country_id': partner.country_id.id,
                'contactBusinessEmail': partner.email,
                'contactBusinessTelephone': partner.phone,
                #'mobile': partner.mobile,
                #'fax': partner.fax,
                #'zip': partner.zip,
                'contactBusinessPosition': partner.function,
                'nameRequistionLabel': label,
                'fullname': label,
            }
        return {}

    #Metodo que esta pendiente de los cambios de partner_id
    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        values = self._onchange_partner_id_values(self.partner_id.id if self.partner_id else False)
        self.update(values)


    #Metodo para contruir el identificador de la requisition, para los cambos Many2one que hagan referencia a la requisition actual que se estra construllendo.

    @api.multi
    @api.depends('name')
    def name_get(self):
        result = []
        #fullname = ''
        for requisition in self:
            #Obtener el valor de la prioridad
            string = str(requisition.AVAILABLE_PRIORITIES[int(requisition.priority)])
            x = string.split(",")[1].split(")")[0].strip("'")
            x = list(x)
            x[0] = ''
            x[1] = ''
            priorityName = ''.join(x)
            name = str(requisition.id) + '/'+ str(priorityName)+'/'+str(requisition.nameRequistionLabel)
            result.append((requisition.id, name))
        return result

    @api.depends('no_of_recruitment','no_of_hired_employee')
    def _calcular_contratadosvsrequisition(self):
        self.viewFlashCalculeButton = str(self.no_of_hired_employee)+'/'+str(self.no_of_recruitment)
         #print "_calcular_contratadosvsrequisition"
        #print self.openStateOldRecruitment
        if self.openStateOldRecruitment == True:
            #print str(self.old_no_of_recruitment)+" = "+str(self.no_of_recruitment)
            #print str(self.old_no_of_recruitment)
            self.old_no_of_recruitment = self.no_of_recruitment
            #print "solo una vez: "+str(self.old_no_of_recruitment)
            self.openStateOldRecruitment = False
            #print "solo una vez: (echar llave) "+str(self.openStateOldRecruitment)


#     def openStateOldRecruitmentPage(self):
#         print "openStateOldRecruitmentPage"


#     def show_recruitment(self):
#         #print "Valor de recruitment" + str(self.no_of_recruitment)
#         return self.no_of_recruitment
    @api.multi
    def show_employees_requisition(self):
        '''
        Este metodo muestra en un grid las lista de los empleados que han sido contratados que corresponde a esta requisicion
        '''
        action = self.env.ref('hr.open_view_employee_list_my')
        result = action.read()[0]
        result['domain'] = [('nameRequisition_id', '=', str(self.id))]
        return result


    @api.multi
    def toggle_statistics(self):
        print "Button statistics"

#     def default_value(self):
#         return self.uid
    @api.multi
    def toggle_active(self):
        """ Inverse the value of the field ``active`` on the records in ``self``. """
        for record in self:
            #print "Estoy sobreescribiendo el metodo de active"
            record.activeS = not record.activeS
            self.finalize_date = date.today()


#     @api.onchange('active')
#     def registry_finalize_date(self):
#         self.finalize_date = date.today()
#         print self.finalize_date

    @api.depends('no_of_recruitment', 'no_of_hired_employee')
    def _taken_job(self):
        for r in self:
            if not r.no_of_recruitment:
                r.taken_job = 0.0
            else:
                if r.no_of_hired_employee != 0:
                    r.taken_job = 100.0 * r.no_of_hired_employee / r.no_of_recruitment
                #if int(r.no_of_hired_employee) == int(r.no_of_recruitment):
                    #print "dentro del if 100% contratados "
                    #r.action_done()


    @api.depends('name')
    def generyName(self):
        for r in self:
            print self.name

    #Metodos para gestionar el workflow
    @api.multi
    def action_draft(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        self.state = 'confirmed'

    @api.multi
    def action_done(self):
        self.state = 'done'
        self.toggle_active()

    @api.onchange('no_of_recruitment')
    def _verify_valid_no_of_recruitment(self):
        print "_verify_valid_no_of_recruitment"
        if self.no_of_recruitment < 1:
            return {
                'warning': {
                    'title': "Valor incorrecto de plazas",
                    'message': "El número de plazas disponibles no puede ser cero ó negativa.",
                },
            }

    @api.constrains('no_of_recruitment')
    def _check_no_of_recruitment(self):
        if self.no_of_recruitment < 1:
            raise exceptions.ValidationError("El número de plazas disponibles no puede ser cero ó negativa.")


#     @api.model
#     def default_get(self, fields):
#         context = self._context or {}
#         print "method default_get"
#         res = super(EsHrRequistion, self).default_get(fields)
#         res.update({
#             'openStateOldRecruitment': True,
#         })
#         return res

#     @api.model
#     def default_get(self, fields):
#         print "metodo default_get old_value_recruitment"
#         for record in self:
#             print record
#         default_name = self._context.get('no_of_recruitment')
#         print default_name
#         #self.old_no_of_recruitment = self.no_of_recruitment
#         #print "valor old_no_of_recruitment "+str(self.old_no_of_recruitment)
#         res = super(EsHrRequistion, self).default_get(fields)
#         return res

    #@api.multi
    @api.onchange('no_of_recruitment','responsable_ids')
    def _verify_valid_responsible(self):
        count = 0
        for r in self:
            count = len(r.responsable_ids)
        #print "Imprimiendo la variable count: " + str(count)
        for record in self:
            self.sumarResponsableAssigned(record)
        if self.sumarAssigned > self.no_of_recruitment:
            return {
                'warning': {
                    'title': "Valor de asignaciones incorrectas",
                    'message': "El numero de asignaciones debe ser igual o menor al número de plazas de la requisición.",
                },
            }

        #print "Imprimiento el TOTAL: "+ str(self.sumarAssigned)

    @api.one
    def sumarResponsableAssigned(self, record):
        self.sumarAssigned = 0
        for r in record.responsable_ids:
            if r.assigned != False:
                #print "dentro de sumarRAsig: " + str(r.assigned)
                self.sumarAssigned = self.sumarAssigned + int(r.assigned)
                #Verificar que la suma del numero de asignados a todos los responsables no sea mayor a no_of_recruitment
                #if self.no_of_recruitment < self.sumarAssigned:
                #    raise exceptions.ValidationError("El total de los asignados en los responsables es mayor al numero de plazas.")
                #print "self.sumarAssigned "+ str(self.sumarAssigned)

    def selectorResponsable(self):
        count = 0
        for r in self:
            count = len(r.responsable_ids)
        if count != 0:
            print "valor de count:"+str(count)
            for record in self:
                self.addDataResponsable(record)

    @api.one
    def addDataResponsable(self, record):
        for r in record.responsable_ids:
            r.service = self.service
            print r
#             r.service = self.service
#             r.businessname = self.businessname
#             r.partner_id = self.partner_id
#             r.contactBusinessName = self.contactBusinessName
#             r.contactBusinessPosition = self.contactBusinessPosition
#             r.contactBusinessTelephone = self.contactBusinessTelephone
#             r.contactBusinessEmail = self.contactBusinessEmail
#             r.no_of_recruitment = r.assigned


    @api.multi
    def write(self, vals):
        #print vals

        vals['openStateOldRecruitment'] = True
        print vals

        if 'responsable_ids' in vals:
            print "Ver el contenido de la lista de responsables"
            for item in vals['responsable_ids']:
                if item[2]:
                    item[2]['onlyAssign'] = True
            #vals['responsable_ids'][0][2]['onlyAssign'] = True
                    #item[2]['datestart'] = self.datestart

        if self.state == False:
            #print "if state False"
            #print self.jobname.id
            try:
                if not self.jobname.id:
                    print str(self.jobname.id)
                else:
                    print str(self.jobname.id)
                    sql = ("update hr_job set no_of_recruitment=((select no_of_recruitment from hr_job where id="+str(self.jobname.id)+")+"+str(self.no_of_recruitment)+") where id="+str(self.jobname.id)+";")
                    self.env.cr.execute(sql)
            except Exception,e:
                        print (str(e));
        if ((self.state != False) and ('service' not in vals)):
            if 'old_no_of_recruitment' in vals:
                if int(self.no_of_recruitment) > int(vals['old_no_of_recruitment']):
                    try:
                        if not self.jobname.id:
                            print str(self.jobname.id)
                        else:
                            print str(self.jobname.id)
                            sql = ("update hr_job set no_of_recruitment=((select no_of_recruitment from hr_job where id="+str(self.jobname.id)+")-("+str(self.no_of_recruitment)+"-"+str(vals['old_no_of_recruitment'])+")) where id="+str(self.jobname.id)+";")
                            print sql
                            self.env.cr.execute(sql)
                            print "if state != False(1)"
                    except Exception,e:
                        print (str(e))
                if int(self.no_of_recruitment) < int(vals['old_no_of_recruitment']):
                    try:
                        if not self.jobname.id:
                            print str(self.jobname.id)
                        else:
                            print str(self.jobname.id)
                            sql = ("update hr_job set no_of_recruitment=((select no_of_recruitment from hr_job where id="+str(self.jobname.id)+")+("+str(vals['old_no_of_recruitment'])+"-"+str(self.no_of_recruitment)+")) where id="+str(self.jobname.id)+";")
                            print sql
                            self.env.cr.execute(sql)
                            print "if state != False(2)"
                    except Exception,e:
                        print (str(e))
            #self.selectorResponsable()

        return super(EsHrRequistion, self).write(vals)


    @api.constrains('sumarAssigned','no_of_recruitment')
    def verify_sumarAssigned(self):
        if self.no_of_recruitment < self.sumarAssigned:
            raise exceptions.ValidationError("El total de los asignados en los responsables es mayor al numero de plazas.")
        if self.openStateOldRecruitment == True:
            #print str(self.old_no_of_recruitment)+" = "+str(self.no_of_recruitment)
            #print str(self.old_no_of_recruitment)
            self.old_no_of_recruitment = self.no_of_recruitment
            #print "solo una vez: "+str(self.old_no_of_recruitment)
            self.openStateOldRecruitment = False
            #print "solo una vez: (echar llave) "+str(self.openStateOldRecruitment)
        #print "self.sumarAssigned(2) "+ str(self.sumarAssigned)
            #if r.assigned[1] != False:
            #    print "dentro de sumarRAsig: " + str(r.assigned[1])
            #    self.sumarAssigned = self.sumarAssigned + int(r.assigned[1])
      #      print self.responsable_ids.assigned(i)
      #  print 'dentro del onchange'
#         if len(self.responsable_ids) > 0:
            #sql = ("update hr_job set jobAssignedResponsible='asignado' where id=" + str(self.id) + ";")
            #self.env.cr.execute(sql)
#
#             print 'dentro del if'
#             for record in self:
#                 record.write({'jobAssignedResponsible': 'asignado'})
#                 print 'dentro del for'


#     @api.model
#     def create(self, values):
#         #print 'prueba'
#         #sql = ("select price_unit,quantity,price_subtotal, tipov from account_invoice_line where invoice_id='" + str(self.id) + "';")
#         #print 'Estoy sobreescribiendo el metodo el boton de guardar!!'
#            #return super(Job, self.with_context(mail_create_nosubscribe=True)).create(values
#         res_id = super(EsHrRequistion, self.with_context(valor=True)).create(values)
#         return res_id
#         #sql = ("update hr_job set valor=True where id='" + str(id) + "';")
#         #self.env.cr.execute(sql)
#
    @api.model
    def create(self, values):
        #print "metodo multi"
        #print values
        #print self.id
        print "Imprimiendo los values del metodo create"
        print values
        res_id = super(EsHrRequistion, self).create(values)
        return res_id

    @api.constrains("datestart", "dateend")
    def ValidTypeJobTeTemporary(self):
        print "Validar fecha tipo de plaza temporarl"
        for record in self:
            if record.datestart != False and record.dateend != False:
                # La fecha de fin no puede ser anterior a la fecha de incio
                a = dt.datetime.strptime(record.datestart, "%Y-%m-%d")
                b = dt.datetime.strptime(record.dateend, "%Y-%m-%d")
                if a > b:
                    raise ValidationError("La fecha de inicio no puede ser posterior a la fecha de fin del periodo de plaza temporal")

    @api.constrains("ageStart", "ageEnd")
    def ValidAgePerson(self):
        print "Validar la edad de la persona a contactar"
        for record in self:
            if record.ageStart != False and record.ageEnd != False:
                # La edad de fin no puede ser menor a la edad de incio
                a = int(record.ageStart)
                b = int(record.ageEnd)
                if a > b:
                    raise ValidationError("La edad de inicio no puede ser posterior a la edad de fin del personal a contratar")
#     @api.multi
#     def write(self, values):
#         print "metodo write"
#         res_id = super(EsHrRequistion, self).create(values)
#         return res_id


#     @api.one
#     @api.depends("how_request")
#     def _calcular_valor(self):
#         #RECORREMOS LA LISTA DEVUELTA EN LA EJECUCIÓN DEL SQL
#         try:
#             sql = ("update hr_job set valor=True where id='" + str(self.id) + "';")
#             self.env.cr.execute(sql)
#
#             for item  in self.env.cr.fetchall():
#                 print item[0]
#         except Exception,e:
#             print (str(e));
#
