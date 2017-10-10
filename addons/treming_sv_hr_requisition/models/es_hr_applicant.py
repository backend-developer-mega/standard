# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError, UserError
from openerp import api, fields, models, _
from datetime import date

class EsHrApplicant(models.Model):
    _inherit = "hr.applicant"

    #Espesificar la requisicion a la que pertenece la aplicacion
    requisition_id = fields.Many2one('hr.requisition', ondelete='cascade', string='Requisición')
    responsible_id = fields.Many2one('res.users', string="Responsable", index=True)
    #name = fields.Char("Nombre del candidato")
    #partner_name = fields.Char("Nombre del candidato", compute='_campute_name')
    #Metodo agrega el value del campo name al campo partner_name
    #@api.onchange('name')
    #def _onchange_name_add_partner_name(self):
    #    self.partner_name = self.name

    #@api.depends('partner_name')
    #@api.one
    #def _campute_name(self):
    #    self.partner_name = self.name

    @api.depends("responsible_id")
    @api.onchange("responsible_id")
    def _compute_responsible(self):
        self.user_id = self.responsible_id or False

    #Agregando funcionabilidad de sincronizacion con el modelo hr.requisition al metodo create_employee_from_applicant
    @api.multi
    def create_employee_from_applicant(self):
        """ Create an hr.employee from the hr.applicants """
        employee = False
        for applicant in self:

            address_id = contact_name = False
            if applicant.partner_id:
                address_id = applicant.partner_id.address_get(['contact'])['contact']
                contact_name = applicant.partner_id.name_get()[0][1]
            if applicant.job_id and (applicant.partner_name or contact_name):
                applicant.job_id.write({'no_of_hired_employee': applicant.job_id.no_of_hired_employee + 1})
                employee = self.env['hr.employee'].create({'name': applicant.partner_name or contact_name,
                                               'job_id': applicant.job_id.id or False,
                                               'requisition_id': applicant.requisition_id.id or False,
                                               'responsible_id': applicant.responsible_id.id or False,
                                               'address_home_id': address_id or False,
                                               'department_id': applicant.department_id.id or False,
                                               'address_id': applicant.company_id and applicant.company_id.partner_id and applicant.company_id.partner_id.id or False,
                                               'work_email': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.email or False,
                                               'work_phone': applicant.department_id and applicant.department_id.company_id and applicant.department_id.company_id.phone or False})
#                applicant.write()
		try:
		   applicant.write({'emp_id': employee.id})
		except Exception, e:
		   print (str(e));
		   #applicant.write()

                if applicant.requisition_id.id:
                    #Actuliazar la requisicion que dio origen al contrato
                    sql = ("update hr_requisition set no_of_hired_employee=((select no_of_hired_employee from hr_requisition where id="+str(applicant.requisition_id.id)+")+1) where id="+str(applicant.requisition_id.id)+";")
                    self.env.cr.execute(sql)
                    #Actuliazar la carga de trabajo del hr.responsable.
                    sql1 = ("update hr_responsable set no_of_hired_employee=((select no_of_hired_employee from hr_responsable where (requisition_id="+str(applicant.requisition_id.id)+" and responsible_id = "+str(applicant.responsible_id.id)+"))+1) where (requisition_id="+str(applicant.requisition_id.id)+" and responsible_id = "+str(applicant.responsible_id.id)+");")
                    self.env.cr.execute(sql1)
                    #Verificar la cantidad de empleados contratados actualmente para cerrar la requisition automaticamente.
                    sql2 = ("select no_of_hired_employee, no_of_recruitment from hr_requisition where id="+str(applicant.requisition_id.id)+";")
                    self.env.cr.execute(sql2)
                    try:
                        for item  in self.env.cr.fetchall():
                            if item[0] == item[1]:
                                sql3 = ("update hr_requisition set state = 'done', finalize_date = '"+str(date.today())+"' where id="+str(applicant.requisition_id.id)+";")
                                self.env.cr.execute(sql3)
                    except Exception, e:
                        print (str(e));

                applicant.job_id.message_post(
                    body=_('New Employee %s Hired') % applicant.partner_name if applicant.partner_name else applicant.name,
                    subtype="hr_recruitment.mt_job_applicant_hired")
#                employee._broadcast_welcome()
            else:
                raise UserError(_('You must define an Applied Job and a Contact Name for this applicant.'))

        employee_action = self.env.ref('hr.open_view_employee_list')
        dict_act_window = employee_action.read([])[0]
        if employee:
            dict_act_window['res_id'] = employee.id
        dict_act_window['view_mode'] = 'form,tree'
        return dict_act_window
