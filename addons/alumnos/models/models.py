# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from docutils.nodes import field

class alumnos(models.Model):
    _name = 'alumnos.alumnos'
    
    def _default_stage_id(self):
        if self._context.get('default_job_id'):
            ids = self.env['hr.recruitment.stage'].search([
                '|',
                ('job_id', '=', False),
                ('job_id', '=', self._context['default_job_id']),
                ('fold', '=', False)
            ], order='sequence asc', limit=1).ids
            if ids:
                return ids[0]
        return False

    name = fields.Char()
    materias = fields.Many2one('alumnos.materias', "Materias")
    value = fields.Integer()
    value2 = fields.Float(compute="_value_pc", store=True)
    description = fields.Text()
    job_id = fields.Many2one('alumnos.materias', "Departamento")
    stage_id = fields.Many2one('alumnos.stage', 'Stage', rack_visibility='onchange',
                               domain="['|', ('job_id', '=', False), ('job_id', '=', job_id)]", 
                               copy=False, index=True, default=_default_stage_id)

    @api.depends('value')
    def _value_pc(self):
        self.value2 = float(self.value) / 100

class materias(models.Model):
    _name = 'alumnos.materias'

    name = fields.Char()
    code = fields.Integer()
    
    @api.multi
    def name_get(self):
        '''Method to display name and code'''
        return [(rec.id, ' ' + str(rec.code) + ' - ' + rec.name) for rec in self]
    
class estados(models.Model):
    _name = 'alumnos.stage'
    _order = 'sequence'

    name = fields.Char()
    code = fields.Integer()
    job_id = fields.Many2one('alumnos.materias', "Departamento")
    sequence = fields.Integer(
        "Sequence", default=10,
        help="Gives the sequence order when displaying a list of stages.")
    
class course(models.Model):
    _name = 'alumnos.course'

    name = fields.Char()
    descripcion = fields.Char()
    line_ids = fields.One2many('alumnos.line', 'session_ids')

class session(models.Model):
    _name = 'alumnos.session'
    
    name = fields.Char()
    code = fields.Integer()
    
    course_id = fields.One2many('alumnos.line', 'course_ids')
    
class lineSession(models.Model):
    _name = 'alumnos.line'
    
    name = fields.Char()
    number = fields.Integer()
    
    course_ids  = fields.Many2one('alumnos.course')
    session_ids  = fields.Many2one('alumnos.session')
    
class workflow(models.Model):
    _name = 'alumnos.work'
    
    name = fields.Char()
    description = fields.Char()
    datos = fields.Char()
    linea = fields.Char()
    
    state = fields.Selection([('draft', 'Draft'), ('in_progress', 'Confirmed'),
                               ('open', 'Bid Selection'), ('done', 'Done'),
                               ('cancel', 'Cancelled')],
                              'Status', track_visibility='onchange', required=True,
                              copy=False, default='draft')
    
    
    @api.multi
    def action_draft(self):
        self.write({'state': 'draft'})
        
    
    @api.multi
    def action_in_progress(self):
        self.write({'state': 'in_progress'})
    
    @api.multi
    def action_open(self):
        self.write({'state': 'open'})
        
    @api.multi
    def action_done(self):
        self.write({'state': 'draft'})
        
class emailSend(models.Model):
    _name = "alumnos.email1"
    
    name = fields.Char()
    description = fields.Text()
    
    
    @api.multi
    def action_rfq_send(self):
        '''
        This function opens a window to compose an email, with the edi purchase template message loaded by default
        '''
        self.ensure_one()
        ir_model_data = self.env['ir.model.data']
        template_id = ir_model_data.get_object_reference('alumnos', 'email_template_edi_alumnos')[1]
        compose_form_id = ir_model_data.get_object_reference('mail', 'email_compose_message_wizard_form')[1]
        ctx = dict()
        ctx.update({
            'default_model': 'alumnos.email1',
            'default_res_id': self.ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
        })
        return {
            'name': _('Compose Email'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }