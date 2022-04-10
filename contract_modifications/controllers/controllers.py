# -*- coding: utf-8 -*-
# from odoo import http


# class ContractModifications(http.Controller):
#     @http.route('/contract_modifications/contract_modifications/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/contract_modifications/contract_modifications/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('contract_modifications.listing', {
#             'root': '/contract_modifications/contract_modifications',
#             'objects': http.request.env['contract_modifications.contract_modifications'].search([]),
#         })

#     @http.route('/contract_modifications/contract_modifications/objects/<model("contract_modifications.contract_modifications"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('contract_modifications.object', {
#             'object': obj
#         })
