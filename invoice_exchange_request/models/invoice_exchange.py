# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class InvoiceExchange(models.Model):
    _name = 'invoice.exchange'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name", default="New", readonly=True, copy=False)



    state = fields.Selection(string="", selection=[('draft', 'Draft'), ('d_manager', 'Direct Manager'),
                                                   ('hr_manager', 'HR Manager'), ('accounting_manager', 'Accounting Manager'),
                                                   ('confirm', 'Confirmed'), ('rejected', 'Rejected')], required=False,
                             default='draft')

    def employee_confirm(self):
        for rec in self:
            rec.state = 'd_manager'

    def d_manager_confirm(self):
        for rec in self:
            if self.env.user.id == self.employee_id.parent_id.user_id.id:
                rec.write({'state': 'hr_manager'})
            else:
                raise ValidationError("Only Employee Manger Can Approve That! ")

    def hr_manager_confirm(self):
        for rec in self:
            rec.state = 'accounting_manager'

    def accounting_manager_confirm(self):
        for rec in self:
            rec.state = 'confirm'
            self.create_account_move()

    def reject_button(self):
        for rec in self:
            rec.state = 'rejected'

    d_manager_notes = fields.Text()
    hr_manager_notes = fields.Text()
    accounting_manager_notes = fields.Text()

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee Name", required=True, )

    request_date = fields.Date(string="Today Date", required=True, default=fields.Date.context_today)

    amount = fields.Float(string="Amount", required=True )

    reason = fields.Text(string="Reason", required=False, )

    amount_journal_id = fields.Many2one(comodel_name="account.journal", string="Journal", )
    amount_debit_account_id = fields.Many2one(comodel_name="account.account", string="Debit Account", )
    amount_credit_account_id = fields.Many2one(comodel_name="account.account", string="Credit Account", )
    amount_account_move_id = fields.Many2one(comodel_name="account.move", string="Account Move", readonly=True)



    @api.model
    def create(self, vals):
        vals['name'] = (self.env['ir.sequence'].next_by_code('invoice.exchange')) or 'New'
        return super(InvoiceExchange, self).create(vals)


    def create_account_move(self):
        move_line_1 = {
            'name': self.name or '',
            'account_id': self.amount_debit_account_id.id or False,
            'debit': self.amount or 0.0,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id or False,
            'credit': 0.0,
        }
        move_line_2 = {
            'name': self.name or '',
            'account_id': self.amount_credit_account_id.id or False,
            'debit': 0.0,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id or False,
            'credit': self.amount or 0.0,
        }
        move_vals = {
            'name': self.name or '',
            'date': self.request_date or False,
            'state': 'draft',
            'journal_id': self.amount_journal_id.id or False,
            'invoice_exchange_id': self.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        account_move = self.env['account.move'].create(move_vals)
        self.amount_account_move_id = account_move.id

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    invoice_exchange_id = fields.Many2one(comodel_name="invoice.exchange", string="", required=False, )
