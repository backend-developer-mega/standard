# -*- coding: utf-8 -*-

from datetime import timedelta
from datetime import date
from openerp.exceptions import ValidationError
from openerp import models, fields, api, exceptions
import simplejson as json
import datetime as dt

class EsHrRequistionResponsable(models.Model):
    _name = 'hr.responsable'
    _inherit = ['mail.thread']

    #Variables indispensables
    requisition_id = fields.Many2one('hr.requisition', string="Course")
    responsible_id = fields.Many2one('res.users', string="Responsable", index=True)
    assigned = fields.Integer(string="Plazas asignadas", default=1)
    #FIN DE VARIABLES INDISPENSABLES

    #Lista Genero
    genderList = [('0','Femenino'),('1','Masculino'),('2','Indiferente')]
    #Lista estado civil
    civilStatusList = [('0','Soltero'),('1','Casado'),('2','Indiferente')]
    #Lista vehiculo
    vehicleList = [('0','Indispensable'),('1','Deseable'),('2','No Necesita')]
    #Detalle de prioridades
    AVAILABLE_PRIORITIES = [
        ('0', 'Baja'),
        ('1', 'Normal'),
        ('2', 'Alta'),
        ('3', 'Muy Alta'),
        ]

    #Email
    contactBusinessEmail = fields.Char(string="Email", compute='_onchange_id_values')

    #Numero de vacantes
    no_of_recruitment = fields.Integer(string="Cantidad de Plazas", default=1, compute='_onchange_id_values')

    #Numero de contratados
    no_of_hired_employee = fields.Integer(string="Contratados", default=0)

    #Barra de progreso
    taken_job = fields.Float(compute='_taken_job')
    taken_job_or = fields.Float(string="Progreso", compute='_taken_job_or')

    #Lista de beneficios
    listBenefits = fields.Many2many('hr.tagbenefits', 'tagbenefitsr_lead_tag_rel', 'tagbenefitsr_lead_id', 'tagbenefitsr_tag_id', string="Beneficios", compute='_onchange_id_values')

    #Vista rapida en el boton del total de contratados
    viewFlashCalculeButton = fields.Char(default='0/0', compute='_calcular_contratadosvsrequisition')

    #Valor old de no_of_recruitment
    old_no_of_recruitment = fields.Integer(default=0, compute='_onchange_id_values')

    #Hechar llave por dentro
    openStateOldRecruitment = fields.Boolean(default=True, compute='_onchange_id_values')

    #Fecha asignacion del requerimiento.
    start_date = fields.Date(default=date.today())
    finalize_date = fields.Date()

    #####DATOS DEL SOLICITANTE
    #Servicio solicitado
    service = fields.Many2one(string="Servicio solicitado: ", help="Espesificar el servicio solicitado.", comodel_name='hr.service', compute='_onchange_id_values')
    #Nombre de la empresa
    businessname = fields.Char(string="Nombre de la empresa", compute='_onchange_id_values')
    partner_id = fields.Many2one('res.partner', string='Cliente', track_visibility='onchange', index=True,
        help="Selecione le nombre del cliente de la lista.", compute='_onchange_id_values')
    #Contacto de la empresa
    contactBusinessName = fields.Char(string="Nombre y Apellido", compute='_onchange_id_values')
    #Nombre de la requisicion
    name = fields.Char(string="name")
    nameRequistionLabel = fields.Char(string="nameRequistion")
    #Cargo
    contactBusinessPosition = fields.Char(string="Cargo", compute='_onchange_id_values')
    #Telefono
    contactBusinessTelephone = fields.Char(string="Teléfono", compute='_onchange_id_values')
    #Agregar Notas
    note = fields.Text(string="Notas", compute='_onchange_id_values')
    #Nombre de la plaza
    jobname = fields.Many2one( string="Nombre de la plaza",comodel_name="hr.job", compute='_onchange_id_values')
    #Fecha deseable de inicio
    dateDesirableStart = fields.Date(string="Fecha deseable de inicio", compute='_onchange_id_values')
    #Salario a ofertar
    salaryOffer = fields.Float(string="Salario a ofertar", default=0.0, compute='_onchange_id_values')
    #Horario de trabajo
    scheduleJob = fields.Char(string="Horarios de trabajo", compute='_onchange_id_values')
    #Tipo de plaza
    typeJob = fields.Many2one( string="Tipo de plaza", help="Espesificar el tipo de plaza", comodel_name="hr.typejob", compute='_onchange_id_values')
    #Espesificar la duracion si es temporal
    #Fecha de inicio
    datestart = fields.Date(string="Inicio", compute='_onchange_id_values')
    #Fecha fin
    dateend = fields.Date(string="Fin", compute='_onchange_id_values')
    #Beneficios
    #Observaciones y comentarios adicionales al Puesto o del Proyecto que se desempeñará
    commentsAdditional = fields.Text(string="Comentarios adicionales", help="Observaciones y comentarios adicionales al Puesto o del Proyecto que se desempeñará", compute='_onchange_id_values')
    #Direccion donde estara asignado
    addressAssigned = fields.Text(string="Dirección", compute='_onchange_id_values')
    #Actividades espesificas del puesto
    descriptionPosition = fields.Html(string="Actividades espesificas del puesto", compute='_onchange_id_values')
    #####INFORMACION DEL PERSONAL A CONTACTAR
    #Edad inicial
    ageStart = fields.Integer(string="Edad", compute='_onchange_id_values')
    #Edad fin
    ageEnd = fields.Integer(string="a", compute='_onchange_id_values')
    #Genero
    gender = fields.Selection(genderList, string="Género", default=genderList[2][0], compute='_onchange_id_values')
    #Estado Civil
    civilStatus = fields.Selection(civilStatusList, string="Estado Civil", default=civilStatusList[2][0], compute='_onchange_id_values')
    #Nivel Académico
    levelAcademic = fields.Many2one( string="Nivel Académico", comodel_name="hr.levelacademic", compute='_onchange_id_values')
    #Carrera Universitaria
    tag_ids = fields.Many2many('hr.tagcareer', 'tagcareerr_lead_tag_rel_res', 'tagcareerr_lead_id_res', 'tagcareerr_tag_id_res', string='Carrera Universitaria', help="Establecer las carreras universitarias", compute='_onchange_id_values')
    #Idiomas
    languages = fields.Many2many('hr.languages', 'languagesr_lead_tag_rel_res', 'languagesr_lead_id_res', 'languagesr_tag_id_res', string="Idiomas", compute='_onchange_id_values')
    #Experiencia Laboral (Años)
    experienceJob = fields.Char(string="Experiencia Laboral (Años)", compute='_onchange_id_values')
    #Conocimientos específicos
    knowledgeSpecific = fields.Text(string="Conocimientos específicos", compute='_onchange_id_values')
    #Cualidades específicas del Candidato: (Aptitudes, Características, Competencias)
    tag_ids_qualities = fields.Many2many('hr.tagqualities', 'tagqualitiesr_lead_tag_rel_res', 'tagqualitiesr_lead_id_res', 'tagqualitiesr_tag_id_res', string='Cualidades espesificas', help="Establecer las cualidades espesificas", compute='_onchange_id_values')
    #Vehiculo
    vehicle = fields.Selection(vehicleList,string="Vehículo", default=vehicleList[2][0], compute='_onchange_id_values')
    #Otras Observaciones
    otherObservations = fields.Text(string="Otras Observaciones", compute='_onchange_id_values')


    #####PARA USO INTERNO
    #Analista asignada o Nombre del solicitante
    #Prioridad de la requisicion.
    priority = fields.Selection(AVAILABLE_PRIORITIES, string='Puntuacion', index=True, default=AVAILABLE_PRIORITIES[0][0], compute='_onchange_id_values')
    #Estado del requerimiento
    active = fields.Boolean(default=True)
    activeS = fields.Boolean(default=True)
    onlyAssign = fields.Boolean(default=False)


    @api.depends('no_of_recruitment', 'no_of_hired_employee')
    def _taken_job(self):
        self._onchange_id_values()

    @api.one
    @api.depends('no_of_recruitment', 'no_of_hired_employee')
    def _taken_job_or(self):
        for r in self:
            if not r.no_of_recruitment:
                r.taken_job_or = 0.0
            else:
                if r.no_of_hired_employee != 0:
                    r.taken_job_or = 100.0 * r.no_of_hired_employee / r.no_of_recruitment
            if r.taken_job_or == 100.0:
                self.finalize_date = date.today()
        if self.taken_job_or == 100.0:
            self.finalize_date = date.today()

    @api.one
    @api.depends('contactBusinessEmail')
    def _onchange_id_values(self):
        """ Retorna los valores del requisition_id espesifico """
        for requisition in self.requisition_id:
            if (requisition.id and (self.env["hr.requisition"].search([['id', '=', self.requisition_id.id]]).active == True)):
                obj = self.env["hr.requisition"].search([['id', '=', self.requisition_id.id]])[0]
                #Datos del solicitante
                self.activeS = obj.activeS
                self.service = obj.service
                self.partner_id = obj.partner_id
                self.contactBusinessName = obj.contactBusinessName
                self.name = self.responsible_id.name
                self.businessname = obj.businessname
                #self.nameRequistionLabel = obj.nameRequistionLabel
                self.contactBusinessEmail = obj.contactBusinessEmail
                self.contactBusinessPosition = obj.contactBusinessPosition
                self.contactBusinessTelephone = obj.contactBusinessTelephone
                self.priority = obj.priority
                #Notebook
                #Page: Notas
                self.note = obj.note
                #Page: Informacion del puesto
                self.jobname = obj.jobname
                self.listBenefits = obj.listBenefits
                self.no_of_recruitment = self.assigned
                self.dateDesirableStart = obj.dateDesirableStart
                self.salaryOffer = obj.salaryOffer
                self.scheduleJob = obj.scheduleJob
                #self.no_of_hired_employee = obj.no_of_hired_employee  #Aqui hay que adactarlo a la requisicion
                self.openStateOldRecruitment = obj.openStateOldRecruitment
                self.typeJob = obj.typeJob
                self.datestart = obj.datestart
                self.dateend = obj.dateend
                self.commentsAdditional = obj.commentsAdditional
                self.addressAssigned = obj.addressAssigned
                self.descriptionPosition = obj.descriptionPosition
                #Page: Personal a contactar
                self.ageStart = obj.ageStart
                self.ageEnd = obj.ageEnd
                self.gender = obj.gender
                self.civilStatus = obj.civilStatus
                self.levelAcademic = obj.levelAcademic
                self.experienceJob = obj.experienceJob
                self.tag_ids_qualities = obj.tag_ids_qualities
                self.tag_ids = obj.tag_ids
                self.languages = obj.languages
                self.knowledgeSpecific = obj.knowledgeSpecific
                self.vehicle = obj.vehicle
                self.otherObservations = obj.otherObservations

                print "_onchange_id_values -> listBenefits"
                print self.listBenefits

    @api.depends('no_of_recruitment','no_of_hired_employee')
    def _calcular_contratadosvsrequisition(self):
        self.viewFlashCalculeButton = str(self.no_of_hired_employee)+'/'+str(self.no_of_recruitment)

    @api.multi
    def show_employees_requisition(self):
        '''
        Este metodo muestra en un grid las lista de los empleados que han sido contratados que corresponde a esta requisicion y a este responsable
        '''
        action = self.env.ref('hr.open_view_employee_list_my')
        result = action.read()[0]
        result['domain'] = [('nameRequisition_id', '=', str(self.requisition_id.id)),('responsible_id','=',self.responsible_id.id)]
        return result

    @api.multi
    def show_applicant_reponsable(self):
        '''
        Este metodo envia al usuario al kanba donde puede agregar aplicantes
        '''
        action = self.env.ref('treming_sh_hr_requisition.open_view_aplicant_list_my')
        result = action.read()[0]
        #iter(result['context']).next()['default_job_id'] = self.jobname.id
        #iter(result['context']).next()['default_requisition_id'] = self.requisition_id.id
        result['context'] = {'default_job_id': self.jobname.id, 'default_requisition_id': self.requisition_id.id, 'default_responsible_id' : self.responsible_id.id}
        #print result['context']
        #invoice_context = eval(result['context'])
        #invoice_context.update(
        #    {'op_type': op_type, 'partner_id': partner_id, 'parent_id': parent_id})
        #result['context'] = invoice_context
        #result['domain'] = [('nameRequisition_id', '=', str(self.requisition_id.id)),('responsible_id','=',self.responsible_id.id)]
        return result
