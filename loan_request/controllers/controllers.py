# -*- coding: utf-8 -*-
# from odoo import http


# class LoanRequest(http.Controller):
#     @http.route('/loan_request/loan_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/loan_request/loan_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('loan_request.listing', {
#             'root': '/loan_request/loan_request',
#             'objects': http.request.env['loan_request.loan_request'].search([]),
#         })

#     @http.route('/loan_request/loan_request/objects/<model("loan_request.loan_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('loan_request.object', {
#             'object': obj
#         })
