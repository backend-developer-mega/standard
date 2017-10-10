# -*- coding: utf-8 -*-

from datetime import timedelta
from openerp import models, fields, api, exceptions

class Course(models.Model):
    _name = 'openacademy.course'
    
    name = fields.Char(string="Title", required=True)

    session_ids = fields.One2many(
        'openacademy.session', 'course_id', string="Lista de evaluaciones")
    
    alumnos_ids = fields.One2many(
        'openacademy.alumno', 'course_id', string="Lista de alumnos")


class Session(models.Model):
    _name = 'openacademy.session'

    name = fields.Char(string="Title", required=True)
    lastname = fields.Char(string="lastname")

    course_id = fields.Many2one('openacademy.course',
        ondelete='cascade', string="Projecto", required=True)
    
    nota = fields.Char(string='Nota')


class Alumno(models.Model):
    _name = 'openacademy.alumno'

    fullname = fields.Char(string="Nombre", required=True)

    course_id = fields.Many2one('openacademy.course',
        ondelete='cascade', string="Projecto")

    #session_ids = fields.One2many(
    #    'openacademy.session', 'course_id', string="Lista de evaluaciones",
    #    domain=[('category_id.name', 'ilike', "Teacher")])

    session_ids = fields.One2many(
        'openacademy.alumno.evaluaciones', 'alumno_id', string="Lista de alumnos")
    
    
class AlumnoEvaluaciones(models.Model):
    _name = 'openacademy.alumno.evaluaciones'
    
    alumno_id = fields.Many2one('openacademy.alumno', string="Alumno")
    
    session_id = fields.Many2one('openacademy.session', string="evaluaciones")
    
    nota = fields.Char(string="Nota")
    
    