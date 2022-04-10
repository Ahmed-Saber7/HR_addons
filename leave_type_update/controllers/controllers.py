# -*- coding: utf-8 -*-
# from odoo import http


# class LeaveTypeUpdate(http.Controller):
#     @http.route('/leave_type_update/leave_type_update/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/leave_type_update/leave_type_update/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('leave_type_update.listing', {
#             'root': '/leave_type_update/leave_type_update',
#             'objects': http.request.env['leave_type_update.leave_type_update'].search([]),
#         })

#     @http.route('/leave_type_update/leave_type_update/objects/<model("leave_type_update.leave_type_update"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('leave_type_update.object', {
#             'object': obj
#         })
