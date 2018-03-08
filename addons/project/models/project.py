# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details

from lxml import etree

from email.utils import formataddr
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools.safe_eval import safe_eval

class MessagePostShowAll(models.Model):

    """With this object you can add an extensive log in your model like the
    traditional message log don't does
    You need do it the following way:
        _name = "account.invoice"
        _inherit = ['account.invoice', 'message.post.show.all']
    """

    _name = 'message.post.show.all'
    _inherit = ['mail.thread']

    # pylint: disable=W0622
    @api.model
    def get_last_value(self, ids, model=None, field=None,
                       fieldtype=None):
        """Return the last value of a record in the model to show a post with the
        change
        @param ids: int with id record
        @param model: String with model name
        @param field: Name field to return his value
        return the value of the field
        """

        field = ids and field or []
        model_obj = self.env[model]
        model_brw = model_obj.browse(ids)
        if 'many2one' in fieldtype:
            value = field and model_brw[field] and \
                model_brw[field].name_get() or ''
            value = value and value[0][1]
        elif 'many2many' in fieldtype:
            value = [i.id for i in model_brw[field]]
        else:
            value = field and model_brw[field] or ''

        return field and value or ''

    @api.model
    def prepare_many_info(self, ids, records, string, n_obj,
                          last=None):
        info = {
            0: _('Created New Line'),
            1: _('Updated Line'),
            2: _('Removed Line'),
            3: _('Removed Line'),
            6: _('many2many'),
        }
        message = '<ul>'
        obj = self.env[n_obj]
        r_name = obj._rec_name
        mes = ''
        last = last or []
        for val in records:
            if val and info.get(val[0], False):
                if val[0] == 0:
                    value = val[2]
                    message = '%s\n<li><b>%s<b>: %s</li>' % \
                        (self.get_encode_value(message),
                         self.get_encode_value(info.get(val[0])),
                         self.get_encode_value(value.get(r_name)))
                elif val[0] in (2, 3):
                    model_brw = obj.browse(val[1])
                    last_value = model_brw.name_get()
                    last_value = last_value and last_value[0][1]
                    value = val[1]
                    message = '%s\n<li><b>%s<b>: %s</li>' % \
                        (self.get_encode_value(message),
                         self.get_encode_value(info.get(val[0])),
                         self.get_encode_value(last_value))

                elif val[0] == 6:
                    lastv = list(set(val[2]) - set(last))
                    new = list(set(last) - set(val[2]))
                    add = _('Agregado')
                    delete = _('Eliminado')
                    if lastv and not new:
                        dele = [obj.browse(i).name_get()[0][1]
                                for i in lastv]
                        mes = ' - '.join(dele)
                        message = '%s\n<li><b>%s %s<b>: %s</li>' % \
                            (self.get_encode_value(message),
                             self.get_encode_value(add),
                             self.get_encode_value(string),
                             self.get_encode_value(mes))
                    if not lastv and new:

                        dele = [obj.browse(i).name_get()[0][1] for i in new]
                        mes = '-'.join(dele)
                        message = '%s\n<li><b>%s %s<b>: %s</li>' % \
                            (self.get_encode_value(message),
                             self.get_encode_value(delete),
                             self.get_encode_value(string),
                             self.get_encode_value(mes))

                elif val[0] == 1:
                    vals = val[2]
                    id_line = 0
                    for field in vals:
                        if obj._fields[field].type in \
                                ('one2many', 'many2many'):
                            is_many = obj._fields[field].type == 'many2many'

                            last_value = is_many and self.get_last_value(
                                val[1], n_obj, field, 'many2many')
                            field_str = self.get_string_by_field(obj, field)
                            new_n_obj = obj._fields[field].comodel_name
                            mes = self.prepare_many_info(val[1],
                                                         vals[field],
                                                         field_str,
                                                         new_n_obj,
                                                         last_value)

                        elif obj._fields[field].type == 'many2one':
                            mes = self.prepare_many2one_info(val[1],
                                                             n_obj,
                                                             field,
                                                             vals)

                        elif 'many' not in obj._fields[field].type:
                            mes = self.prepare_simple_info(val[1],
                                                           n_obj, field,
                                                           vals)
                        if mes and mes != '<p>':
                            message = id_line != val[1] and \
                                _('%s\n<h3>Line %s</h3>' % (message, val[1])) \
                                or message
                            message = '%s\n%s' % \
                                (self.get_encode_value(message),
                                 mes)
                            id_line = val[1]

        message = '%s\n</ul>' % self.get_encode_value(message)
        return message

    @api.model
    def get_selection_value(self, source_obj, field, value):
        """Get the string of a selection field using
        fields_get method to get the string
        @param source_obj: Model that contains the field
        @type source_obj: RecordSet
        @param field: Database name of the field
        @type field: str or unicode
        @param value: Database value used to find its the
                      string in the selection
        @type value: str or unicode
        @returns: String shown in the selection field
        @rtype: str
        """
        val = source_obj.fields_get([field])
        val = val and val.get(field, {})
        val = val and val.get('selection', ()) or ()
        val = [i[1] for i in val if value in i]
        val = val and val[0] or ''
        return val.encode('utf-8', 'ignore')

    @api.model
    def get_string_by_field(self, source_obj, field):
        """Get the string of a field using fields_get method to
        get the string depending of the user lang
        @param source_obj: Model that contains the field
        @type source_obj: RecordSet
        @param field: Database name of the field
        @type field: str or unicode
        @returns: String of the field shown in the views
        @rtype: str
        """
        description = source_obj.fields_get([field])
        description = description and description.get(field, {})
        description = description and description.get('string', '') or ''
        return description.encode('utf-8', 'ignore')

    @api.model
    def prepare_many2one_info(self, ids, n_obj, field, vals):
        obj = self.env[n_obj]
        message = '<p>'

        last_value = self.get_last_value(
            ids, obj._name, field, obj._fields[field].type)
        model_obj = self.env[obj._fields[field].comodel_name]
        model_brw = model_obj.browse(vals[field])
        new_value = model_brw.name_get()
        new_value = new_value and new_value[0][1]

        if not (last_value == new_value) and any((new_value, last_value)):
            message = '<li><b>%s<b>: %s → %s</li>' % \
                (self.get_string_by_field(obj, field),
                 self.get_encode_value(last_value),
                 self.get_encode_value(new_value))
        return message

    @staticmethod
    def get_encode_value(value):
        """Encode string values to avoid unicode errors
        @param value: Any object to try encode the value
        @type value: str bool date
        """
        val = value
        if isinstance(value, (unicode)):
            val = value.encode('utf-8', 'ignore')
        return val

    @api.model
    def prepare_simple_info(self, ids, n_obj, field,
                            vals):
        obj = self.env[n_obj]
        message = '<p>'
        last_value = self.get_last_value(
            ids, obj._name, field, obj._fields[field].type)

        last_value = obj._fields[field].type == 'selection' and \
            self.get_selection_value(obj, field, last_value) or last_value
        new_value = obj._fields[field].type == 'selection' and \
            self.get_selection_value(obj, field, vals[field]) or vals[field]
        last_value = self.get_encode_value(last_value)
        new_value = self.get_encode_value(new_value)

        message = ((last_value != new_value) and
                   any((last_value, vals[field]))) and \
            '<li><b>%s<b>: %s → %s</li>' % \
            (self.get_string_by_field(obj, field), last_value,
             new_value) or '<p>'
        return message

    # pylint: disable=W0106
    @api.multi
    def write(self, vals):
        for idx in self:
            body = '<ul>'
            message = ''
            for field in vals:
                if self._fields[field].type in ('one2many', 'many2many'):
                    is_many = self._fields[field].type == 'many2many'

                    last_value = is_many and self.get_last_value(
                        idx.id, self._name, field, 'many2many')
                    field_str = self.get_string_by_field(self, field)
                    n_obj = self._fields[field].comodel_name
                    message = self.prepare_many_info(
                        idx.id, vals[field], field_str, n_obj,
                        last_value)
                    body = len(message.split('\n')) > 2 and '%s\n%s: %s' % (
                        body, field_str, message) or body

                elif self._fields[field].type == 'many2one':
                    message = self.prepare_many2one_info(idx.id,
                                                         self._name,
                                                         field,
                                                         vals)
                    body = '%s\n%s' % (body, message)

                elif 'many' not in self._fields[field].type:
                    #message = self.prepare_simple_info(
                    #    idx.id, self._name, field, vals)
                    #body = '%s\n%s' % (body, message)
                    lis_info = ''

            body = body and '%s\n</ul>' % body
            if body and message:
                idx.message_post(body, _('Cambios en los campos'))
        res = super(MessagePostShowAll, self).write(vals)
        return res

class ProjectTaskType(models.Model):
    _name = 'project.task.type'
    _description = 'Task Stage'
    _order = 'sequence, id'

    def _get_mail_template_id_domain(self):
        return [('model', '=', 'project.task')]

    def _get_default_project_ids(self):
        default_project_id = self.env.context.get('default_project_id')
        return [default_project_id] if default_project_id else None

    name = fields.Char(string='Stage Name', required=True, translate=True)
    description = fields.Text(translate=True)
    sequence = fields.Integer(default=1)
    project_ids = fields.Many2many('project.project', 'project_task_type_rel', 'type_id', 'project_id', string='Projects',
        default=_get_default_project_ids)
    legend_priority = fields.Char(
        string='Priority Management Explanation', translate=True,
        help='Explanation text to help users using the star and priority mechanism on stages or issues that are in this stage.')
    legend_blocked = fields.Char(
        string='Kanban Blocked Explanation', translate=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the task or issue is in that stage.')
    legend_done = fields.Char(
        string='Kanban Valid Explanation', translate=True,
        help='Override the default value displayed for the done state for kanban selection, when the task or issue is in that stage.')
    legend_normal = fields.Char(
        string='Kanban Ongoing Explanation', translate=True,
        help='Override the default value displayed for the normal state for kanban selection, when the task or issue is in that stage.')
    mail_template_id = fields.Many2one(
        'mail.template',
        string='Email Template',
        domain=lambda self: self._get_mail_template_id_domain(),
        help="If set an email will be sent to the customer when the task or issue reaches this step.")
    fold = fields.Boolean(string='Folded in Kanban',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')


#===============================================================================
# class AccountInvoiceLineSecond(models.Model):
#     _name = "account.invoice.line.second"
#     _description = "Invoice Line"
# 
#     name = fields.Text(string='Description', required=True)
#     origin = fields.Char(string='Source Document',
#         help="Reference of the document that produced this invoice.")
#     sequence = fields.Integer(default=10,
#         help="Gives the sequence of this line when displaying the invoice.")
#     
#     price_unit = fields.Float(string='Unit Price', required=True, digits=2)
#     price_subtotal = fields.Float(string='Unit Price', required=True, digits=2)
#     price_subtotal_signed = fields.Float(string='Unit Price', required=True, digits=2)
#     discount = fields.Float(string='Discount (%)', digits=2,
#         default=0.0)
#===============================================================================
    

class Project(models.Model):
    _name = "project.project"
    _description = "Project"
    _inherit = ['mail.alias.mixin', 'mail.thread', 'ir.needaction_mixin']
    _inherits = {'account.analytic.account': "analytic_account_id"}
    _order = "sequence, name, id"
    _period_number = 5
    
    # invoice_line_ids = fields.One2many('account.invoice.line', 'name', string='Invoice Lines')
    
    # session_ids = fields.One2many(
    #    'openacademy.session', 'course_id', string="Sessions")
    
    # calificaciones = fields.One2many(
    #    'account.invoice.line.second',
    #    string='Estados',
    #    help="If set an email will be sent to the customer when the task or issue reaches this step.")
    
    # order_line = fields.One2many('sale.order.line', 'order_id', string='Order Lines', states={'cancel': [('readonly', True)], 'done': [('readonly', True)]}, copy=True)


    def get_alias_model_name(self, vals):
        return vals.get('alias_model', 'project.task')

    def get_alias_values(self):
        values = super(Project, self).get_alias_values()
        values['alias_defaults'] = {'project_id': self.id}
        return values

    @api.multi
    def show_topic_for_user(self):
        '''
        Este metodo muestra en un grid las lista de los temas de trabajo de grado que un usuario ha creado
        '''
        action = self.env.ref('project.act_project_project_2_project_task_all_2')
        result = action.read()[0]
        users_ids = self.env['hr.employee'].search([('user_id', '=', self.env.user.id)]) 
        task_ids = self.env['project.task'].search([('project_id', '=', self.id), ('student_ids', 'in', users_ids.ids)]) 
        result['domain'] = [('id', 'in', task_ids.ids)]
        return result

    @api.multi
    def unlink(self):
        analytic_accounts_to_delete = self.env['account.analytic.account']
        for project in self:
            if project.tasks:
                raise UserError(_('You cannot delete a project containing tasks. You can either delete all the project\'s tasks and then delete the project or simply deactivate the project.'))
            if project.analytic_account_id and not project.analytic_account_id.line_ids:
                analytic_accounts_to_delete |= project.analytic_account_id
        res = super(Project, self).unlink()
        analytic_accounts_to_delete.unlink()
        return res

    def _compute_attached_docs_count(self):
        Attachment = self.env['ir.attachment']
        for project in self:
            project.doc_count = Attachment.search_count([
                '|',
                '&',
                ('res_model', '=', 'project.project'), ('res_id', '=', project.id),
                '&',
                ('res_model', '=', 'project.task'), ('res_id', 'in', project.task_ids.ids)
            ])

    def _compute_task_count(self):
        for project in self:
            project.task_count = len(project.task_ids)

    def _compute_task_needaction_count(self):
        projects_data = self.env['project.task'].read_group([
            ('project_id', 'in', self.ids),
            ('message_needaction', '=', True)
        ], ['project_id'], ['project_id'])
        mapped_data = {project_data['project_id'][0]: int(project_data['project_id_count'])
                       for project_data in projects_data}
        for project in self:
            project.task_needaction_count = mapped_data.get(project.id, 0)

    @api.model
    def _get_alias_models(self):
        """ Overriden in project_issue to offer more options """
        return [('project.task', "Tasks")]

    @api.multi
    def attachment_tree_view(self):
        self.ensure_one()
        domain = [
            '|',
            '&', ('res_model', '=', 'project.project'), ('res_id', 'in', self.ids),
            '&', ('res_model', '=', 'project.task'), ('res_id', 'in', self.task_ids.ids)]
        return {
            'name': _('Attachments'),
            'domain': domain,
            'res_model': 'ir.attachment',
            'type': 'ir.actions.act_window',
            'view_id': False,
            'view_mode': 'kanban,tree,form',
            'view_type': 'form',
            'help': _('''<p class="oe_view_nocontent_create">
                        Documents are attached to the tasks and issues of your project.</p><p>
                        Send messages or log internal notes with attachments to link
                        documents to your project.
                    </p>'''),
            'limit': 80,
            'context': "{'default_res_model': '%s','default_res_id': %d}" % (self._name, self.id)
        }

    @api.model
    def activate_sample_project(self):
        """ Unarchives the sample project 'project.project_project_data' and
            reloads the project dashboard """
        # Unarchive sample project
        project = self.env.ref('project.project_project_data', False)
        if project:
            project.write({'active': True})

        cover_image = self.env.ref('project.msg_task_data_14_attach', False)
        cover_task = self.env.ref('project.project_task_data_14', False)
        if cover_image and cover_task:
            cover_task.write({'displayed_image_id': cover_image.id})

        # Change the help message on the action (no more activate project)
        action = self.env.ref('project.open_view_project_all', False)
        action_data = None
        if action:
            action.sudo().write({
                "help": _('''<p class="oe_view_nocontent_create">Click to create a new project.</p>''')
            })
            action_data = action.read()[0]
        # Reload the dashboard
        return action_data

    def _compute_is_favorite(self):
        for project in self:
            project.is_favorite = self.env.user in project.favorite_user_ids

    def _get_default_favorite_user_ids(self):
        return [(6, 0, [self.env.uid])]

    @api.model
    def default_get(self, flds):
        result = super(Project, self).default_get(flds)
        result['use_tasks'] = True
        return result

    evaluation_ids = fields.One2many(
        'project.evaluation', 'project_id', string="Lista de evaluaciones")
    
    # Lambda indirection method to avoid passing a copy of the overridable method when declaring the field
    _alias_models = lambda self: self._get_alias_models()

    active = fields.Boolean(default=True,
        help="If the active field is set to False, it will allow you to hide the project without removing it.")
    sequence = fields.Integer(default=10, help="Gives the sequence order when displaying a list of Projects.")
    analytic_account_id = fields.Many2one(
        'account.analytic.account', string='Contract/Analytic',
        help="Link this project to an analytic account if you need financial management on projects. "
             "It enables you to connect projects with budgets, planning, cost and revenue analysis, timesheets on projects, etc.",
        ondelete="cascade", required=True, auto_join=True)
    favorite_user_ids = fields.Many2many(
        'res.users', 'project_favorite_user_rel', 'project_id', 'user_id',
        default=_get_default_favorite_user_ids,
        string='Members')
    is_favorite = fields.Boolean(compute='_compute_is_favorite', string='Show Project on dashboard',
        help="Whether this project should be displayed on the dashboard or not")
    label_tasks = fields.Char(string='Use Tasks as', default='Tasks', help="Gives label to tasks on project's kanban view.")
    tasks = fields.One2many('project.task', 'project_id', string="Task Activities")
    resource_calendar_id = fields.Many2one('resource.calendar', string='Working Time',
        help="Timetable working hours to adjust the gantt diagram report")
    type_ids = fields.Many2many('project.task.type', 'project_task_type_rel', 'project_id', 'type_id', string='Tasks Stages')
    task_count = fields.Integer(compute='_compute_task_count', string="Tasks")
    task_needaction_count = fields.Integer(compute='_compute_task_needaction_count', string="Tasks")
    task_ids = fields.One2many('project.task', 'project_id', string='Tasks',
                               domain=['|', ('stage_id.fold', '=', False), ('stage_id', '=', False)])
    color = fields.Integer(string='Color Index')
    user_id = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user)
    user_ids_many = fields.Many2one('res.users', string='Project Manager', default=lambda self: self.env.user)
    alias_id = fields.Many2one('mail.alias', string='Alias', ondelete="restrict", required=True,
        help="Internal email associated with this project. Incoming emails are automatically synchronized "
             "with Tasks (or optionally Issues if the Issue Tracker module is installed).")
    alias_model = fields.Selection(_alias_models, string="Alias Model", index=True, required=True, default='project.task',
        help="The kind of document created when an email is received on this project's email alias")
    privacy_visibility = fields.Selection([
            ('followers', _('On invitation only')),
            ('employees', _('Visible by all employees')),
            ('portal', _('Visible by following customers')),
        ],
        string='Privacy', required=True,
        default='employees',
        help="Holds visibility of the tasks or issues that belong to the current project:\n"
                "- On invitation only: Employees may only see the followed project, tasks or issues\n"
                "- Visible by all employees: Employees may see all project, tasks or issues\n"
                "- Visible by following customers: employees see everything;\n"
                "   if website is activated, portal users may see project, tasks or issues followed by\n"
                "   them or by someone of their company\n")
    doc_count = fields.Integer(compute='_compute_attached_docs_count', string="Number of documents attached")
    date_start = fields.Date(string='Start Date')
    date = fields.Date(string='Expiration Date', index=True, track_visibility='onchange')

    _sql_constraints = [
        ('project_date_greater', 'check(date >= date_start)', 'Error! project start-date must be lower than project end-date.')
    ]


    @api.multi
    def map_tasks(self, new_project_id):
        """ copy and map tasks from old to new project """
        tasks = self.env['project.task']
        for task in self.tasks:
            # preserve task name and stage, normally altered during copy
            defaults = {'stage_id': task.stage_id.id,
                        'name': task.name}
            tasks += task.copy(defaults)
        return self.browse(new_project_id).write({'tasks': [(6, 0, tasks.ids)]})

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        self = self.with_context(active_test=False)
        if not default.get('name'):
            default['name'] = _("%s (copia)") % (self.name)
        project = super(Project, self).copy(default)
        for follower in self.message_follower_ids:
            project.message_subscribe(partner_ids=follower.partner_id.ids, subtype_ids=follower.subtype_ids.ids)
        self.map_tasks(project.id)
        return project

    @api.model
    def create(self, vals):
        ir_values = self.env['ir.values'].get_default('project.config.settings', 'generate_project_alias')
        if ir_values:
            vals['alias_name'] = vals.get('alias_name') or vals.get('name')
        # Prevent double project creation when 'use_tasks' is checked
        self = self.with_context(project_creation_in_progress=True, mail_create_nosubscribe=True)
        return super(Project, self).create(vals)

    @api.multi
    def write(self, vals):
        # if alias_model has been changed, update alias_model_id accordingly
        if vals.get('alias_model'):
            vals['alias_model_id'] = self.env['ir.model'].search([
                ('model', '=', vals.get('alias_model', 'project.task'))
            ], limit=1).id
        res = super(Project, self).write(vals)
        if 'active' in vals:
            # archiving/unarchiving a project does it on its tasks, too
            self.with_context(active_test=False).mapped('tasks').write({'active': vals['active']})
        return res

    @api.multi
    def toggle_favorite(self):
        favorite_projects = not_fav_projects = self.env['project.project'].sudo()
        for project in self:
            if self.env.user in project.favorite_user_ids:
                favorite_projects |= project
            else:
                not_fav_projects |= project

        # Project User has no write access for project.
        not_fav_projects.write({'favorite_user_ids': [(4, self.env.uid)]})
        favorite_projects.write({'favorite_user_ids': [(3, self.env.uid)]})

    @api.multi
    def close_dialog(self):
        return {'type': 'ir.actions.act_window_close'}

class employeeTask(models.Model):
    _inherit = "hr.employee"
    
    employee_ids = fields.Many2many('project.task', 'employee_task_rel', 'task_id', 'emp_id', string='Employees')
    # task_ids = fields.Many2one('project.task', string='Task')

class Task(models.Model):
    _name = "project.task"
    _description = "Task"
    _date_name = "date_start"
    _inherit = ['message.post.show.all', 'ir.needaction_mixin']
    _mail_post_access = 'read'
    _order = "priority desc, sequence, date_start, name, id"
    
    # recipient_ids = fields.Many2many('hr.employee', string='Integrantes')
    
    student_ids = fields.Many2many('hr.employee', 'student_lead_tag_rel_res', 'student_lead_id_res', 'student_tag_id_res', string='integrante', help="Agregar los integrantes al grupo", track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string='Carrera', default=lambda self: self.env['res.users'].sudo().browse(self.env.uid).career_id)
    depart_ids = fields.Many2one('hr.job', string='Departamento', default=lambda self: self.env['res.users'].sudo().browse(self.env.uid).department_id)
    jefe_department_id = fields.Many2one('res.users', "Jefe de Departamento", track_visibility='onchange')
    description_general = fields.Text("Descripción", track_visibility='onchange')
    # recipient_ids = fields.One2many('hr.employee', 'task_ids', string='Integrantes')

#    @api.onchange('student_ids')
    def _students(self):
        values = {
            'website_published': True,
            'message_type': 'notification',
            'no_auto_thread': False,
            'record_name': self.name,
            'model':'project.task',
            'subtype_id': 2,
            'parent_id': 1608,
            'res_id': 76, 
        }
        message_id = self.env['mail.message'].create(values)

        vals = {
            'new_value_text': 'valor prueba',
            'write_id': self.env.uid,
            'field':'student_ids',
            'field_type':'text',
            'old_value_text': 'valor viejo',
            'field_desc': 'Integrantes',
            'mail_message_id': message_id.id,
        }
        tracking = self.env['mail.tracking.value'].create(vals)
        #raise UserError(_('Ya tiene un tema en proceso de inscripción.'))

    @api.multi
    def filter_kanban_topic_project(self):
        value_domain = ['|',('user_id_asignado.id','=',self.env.uid),'|',
            ('jefe_department_id.id','=',self.env.uid),'|',
            ('student_ids.id', '=', self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).emp_id),
            ('create_uid','=',self.env.uid)]
        #[('id', '=', self.env.user.emp_id)]
        if self.env.uid == 1:
            value_domain = [] 
        return {
            'name': _('Temas'),
            'view_type': 'form',
            'view_mode': 'kanban,tree,form,calendar,pivot,graph',
            'res_model': 'project.task',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': value_domain,
#           'domain': [('student_ids.id', '=', 53)] or [('docente_director_id.id','=',1)] and [],
#           'domain': [('create_uid', 'in', [x.id for x in self.student_ids])],
        }
    
    
    @api.multi
    def name_get(self):
        res = []
        for record in self:
            name = (record.name[:75] + '...') if len(record.name) > 75 else record.name
            res.append((record.id, name))
        return res

    @api.multi
    def action_step_one(self):
        topic_member = self.env['project.task'].search([('stage_id', '>', 18),('active', '=', True)])
        for project in topic_member:
            for member in project.student_ids:
                if member.id == self.env['res.users'].search([('id', '=', self.env.uid)],limit=1).emp_id:
                    raise UserError(_('Ya perteneces a un grupo que tiene un tema en proceso de inscripción.'))
        topic_active = self.env['project.task'].search([('create_uid', '=', self.env.user.id),('stage_id', '>', 18),('active', '=', True)])
        for projects in topic_active:
            raise UserError(_('Ya tiene un tema en proceso de inscripción.'))
        self.write({'stage_id': '19'})
 
    @api.multi
    def action_step_two(self):
        self.write({'stage_id': '20'})

    @api.multi
    def action_step_three(self):
        self.write({'stage_id': '21'})
 
    @api.multi
    def action_step_four(self):
        self.write({'stage_id': '22'})

    @api.multi
    def action_step_five(self):
        self.write({'stage_id': '23'})
 
    @api.multi
    def action_refuse(self):
        self.write({'stage_id': '24'})

    @api.multi
    def action_inscri(self):
        topic_grade_online = self.env['topic.grade.online.topic'].create({
            'name': self.name,
            'department_id': self.depart_ids.id,
            'carrera_id': self.department_id.id,
            'coordinador_department_id': self.user_id_coordi.id,
            'docente_director_id': self.user_id_asignado.id,
            'jefe_department_id': self.jefe_department_id.id,
            'eraise_topic_ids': self.id,
            'project_topic_id': self.id,
            'create_uid':1
        }) 
        self.write({'stage_id': '24'})
        topic_grade_online._onchange_id_values()

    @api.multi
    def send_email(self):
        """Return a dictionary for specific email values, depending on a
        partner, or generic to the whole recipients given by mail.email_to.

            :param browse_record mail: mail.mail browse_record
            :param browse_record partner: specific recipient partner
        """
        mail = self.env['mail.mail'].create({
            'subject': self.name,
            'body_html': '<p>Test siii prueba de rendimiento</p>',
            'email_to': ','.join(formataddr((partner.name, partner.work_email)) for partner in self.env['hr.employee'].sudo().browse(self.recipient_ids.ids)),
            'recipient_ids' : self.student_ids,
            'partner_ids': '1'
        })
        mail.send()       



    @api.model
    def default_get(self, field_list):
        """ Set 'date_assign' if user_id is set. """
        result = super(Task, self).default_get(field_list)
        if 'user_id' in result:
            result['date_assign'] = fields.Datetime.now()
        return result

    def _get_default_partner(self):
        if 'default_project_id' in self.env.context:
            default_project_id = self.env['project.project'].browse(self.env.context['default_project_id'])
            return default_project_id.exists().partner_id

    def _get_default_stage_id(self):
        """ Gives default stage_id """
        project_id = self.env.context.get('default_project_id')
        if not project_id:
            return False
        return self.stage_find(project_id, [('fold', '=', False)])

    @api.model
    def _read_group_stage_ids(self, stages, domain, order):
        search_domain = [('id', 'in', stages.ids)]
        if 'default_project_id' in self.env.context:
            search_domain = ['|', ('project_ids', '=', self.env.context['default_project_id'])] + search_domain

        stage_ids = stages._search(search_domain, order=order, access_rights_uid=SUPERUSER_ID)
        return stages.browse(stage_ids)

    active = fields.Boolean(default=True, string='Habilitado', track_visibility='onchange')
    user_id_propuesto = fields.Many2one('res.users', string='Docente director propuesto', track_visibility='onchange')
    name = fields.Char(string='Tema', required=True, index=True, track_visibility='onchange')
    description = fields.Html(string='Description', track_visibility='onchange')
    priority = fields.Selection([
            ('0', 'Normal'),
            ('1', 'High')
        ], default='0', index=True)
    sequence = fields.Integer(string='Sequence', index=True, default=10,
        help="Gives the sequence order when displaying a list of tasks.")
    stage_id = fields.Many2one('project.task.type', string='Estado actual', index=True, copy=False, default=18,store=True, track_visibility='onchange')
    tag_ids = fields.Many2many('project.tags', string='Tags', oldname='categ_ids')
    kanban_state = fields.Selection([
            ('normal', 'In Progress'),
            ('done', 'Ready for next stage'),
            ('blocked', 'Blocked')
        ], string='Kanban State',
        default='normal',
        required=True, copy=False,
        help="A task's kanban state indicates special situations affecting it:\n"
             " * Normal is the default situation\n"
             " * Blocked indicates something is preventing the progress of this task\n"
             " * Ready for next stage indicates the task is ready to be pulled to the next stage")
    create_date = fields.Datetime(index=True)
    write_date = fields.Datetime(index=True)  # not displayed in the view but it might be useful with base_action_rule module (and it needs to be defined first for that)
    date_start = fields.Datetime(string='Starting Date',
    default=fields.Datetime.now,
    index=True, copy=False)
    date_end = fields.Datetime(string='Ending Date', index=True, copy=False)
    date_assign = fields.Datetime(string='Assigning Date', index=True, copy=False, readonly=True)
    date_deadline = fields.Date(string='Deadline', index=True, copy=False)
    date_last_stage_update = fields.Datetime(string='Last Stage Update',
        default=fields.Datetime.now,
        index=True,
        copy=False,
        readonly=True)
    project_id = fields.Many2one('project.project',
        string='Departamento',
        default=lambda self: self.env.context.get('default_project_id'),
        index=True,
        track_visibility='onchange',
        change_default=True)
    notes = fields.Text(string='Notes')
    planned_hours = fields.Float(string='Initially Planned Hours', help='Estimated time to do the task, usually set by the project manager when the task is in draft state.')
    remaining_hours = fields.Float(string='Remaining Hours', digits=(16, 2), help="Total remaining time, can be re-estimated periodically by the assignee of the task.")
    user_id = fields.Many2one('res.users',
        string='Creado por',
        default=lambda self: self.env.uid,
        index=True)
    user_id_asignado = fields.Many2one('res.users',
        string='Docente director designado', track_visibility='onchange')
    user_id_coordi = fields.Many2one('res.users',
        string='Coordinador de Carrera', track_visibility='onchange')
    time_grade = fields.Char(string="Tiempo probable de realizacion de trabajo de grado", track_visibility='onchange')
    partner_id = fields.Many2one('res.partner',
        string='Customer',
        default=_get_default_partner)
    manager_id = fields.Many2one('res.users', string='Project Manager', related='project_id.user_id', readonly=True)
    company_id = fields.Many2one('res.company',
        string='Company',
        default=lambda self: self.env['res.company']._company_default_get())
    color = fields.Integer(string='Color Index')
    user_email = fields.Char(related='user_id.email', string='User Email', readonly=True)
    attachment_ids = fields.One2many('ir.attachment', 'res_id', domain=lambda self: [('res_model', '=', self._name)], auto_join=True, string='Attachments')
    # In the domain of displayed_image_id, we couln't use attachment_ids because a one2many is represented as a list of commands so we used res_model & res_id
    displayed_image_id = fields.Many2one('ir.attachment', domain="[('res_model', '=', 'project.task'), ('res_id', '=', id), ('mimetype', 'ilike', 'image')]", string='Displayed Image')
    legend_blocked = fields.Char(related='stage_id.legend_blocked', string='Kanban Blocked Explanation', readonly=True)
    legend_done = fields.Char(related='stage_id.legend_done', string='Kanban Valid Explanation', readonly=True)
    legend_normal = fields.Char(related='stage_id.legend_normal', string='Kanban Ongoing Explanation', readonly=True)

    @api.onchange('project_id')
    def _onchange_project(self):
        if self.project_id:
            self.partner_id = self.project_id.partner_id
            self.stage_id = self.stage_find(self.project_id.id, [('fold', '=', False)])
        else:
            self.stage_id = False

    @api.onchange('user_id')
    def _onchange_user(self):
        if self.user_id:
            self.date_start = fields.Datetime.now()

    @api.multi
    def copy(self, default=None):
        if default is None:
            default = {}
        if not default.get('name'):
            default['name'] = _("%s (copy)") % self.name
        if 'remaining_hours' not in default:
            default['remaining_hours'] = self.planned_hours
        return super(Task, self).copy(default)

    @api.constrains('date_start', 'date_end')
    def _check_dates(self):
        if any(self.filtered(lambda task: task.date_start and task.date_end and task.date_start > task.date_end)):
            raise ValidationError(_('Error ! Task starting date must be lower than its ending date.'))

    # Override view according to the company definition
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        # read uom as admin to avoid access rights issues, e.g. for portal/share users,
        # this should be safe (no context passed to avoid side-effects)
        obj_tm = self.env.user.company_id.project_time_mode_id
        tm = obj_tm and obj_tm.name or 'Hours'

        res = super(Task, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)

        # read uom as admin to avoid access rights issues, e.g. for portal/share users,
        # this should be safe (no context passed to avoid side-effects)
        obj_tm = self.env.user.company_id.project_time_mode_id
        # using get_object to get translation value
        uom_hour = self.env.ref('product.product_uom_hour', False)
        if not obj_tm or not uom_hour or obj_tm.id == uom_hour.id:
            return res

        eview = etree.fromstring(res['arch'])

        # if the project_time_mode_id is not in hours (so in days), display it as a float field
        def _check_rec(eview):
            if eview.attrib.get('widget', '') == 'float_time':
                eview.set('widget', 'float')
            for child in eview:
                _check_rec(child)
            return True

        _check_rec(eview)

        res['arch'] = etree.tostring(eview)

        # replace reference of 'Hours' to 'Day(s)'
        for f in res['fields']:
            # TODO this NOT work in different language than english
            # the field 'Initially Planned Hours' should be replaced by 'Initially Planned Days'
            # but string 'Initially Planned Days' is not available in translation
            if 'Hours' in res['fields'][f]['string']:
                res['fields'][f]['string'] = res['fields'][f]['string'].replace('Hours', obj_tm.name)
        return res

    @api.model
    def get_empty_list_help(self, help):
        self = self.with_context(
            empty_list_help_id=self.env.context.get('default_project_id'),
            empty_list_help_model='project.project',
            empty_list_help_document_name=_("tasks")
        )
        return super(Task, self).get_empty_list_help(help)

    # ----------------------------------------
    # Case management
    # ----------------------------------------

    def stage_find(self, section_id, domain=[], order='sequence'):
        """ Override of the base.stage method
            Parameter of the stage search taken from the lead:
            - section_id: if set, stages must belong to this section or
              be a default stage; if not set, stages must be default
              stages
        """
        # collect all section_ids
        section_ids = []
        if section_id:
            section_ids.append(section_id)
        section_ids.extend(self.mapped('project_id').ids)
        search_domain = []
        if section_ids:
            search_domain = [('|')] * (len(section_ids) - 1)
            for section_id in section_ids:
                search_domain.append(('project_ids', '=', section_id))
        search_domain += list(domain)
        # perform search, return the first found
        return self.env['project.task.type'].search(search_domain, order=order, limit=1).id

    # ------------------------------------------------
    # CRUD overrides
    # ------------------------------------------------

    @api.model
    def create(self, vals):
        # context: no_log, because subtype already handle this
        context = dict(self.env.context, mail_create_nolog=True)

        # for default stage
        if vals.get('project_id') and not context.get('default_project_id'):
            context['default_project_id'] = vals.get('project_id')
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = fields.Datetime.now()
            vals['stage_id'] = 18
        task = super(Task, self.with_context(context)).create(vals)
        #update project_task set stage_id=18 where id=64;
        #query = """UPDATE public.project_task SET stage_id=%s WHERE id=%s;"""
        #self.env.cr.execute(query, (18, task.id))

        return task

    @api.multi
    def write(self, vals):
        #query = """SELECT COUNT(*) FROM res_groups_users_rel WHERE uid = %s AND gid = 35;"""
        #is_groups_students = self.env.cr.execute(query, (self.env.user.id))
        #if self.stage_id != 18 and is_groups_students = 1:
        #    raise UserError(_('Los alumnos no pueden editar '))
        now = fields.Datetime.now()
        # stage change: update date_last_stage_update
        if 'stage_id' in vals:
            vals['date_last_stage_update'] = now
            # reset kanban state when changing stage
            if 'kanban_state' not in vals:
                vals['kanban_state'] = 'normal'
        # user_id change: update date_assign
        if vals.get('user_id'):
            vals['date_assign'] = now

        result = super(Task, self).write(vals)

        return result

    # ---------------------------------------------------
    # Mail gateway
    # ---------------------------------------------------

    @api.multi
    def _track_template(self, tracking):
        res = super(Task, self)._track_template(tracking)
        test_task = self[0]
        changes, tracking_value_ids = tracking[test_task.id]
        if 'stage_id' in changes and test_task.stage_id.mail_template_id:
            res['stage_id'] = (test_task.stage_id.mail_template_id, {'composition_mode': 'mass_mail'})
        return res

    @api.multi
    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'kanban_state' in init_values and self.kanban_state == 'blocked':
            return 'project.mt_task_blocked'
        elif 'kanban_state' in init_values and self.kanban_state == 'done':
            return 'project.mt_task_ready'
        elif 'user_id' in init_values and self.name:  # assigned -> new
            return 'project.mt_task_new'
        elif 'stage_id' in init_values and self.stage_id and self.stage_id.sequence <= 1:  # start stage -> new
            return 'project.mt_task_new'
        elif 'stage_id' in init_values:
            return 'project.mt_task_stage'
        return super(Task, self)._track_subtype(init_values)

    @api.multi
    def _notification_recipients(self, message, groups):
        """ Handle project users and managers recipients that can convert assign
        tasks and create new one directly from notification emails. """
        groups = super(Task, self)._notification_recipients(message, groups)

        self.ensure_one()
        if not self.user_id:
            take_action = self._notification_link_helper('assign')
            project_actions = [{'url': take_action, 'title': _('I take it')}]
        else:
            new_action_id = self.env.ref('project.action_view_task').id
            new_action = self._notification_link_helper('new', action_id=new_action_id)
            project_actions = [{'url': new_action, 'title': _('New Task')}]

        new_group = (
            'group_project_user', lambda partner: bool(partner.user_ids) and any(user.has_group('project.group_project_user') for user in partner.user_ids), {
                'actions': project_actions,
            })

        return [new_group] + groups

    @api.model
    def message_get_reply_to(self, res_ids, default=None):
        """ Override to get the reply_to of the parent project. """
        tasks = self.sudo().browse(res_ids)
        project_ids = tasks.mapped('project_id').ids
        aliases = self.env['project.project'].message_get_reply_to(project_ids, default=default)
        return {task.id: aliases.get(task.project_id.id, False) for task in tasks}

    @api.multi
    def email_split(self, msg):
        email_list = tools.email_split((msg.get('to') or '') + ',' + (msg.get('cc') or ''))
        # check left-part is not already an alias
        aliases = self.mapped('project_id.alias_name')
        return filter(lambda x: x.split('@')[0] not in aliases, email_list)

    @api.model
    def message_new(self, msg, custom_values=None):
        """ Override to updates the document according to the email. """
        if custom_values is None:
            custom_values = {}
        defaults = {
            'name': msg.get('subject'),
            'planned_hours': 0.0,
            'partner_id': msg.get('author_id')
        }
        defaults.update(custom_values)

        res = super(Task, self).message_new(msg, custom_values=defaults)
        task = self.browse(res)
        email_list = task.email_split(msg)
        partner_ids = filter(None, task._find_partner_from_emails(email_list, force_create=False))
        task.message_subscribe(partner_ids)
        return res

    @api.multi
    def message_update(self, msg, update_vals=None):
        """ Override to update the task according to the email. """
        if update_vals is None:
            update_vals = {}
        maps = {
            'cost': 'planned_hours',
        }
        for line in msg['body'].split('\n'):
            line = line.strip()
            res = tools.command_re.match(line)
            if res:
                match = res.group(1).lower()
                field = maps.get(match)
                if field:
                    try:
                        update_vals[field] = float(res.group(2).lower())
                    except (ValueError, TypeError):
                        pass

        email_list = self.email_split(msg)
        partner_ids = filter(None, self._find_partner_from_emails(email_list, force_create=False))
        self.message_subscribe(partner_ids)
        return super(Task, self).message_update(msg, update_vals=update_vals)

    @api.multi
    def message_get_suggested_recipients(self):
        recipients = super(Task, self).message_get_suggested_recipients()
        for task in self.filtered('partner_id'):
            reason = _('Customer Email') if task.partner_id.email else _('Customer')
            task._message_add_suggested_recipient(recipients, partner=task.partner_id, reason=reason)
        return recipients

    @api.multi
    def message_get_email_values(self, notif_mail=None):
        res = super(Task, self).message_get_email_values(notif_mail=notif_mail)
        headers = {}
        if res.get('headers'):
            try:
                headers.update(safe_eval(res['headers']))
            except Exception:
                pass
        if self.project_id:
            current_objects = filter(None, headers.get('X-Odoo-Objects', '').split(','))
            current_objects.insert(0, 'project.project-%s, ' % self.project_id.id)
            headers['X-Odoo-Objects'] = ','.join(current_objects)
        if self.tag_ids:
            headers['X-Odoo-Tags'] = ','.join(self.tag_ids.mapped('name'))
        res['headers'] = repr(headers)
        return res


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'
    _description = 'Analytic Account'

    use_tasks = fields.Boolean(string='Use Tasks', help="Check this box to manage internal activities through this project")
    company_uom_id = fields.Many2one('product.uom', related='company_id.project_time_mode_id', string="Company UOM")
    project_ids = fields.One2many('project.project', 'analytic_account_id', string='Projects')
    project_count = fields.Integer(compute='_compute_project_count', string='Project Count')

    def _compute_project_count(self):
        for account in self:
            account.project_count = len(account.with_context(active_test=False).project_ids)

    @api.model
    def _trigger_project_creation(self, vals):
        '''
        This function is used to decide if a project needs to be automatically created or not when an analytic account is created. It returns True if it needs to be so, False otherwise.
        '''
        return vals.get('use_tasks') and 'project_creation_in_progress' not in self.env.context

    @api.multi
    def project_create(self, vals):
        '''
        This function is called at the time of analytic account creation and is used to create a project automatically linked to it if the conditions are meet.
        '''
        self.ensure_one()
        Project = self.env['project.project']
        project = Project.with_context(active_test=False).search([('analytic_account_id', '=', self.id)])
        if not project and self._trigger_project_creation(vals):
            project_values = {
                'name': vals.get('name'),
                'analytic_account_id': self.id,
                'use_tasks': True,
            }
            return Project.create(project_values).id
        return False

    @api.model
    def create(self, vals):
        analytic_account = super(AccountAnalyticAccount, self).create(vals)
        analytic_account.project_create(vals)
        return analytic_account

    @api.multi
    def write(self, vals):
        vals_for_project = vals.copy()
        for account in self:
            if not vals.get('name'):
                vals_for_project['name'] = account.name
            account.project_create(vals_for_project)
        return super(AccountAnalyticAccount, self).write(vals)

    @api.multi
    def unlink(self):
        projects = self.env['project.project'].search([('analytic_account_id', 'in', self.ids)])
        has_tasks = self.env['project.task'].search_count([('project_id', 'in', projects.ids)])
        if has_tasks:
            raise UserError(_('Please remove existing tasks in the project linked to the accounts you want to delete.'))
        return super(AccountAnalyticAccount, self).unlink()

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        if args is None:
            args = []
        if self.env.context.get('current_model') == 'project.project':
            return self.search(args + [('name', operator, name)], limit=limit).name_get()

        return super(AccountAnalyticAccount, self).name_search(name, args=args, operator=operator, limit=limit)

    @api.multi
    def projects_action(self):
        projects = self.with_context(active_test=False).mapped('project_ids')
        result = {
            "type": "ir.actions.act_window",
            "res_model": "project.project",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [["id", "in", projects.ids]],
            "context": {"create": False},
            "name": "Projects",
        }
        if len(projects) == 1:
            result['views'] = [(False, "form")]
            result['res_id'] = projects.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

class ProjectTags(models.Model):
    """ Tags of project's tasks (or issues) """
    _name = "project.tags"
    _description = "Tags of project's tasks, issues..."

    name = fields.Char(required=True)
    color = fields.Integer(string='Color Index')

    _sql_constraints = [
        ('name_uniq', 'unique (name)', "Tag name already exists !"),
    ]


class ProjectEvaluation(models.Model):
    """ Tags of project's tasks (or issues) """
    _name = "project.evaluation"
    _description = "Las evaluaciones de los projectos."

    name = fields.Char(required=True)
    # nota = fields.Char(string='Notas')
    
    project_id = fields.Many2one('project.project',
        ondelete='cascade', string="Projecto")
    
class TaskEvaluation(models.Model):
    """ Tags of project's tasks (or issues) """
    _name = "project.task.evaluation"
    _description = "Relacion de tareas a evaluaciones."

    name = fields.Char(required=True)
    # nota = fields.Char(string='Notas')
    
    project_id = fields.Many2one('project.project',
        ondelete='cascade', string="Projecto")

