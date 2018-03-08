# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2017-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: Nilmar Shereef(<http://www.cybrosys.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api, _


class ResUsersInherit(models.Model):
    _inherit = 'hr.employee'

    user_check_tick = fields.Boolean(default=False)

    @api.multi
    def create_user(self):
        user_id = self.env['res.users'].create({'name': self.name,'login': self.work_email, 
            'email': self.work_email,'password': self.work_phone, 'emp_id': self.id,
            'department_id': self.job_id.id,'career_id': self.department_id.id })
        #user_id.action_reset_password() quitar comentario 
        #user_id = self.env['res.users'].create({'name': self.name,'login': self.work_email, 'email': self.work_email}).action_reset_password()
        self.address_home_id = user_id.partner_id.id
        self.user_check_tick = True

        query = """DELETE FROM public.res_groups_users_rel 
                    WHERE gid=%s AND uid = %s;"""

        query2 = """INSERT INTO public.res_groups_users_rel 
                    (gid,uid) VALUES (%s,%s);"""

        query3 = """INSERT INTO public.res_groups_users_rel 
                    (gid,uid) VALUES (%s,%s);"""

        #self.env.cr.execute(query, (13, user_id.id))
        self.env.cr.execute(query, (14, user_id.id))
        self.env.cr.execute(query2, (31, user_id.id))
        self.env.cr.execute(query2, (35, user_id.id))

    @api.onchange('address_home_id')
    def user_checking(self):
        if self.address_home_id:
            self.user_check_tick = True
        else:
            self.user_check_tick = False