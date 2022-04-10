# -*- coding: utf-8 -*-
# from odoo import http


# class EmployeesAttendanceReport(http.Controller):
#     @http.route('/employees_attendance_report/employees_attendance_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/employees_attendance_report/employees_attendance_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('employees_attendance_report.listing', {
#             'root': '/employees_attendance_report/employees_attendance_report',
#             'objects': http.request.env['employees_attendance_report.employees_attendance_report'].search([]),
#         })

#     @http.route('/employees_attendance_report/employees_attendance_report/objects/<model("employees_attendance_report.employees_attendance_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('employees_attendance_report.object', {
#             'object': obj
#         })
