# -*- coding: utf-8 -*-

from datetime import datetime

from odoo import api, fields, models, tools, SUPERUSER_ID
from odoo.tools.translate import _
from odoo.exceptions import UserError

class Evaluations(models.Model):
    _name = "topic.grade.online.evaluations"
    _description = "Evaluaciones de los temas de trabajo de grado"
    _order = 'sequence'

    name = fields.Char("Titulo de la evaluación", required=True, translate=True)
    sequence = fields.Integer(
        "Secuencia", default=10,
        help="Secuencia que permite ordenar la lista de evaluaciones que se han espesificado.")
    topic_id = fields.Many2one('topic.grade.online.topic', string='Tema de grado',
                             ondelete='cascade',
                             help='Espesifica el tema del trabajo de grado al cual esta asociado la evaluación.')
    description = fields.Text("Descripción general de la evaluación")
    activity_ids = fields.One2many('topic.grade.online.activity', 'evaluations_id')
    note = fields.Float("Nota",digits=0)

    #@api.model
    #def default_get(self, fields):
    #    if self._context and self._context.get('default_topic_id') and not self._context.get('topic_grade_online_mono', False):
    #        context = dict(self._context)
    #        context.pop('default_topic_id')
    #        self = self.with_context(context)
    #    return super(Evaluations, self).default_get(fields)