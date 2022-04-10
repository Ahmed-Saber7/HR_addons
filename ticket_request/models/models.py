# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class TicketRequest(models.Model):
    _name = 'ticket.request'
    _inherit = "mail.thread"

    link = fields.Char()

    total_price = fields.Float(string='Total Price', store=False, readonly=True, compute='_amount_all')

    total_price_journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    total_price_debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    total_price_credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    total_price_account_move_id = fields.Many2one(comodel_name="account.move", string="", readonly=True)

    emp_price_ticket = fields.Float(string="Emp. Ticket Price", required=True)

    employee_family = fields.Many2many("hr.employee.family", domain='get_employee_family',
                                       string="Employee family")

    request_date = fields.Date(string="Request Date", default=fields.Date.context_today)

    city_from = fields.Many2one(
        'res.country.state', string="City From", required=True)

    city_to = fields.Many2one(
        'res.country.state', string="City To", required=True)

    state = fields.Selection([
        ('employee', 'Employee'),
        ('hr_officer', 'HR Officer'),
        ('hr_manager', 'HR Manager'),
        ('accounting', 'Accounting'),
        ('confirmed', 'Confirmed'),
        ('rejected', 'Rejected'),
    ], string='Status', track_visibility='onchange', default='employee')

    department_id = fields.Many2one('hr.department', string="Department", related="employee_id.department_id",
                                    readonly=True, store=True)
    start_date = fields.Date(string='Contract Start Date', related='employee_id.contract_id.date_start', readonly=1, )
    end_date = fields.Date(string='Contract End Date', related='employee_id.contract_id.date_end', readonly=1, )
    nationality = fields.Many2one('res.country', string='National', related='employee_id.country_id', readonly=1,
                                  required=True, )
    hr_officer_note = fields.Text('HR Note')
    hr_manager_note = fields.Text('Purchase Note')
    accounting_note = fields.Text('Financial Note')

    name = fields.Char(string="Ticket ID", required=False, default='New', readonly=True)

    # @api.model
    # def create(self, values):
    #     rec = super(TicketRequest, self).create(values)
    #     rec.name = self.env['ir.sequence'].next_by_code('ticket.request')
    #     return rec

    @api.returns('self')
    def _default_employee_get(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    employee_id = fields.Many2one('hr.employee', string='Employee name', readonly=False, default=_default_employee_get)

    @api.depends('employee_family', 'emp_price_ticket')
    def _amount_all(self):
        for line in self.employee_family:
            self.total_price += line.ticket_price
        self.total_price += self.emp_price_ticket

    @api.onchange('employee_id')
    def get_employee_family(self):
        if self.employee_id:
            for rec in self:

                family = self.env['hr.employee.family'].search([('employee_id', '=', rec.employee_id.id)])
                print(family)
                return {
                    'domain': {'employee_family': [('id', 'in', family.ids)], }
                }

    employee_family = fields.Many2many("hr.employee.family", domain=get_employee_family, string="Employee family")

    def employee_confirm(self):
        for rec in self:
            rec.state = 'hr_officer'

    def reject(self):
        for rec in self:
            rec.state = 'rejected'

    def hr_officer_confirm(self):
        for rec in self:
            rec.state = 'hr_manager'

    def hr_manager_confirm(self):
        for rec in self:
            rec.state = 'accounting'

    def accounting_confirm(self):
        for rec in self:
            rec.state = 'confirmed'
            self.create_account_move()

    def gen_secr_confirm(self):
        self.state = 'confirmed'
        self.create_account_move()
        print("done")


    def unlink(self):
        if self.state not in ['employee']:
            if not self.env.user.has_group('base.group_system'):
                raise ValidationError(_('ليس لديك صلاحية الحذف من فضلك تواصل مع الادمن'))
        elif self.state == 'employee':
            if self.employee_id.user_id.id != self.env.user.id and not self.env.user.has_group('base.group_system'):
                raise ValidationError(_('ليس لديك صلاحية الحذف من فضلك تواصل مع الادمن'))
        super(TicketRequest, self).unlink()

    def create_account_move(self):
        move_line_1 = {
            'name': self.name or '',
            'account_id': self.total_price_debit_account_id.id or False,
            'debit': self.total_price,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id or False,
            'credit': 0.0,
        }
        move_line_2 = {
            'name': self.name or '',
            'account_id': self.total_price_credit_account_id.id or False,
            'debit': 0.0,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id or False,
            'credit': self.total_price,
        }
        move_vals = {
            'name': self.name or '',
            'date': self.request_date or False,
            'state': 'draft',
            'journal_id': self.total_price_journal_id.id or False,
            'ticket_id': self.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        account_move = self.env['account.move'].create(move_vals)
        self.total_price_account_move_id = account_move.id


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    ticket_id = fields.Many2one(comodel_name="ticket.request", string="", required=False, )
