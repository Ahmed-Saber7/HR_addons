# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, AccessError, ValidationError


class LeaveType(models.Model):
    _inherit = 'hr.leave'

    if_alternative_employee = fields.Boolean(string="If Alternative Employee ?",
                                             related="holiday_status_id.alternative_employee")

    take_one_time = fields.Boolean(related="holiday_status_id.take_one_time")

    alternative_employee = fields.Many2one(comodel_name="hr.employee", string="Alternative Employee", required=False, )

    add_off_days = fields.Boolean(string="", default=False)
    actual_request_date_from = fields.Date(string="Actual Date From", required=False, )
    actual_request_date_to = fields.Date(string="Actual Date To", required=False, )

    @api.constrains('holiday_status_id', 'take_one_time')
    def _check_type_choosed_before(self):
        leave_obj = self.env['hr.leave'].search([])
        for record in self:
            max_days = record.holiday_status_id.max_days
            if record.take_one_time == True:
                leave = leave_obj.search(
                    [('employee_id', '=', self.employee_id.id),
                     ('id', '!=', record.id)])
                if leave:
                    raise ValidationError(_('you have already take this Type Of Leave before ..!'))
            if record.number_of_days > max_days and max_days > 0:
                raise ValidationError(
                    _('Error . It is not allowed to exceed the permitted number of days [%s] for this type of leave..!' % max_days))

    @api.onchange('add_off_days', 'request_date_to', 'request_date_from')
    def _check_add_off_days(self):
        if self.add_off_days == True and self.request_date_from and self.request_date_to:
            num_days = self.request_date_to - self.request_date_from
            num_days = num_days.days + 1
            self.number_of_days = num_days
            self.number_of_days_display = num_days
        else:
            return
