# -*- coding: utf-8 -*-

from odoo import api, fields, models


class Topic(models.Model):

    _name = "topic.grade.online.topic"
    _description = "Temas trabajo de grado"

    name = fields.Char(string='Tema de grado', required=True, index=True, translate=True)
    eraise_topic_ids = fields.Char(string='Referencia')
    description = fields.Text(string='Descripcion')
    carrera_id = fields.Many2one('hr.department', string='Carrera')
    department_id = fields.Many2one('hr.job', string='Departamento')
    activity_ids = fields.One2many('topic.grade.online.activity', 'topic_id', "Actividades")
    activity_count = fields.Integer(compute='_compute_activity_count', string="Actividades")
    jefe_department_id = fields.Many2one('res.users', "Jefe de Departamento", track_visibility='onchange')
    coordinador_department_id = fields.Many2one('res.users', "Coordinador de Departamento", track_visibility='onchange')
    docente_director_id = fields.Many2one('res.users', "Docente director", track_visibility='onchange')
    evaluations_ids = fields.One2many('topic.grade.online.evaluations', 'topic_id') 
    total = fields.Float(string="Total", readonly=True, compute='calulate_total', store=True)
    project_topic_id = fields.Many2one('project.task', string='Tema inscripcion')
    student_ids = fields.Many2many('hr.employee', 'students_lead_tag_rel_res', 'students_lead_id_res', 'students_tag_id_res')
    

    #document_ids = fields.One2many('ir.attachment', string="Documentos")
    state = fields.Selection([
        ('process', 'Desarrollo de tema de grado'),
        ('open', 'Cerrado')
    ], string='Estado', readonly=True, required=True, track_visibility='always', copy=False, default='process', help="Muestra en que estado se encuentra un tema de grado.")

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}


    @api.multi
    def show_evaluations_topic(self):
        '''
        Este metodo muestra las evaluaciones que estan asociadas al tema de trbajo de grado
        '''
        action = self.env.ref('topic_grade_online.open_view_topic_grade_online_list')
        result = action.read()[0]
        result['domain'] = [('topic_id', '=', self.id)]
        return result


    @api.one
    @api.depends('evaluations_ids.note')
    @api.onchange('evaluations_ids.note')
    def calulate_total(self):
        divide = sum(1 for line in self.evaluations_ids)
        if divide != 0:
            self.total = sum(line.note for line in self.evaluations_ids) / sum(1 for line in self.evaluations_ids)
        elif divide == 0:
            self.total = 0.0


    @api.one
    @api.depends('project_topic_id','student_ids')
    def _onchange_id_values(self):
        self.student_ids = self.project_topic_id.student_ids
        for project_topic_id in self.project_topic_id:
            if (project_topic_id.id and (self.env["project.task"].search([['id', '=', self.project_topic_id.id]]).active == True)):
                obj = self.env["project.task"].search([['id', '=', self.project_topic_id.id]])[0]
                self.student_ids = obj.student_ids
