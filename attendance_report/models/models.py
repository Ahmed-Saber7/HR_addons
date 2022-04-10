# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta, datetime


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    determination_people = fields.Boolean(string="", )


class ReportDeterminationPeoplenumber(models.AbstractModel):
    _name = 'report.attendance_report.attendance_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        report_language = data['form']['report_language']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        all_attendances = []

        all_attendances_object = self.env['hr.attendance'].search([('check_in', '>=', date_from), ('check_out', '<=', date_to)])

        if all_attendances_object:
            for attendance in all_attendances_object:
                all_attendances.append({'name': attendance.employee_id.name,
                                        'check_in': attendance.check_in,
                                        'check_out': attendance.check_out,
                                        'worked_hours': attendance.worked_hours, })
                print("all_attendances", all_attendances)

        print("all_attendances", all_attendances_object)


        docargs = {
            'doc_model': 'hr.attendance',
            'date': date.today(),
            'report_language': report_language,
            'date_from': date_from,
            'date_to': date_to,
            'attendances': all_attendances,

        }
        return docargs
