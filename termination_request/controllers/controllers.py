# -*- coding: utf-8 -*-
# from odoo import http


# class TerminationRequest(http.Controller):
#     @http.route('/termination_request/termination_request/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/termination_request/termination_request/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('termination_request.listing', {
#             'root': '/termination_request/termination_request',
#             'objects': http.request.env['termination_request.termination_request'].search([]),
#         })

#     @http.route('/termination_request/termination_request/objects/<model("termination_request.termination_request"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('termination_request.object', {
#             'object': obj
#         })
