# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class Job(models.Model):
    _name = "hr.job"
    _inherit = ["mail.alias.mixin", "hr.job"]

    @api.model
    def _default_address_id(self):
        return self.env.user.company_id.partner_id

    address_id = fields.Many2one(
        'res.partner', "Job Location", default=_default_address_id,
        help="Address where employees are working")
    application_ids = fields.One2many('hr.applicant', 'job_id', "Applications")
    application_count = fields.Integer(compute='_compute_application_count', string="Applications")
    manager_id = fields.Many2one(
        'hr.employee', related='department_id.manager_id', string="Department Manager",
        readonly=True, store=True)
    user_id = fields.Many2one('res.users', "Personal administrativo", track_visibility='onchange')
    document_ids = fields.One2many('ir.attachment', compute='_compute_document_ids', string="Applications")
    documents_count = fields.Integer(compute='_compute_document_ids', string="Documentos")
    alias_id = fields.Many2one(
        'mail.alias', "Alias", ondelete="restrict", required=True,
        help="Email alias for this job position. New emails will automatically create new applicants for this job position.")
    color = fields.Integer("Color Index")
    jefe_department_id = fields.Many2one('res.users', "Jefe de Departamento", track_visibility='onchange')
    coordinador_department_id = fields.Many2one('res.users', "Coordinador de Departamento", track_visibility='onchange')
    #topic = fields.One2many('project.task', 'depart_ids', string='Temas')

    @api.multi
    def activate_sample_project(self):
        value_domain = [('id', '=', self.env.user.department_id.id)]
        if self.env.uid == 1:
            value_domain = [] 
        return {
            'name': _('Departamentos'),
            'view_type': 'form',
            'view_mode': 'kanban,form',
            'res_model': 'hr.job',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': value_domain,
#            'domain': [('id', 'in', [x.id for x in self.invoice_ids])],
        }
        
    #@api.model
    #def activate_sample_project(self):
    #    action_data = 1
    #    return action_data

    def _compute_document_ids(self):
        applicants = self.mapped('application_ids').filtered(lambda self: not self.emp_id)
        app_to_job = dict((applicant.id, applicant.job_id.id) for applicant in applicants)
        attachments = self.env['ir.attachment'].search([
            '|',
            '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'hr.applicant'), ('res_id', 'in', applicants.ids)])
        result = dict.fromkeys(self.ids, self.env['ir.attachment'])
        for attachment in attachments:
            if attachment.res_model == 'hr.applicant':
                result[app_to_job[attachment.res_id]] |= attachment
            else:
                result[attachment.res_id] |= attachment

        for job in self:
            job.document_ids = result[job.id]
            job.documents_count = len(job.document_ids)

    @api.multi
    def _compute_application_count(self):
        read_group_result = self.env['hr.applicant'].read_group([('job_id', '=', self.id)], ['job_id'], ['job_id'])
        result = dict((data['job_id'][0], data['job_id_count']) for data in read_group_result)
        for job in self:
            job.application_count = result.get(job.id, 0)

    def get_alias_model_name(self, vals):
        return 'hr.applicant'

    def get_alias_values(self):
        values = super(Job, self).get_alias_values()
        values['alias_defaults'] = {'job_id': self.id}
        return values

    @api.model
    def create(self, vals):
        return super(Job, self.with_context(mail_create_nolog=True)).create(vals)

    @api.multi
    def _track_subtype(self, init_values):
        if 'state' in init_values and self.state == 'open':
            return 'hr_recruitment.mt_job_new'
        return super(Job, self)._track_subtype(init_values)

    @api.multi
    def action_get_attachment_tree_view(self):
        action = self.env.ref('base.action_attachment').read()[0]
        action['context'] = {
            'default_res_model': self._name,
            'default_res_id': self.ids[0]
        }
        action['search_view_id'] = (self.env.ref('hr_recruitment.ir_attachment_view_search_inherit_hr_recruitment').id, )
        action['domain'] = ['|', '&', ('res_model', '=', 'hr.job'), ('res_id', 'in', self.ids), '&', ('res_model', '=', 'hr.applicant'), ('res_id', 'in', self.mapped('application_ids').ids)]
        return action

    @api.multi
    def action_set_no_of_recruitment(self, value):
        return self.write({'no_of_recruitment': value})

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}
