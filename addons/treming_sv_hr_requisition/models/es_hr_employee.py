# -*- coding: utf-8 -*-
from openerp.exceptions import ValidationError
from openerp import api, fields, models

class EsHrEmployee(models.Model):
    _inherit = "hr.employee"

    #Espesificar la requisicion a la que pertenece la aplicacion
    requisition_id = fields.Many2one('hr.requisition', ondelete='set null', string='Requisición')
    #Persona de responsable de la contratacion de este empleado
    responsible_id = fields.Many2one('res.users', ondelete='set null', string="Responsable", index=True)

    #Convertir a texto plano
    #Nombre de la requisition
    nameRequisition_id = fields.Char(compute='_textRequisition_id', store=True)
    date_assign_requisition = fields.Date(string="dateAssignRequisition", compute='_textRequisition_id')
    #Fecha de asignacion Requisition
    date_assign = fields.Date(compute='_getDateAssign')

    @api.depends('date_assign')
    def _getDateAssign(self):
	if self.responsible_id.id:
	     sql = ("select create_date from hr_responsable where (requisition_id = "+str(self.requisition_id.id)+");")
             self.env.cr.execute(sql)
             for item  in self.env.cr.fetchall():
	         self.date_assign = ''+str(item[0])
#        self.date_assign = fields.Date(string="Fecha de asignación",related='requisition_id.datestart', store=False)





    @api.depends('nameRequisition_id','date_assign_requisition')
    @api.one
    def _textRequisition_id(self):
        if self.requisition_id:
            self.nameRequisition_id = str(self.requisition_id.id)
 	    #self.date_assign_requisition = self.env["hr.responsable"].search([['key', '=', 'peq_contrib']])[0]  
	    #if self.responsible_id :
	    #        sql = ("select create_date from hr_responsable where (requisition_id = "+str(self.requisition_id.id)+" and responsible_id="+str(self.user_id.id)+");")
            #	    self.env.cr.execute(sql)
	    #if self.responsible_id.id == False:
	    #        sql = ("select create_date from hr_responsable where (requisition_id = "+str(self.requisition_id.id)+" and responsible_id="+str(self.user_id.id)+");")
            #	    self.env.cr.execute(sql)
#            for item  in self.env.cr.fetchall():
#                self.date_assign_requisition = ''+str(item[0])
