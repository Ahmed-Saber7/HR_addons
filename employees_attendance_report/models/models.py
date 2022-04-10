# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date, timedelta, datetime
import pytz
from odoo.tools import format_time


class ReportEmployeesAttendance_Report(models.AbstractModel):
    _name = 'report.employees_attendance_report.emp_att_repo_temp'

    @api.model
    def _get_report_values(self, docids, data=None):

        report_language = data['form']['report_language']
        date_from = data['form']['date_from']
        date_to = data['form']['date_to']
        all_attendances = []
        all_employees_have_attendance = []
        all_attendances_object = self.env['hr.attendance'].search([('check_in', '>=', date_from), ('check_out', '<=', date_to)])
        for attendance in all_attendances_object:
            all_employees_have_attendance.append(attendance.employee_id)
        all_employees_have_attendance = list(dict.fromkeys(all_employees_have_attendance))

        if all_attendances_object:
            if all_employees_have_attendance:
                for employee in all_employees_have_attendance:
                    all_actual_working_hours = 0.0
                    all_planned_working_hours = 0.0
                    days = 0.0
                    lateness_hours = 0.0
                    employee_attendances_object = self.env['hr.attendance'].search([('check_in', '>=', date_from), ('check_out', '<=', date_to), ('employee_id', '=', employee.id)])
                    days = len(employee_attendances_object)
                    for attendance in employee_attendances_object:
                        # print("attendance.check_in", attendance.check_in)
                        # print("attendance.check_in.time()", attendance.check_in.time())
                        # print("attendance.check_in.time()", type(attendance.check_in.time()))
                        # print("attendance.check_in type", type(attendance.check_in))
                        # print("attendance.check_in", attendance.check_in.strftime('%A'))
                        check_in_day_name = attendance.check_in.strftime('%A')
                        check_in_planned_hour = 0.0
                        employee_resource_calendar = employee.resource_calendar_id
                        if employee_resource_calendar:


                            user_tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz)
                            attendance_check_in = pytz.utc.localize(attendance.check_in).astimezone(user_tz)


                            actual_check_in_hour = attendance_check_in.strftime('%H:%M')
                            actual_check_in_hour_float = float(actual_check_in_hour.replace(":", "."))
                            employee_resource_calendar_attendance_ids = employee.resource_calendar_id.attendance_ids
                            for emp_res_cal_att in employee_resource_calendar_attendance_ids:
                                if emp_res_cal_att.dayofweek == '0' and check_in_day_name == 'Monday':
                                    check_in_planned_hour = emp_res_cal_att.hour_from
                                elif emp_res_cal_att.dayofweek == '1' and check_in_day_name == 'Tuesday':
                                    check_in_planned_hour = emp_res_cal_att.hour_from
                                elif emp_res_cal_att.dayofweek == '2' and check_in_day_name == 'Wednesday':
                                    check_in_planned_hour = emp_res_cal_att.hour_from
                                elif emp_res_cal_att.dayofweek == '3' and check_in_day_name == 'Thursday':
                                    check_in_planned_hour = emp_res_cal_att.hour_from
                                elif emp_res_cal_att.dayofweek == '4' and check_in_day_name == 'Friday':
                                    check_in_planned_hour = emp_res_cal_att.hour_from
                                elif emp_res_cal_att.dayofweek == '5' and check_in_day_name == 'Saturday':
                                    check_in_planned_hour = emp_res_cal_att.hour_from
                                elif emp_res_cal_att.dayofweek == '6' and check_in_day_name == 'Sunday':
                                    check_in_planned_hour = emp_res_cal_att.hour_from
                            print("attendance.check_in", attendance_check_in)
                            print("check_in_day_name", check_in_day_name)
                            print("actual_check_in_hour_float", actual_check_in_hour_float)
                            print("check_in_planned_hour", check_in_planned_hour)
                            if check_in_planned_hour > 0:
                                if actual_check_in_hour_float > check_in_planned_hour:
                                    lateness = actual_check_in_hour_float - check_in_planned_hour
                                    print("lateness", lateness)
                                    lateness_hours += lateness

                        # diff = attendance.check_out - attendance.check_in
                        # worked_hours = diff.total_seconds() / 3600
                        all_actual_working_hours += attendance.worked_hours

                        all_planned_working_hours = len(employee_attendances_object) * employee.resource_calendar_id.hours_per_day
                    all_attendances.append({'employee_name': employee.name,
                                            'all_actual_working_hours': all_actual_working_hours,
                                            'all_planned_working_hours': all_planned_working_hours,
                                            'days': days,
                                            'lateness_hours': lateness_hours, })

        print("lateness >>>>", lateness)
        print("all_attendances", all_attendances)

        docargs = {
            'doc_model': 'hr.attendance',
            'date': date.today(),
            'report_language': report_language,
            'date_from': date_from,
            'date_to': date_to,
            'attendances': all_attendances,

        }
        return docargs
