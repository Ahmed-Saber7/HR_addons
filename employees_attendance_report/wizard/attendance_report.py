# -*- coding: utf-8 -*-

from odoo import api, fields, models


class EmployeesAttendanceReportWizard(models.TransientModel):
    _name = "employees.attendance.report"
    _description = "Employees Attendance Report wizard"

    report_language = fields.Selection([
        ('en', 'English'),
        ('ar', 'Arabic'),
    ], string='Language', default='en', required=True)

    date_from = fields.Datetime(required=True)
    date_to = fields.Datetime(required=True)


    def check_report(self):
        data = {}
        data['form'] = self.read(['date_from', 'date_to', 'report_language'])[0]
        return self.env.ref('employees_attendance_report.action_employees_attendance_report_pdf').report_action(self, data=data, config=False)



