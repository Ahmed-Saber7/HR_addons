# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class LeaveTypeInherit(models.Model):
    _inherit = 'hr.leave.type'

    max_days = fields.Integer(string="Maximum Days", required=False, )

    gender = fields.Selection(string="Gender", selection=[('male', 'Male'), ('female', 'Female'), ], required=False, )

    religion = fields.Selection(string="Religion",
                                selection=[('muslim', 'Muslim'), ('christian', 'Christian'), ('jewish', 'Jewish'), ],
                                required=False, )

    leave_type = fields.Selection(string="", selection=[('marriage', 'Marriage Leave'), ('Hajj', 'Hajj Leave'),
                                                        ('exams', 'Exams Leave'),
                                                        ('maternity', 'Maternity leave'), ('death', 'Death Leave'),
                                                        ('divorce', 'Divorce Leave'),
                                                        ('newborn', 'Newborn Leave'), ('paid', 'Paid Leave'),
                                                        ('unpaid', 'Unpaid Leave'),
                                                        ('business_trip', 'Business Trip Leave'),
                                                        ('sick', 'Sick Leave'), ('permission', 'Permission Leave'),
                                                        ('legal', 'Legal Leave')],
                                  required=False, )

    alternative_employee = fields.Boolean(string="Alternative Employee ?", )
    take_one_time = fields.Boolean(string="Take only one time ?", )
    check_type_newborn = fields.Boolean(string="", default=False)

    child_disabled = fields.Boolean(string="Child Disabled ?", default=False)

    @api.onchange('leave_type')
    def get_leave_type(self):
        if self.leave_type == 'newborn':
            self.check_type_newborn = True
        else:
            self.check_type_newborn = False
