# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError
from datetime import date, datetime


class HREmployeesTermination(models.Model):
    _name = 'hr.termination'

    name = fields.Char(compute='_set_name')

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, )

    termination_type = fields.Selection(string="Type", selection=[('resignation', 'Resignation'),
                                                                  ('end_contract', 'End Of Contract'),
                                                                  ('terminate', 'Terminate'), ])

    state = fields.Selection(string="", selection=[('d_manager', 'Direct Manager'), ('purchase', 'Purchase Manager'),
                                                   ('hr_manager', 'HR Manager'), ('accounting_manager', 'Accounting Manager'),
                                                   ('confirm', 'Confirmed'), ('rejected', 'Rejected')], required=False,
                             default='d_manager')

    d_manager_notes = fields.Text()
    purchase_notes = fields.Text()
    hr_manager_notes = fields.Text()
    accounting_manager_notes = fields.Text()


    # TODO NEW WORKFLOW

    def d_manager_confirm(self):
        for rec in self:
            if rec.if_handover == False:
                raise ValidationError("Sorry, this employee does not have a handover request yet")
            if self.env.user.id != self.employee_id.parent_id.user_id.id:
                raise ValidationError("Only Employee Manger Can Approve That! ")
            else:
                rec.state = 'purchase'

    def purchase_confirm(self):
        for rec in self:
            rec.state = 'hr_manager'

    def hr_manager_confirm(self):
        for rec in self:
            rec.state = 'accounting_manager'

    def accounting_manager_confirm(self):
        for rec in self:
            rec.state = 'confirm'
            self.create_account_move()

    def reject(self):
        self.state = 'rejected'

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, )
    employee_company_id = fields.Many2one('res.company', related='employee_id.company_id')
    employee_department_id = fields.Many2one('hr.department', related='employee_id.department_id')
    handover_id = fields.Many2one('hr.handover', string="Employee Handover", readonly=True, )
    joining_date = fields.Date(readonly=True, related='employee_id.joining_date')
    notes = fields.Text()
    contract_id = fields.Many2one('hr.contract', related='employee_id.contract_id')
    contract_joining_date = fields.Date(readonly=True, related='contract_id.date_start')
    today_date = fields.Date(readonly=True, default=fields.Date.context_today)
    duration_days = fields.Float(string="Duration/days", readonly=True)
    duration_years = fields.Float(string="Duration/years", readonly=True)
    other_allowances = fields.Float(string="Other Allowances", required=False, )
    other_deductions = fields.Float(string="Other Deductions", required=False, )
    left_vacations_days = fields.Float(string="Left Vacation Days", required=False, readonly=True)
    left_vacations_days_amount = fields.Float(string="Left Vacation Amount", required=False, readonly=True)
    wage_day_amount = fields.Float(string="", required=False, )
    loans = fields.Float(string="Outstanding Loans", required=False, readonly=True)
    last_working_day = fields.Date(string="", required=False, )
    last_working_days = fields.Float(string="", required=False, readonly=True)
    deserved_salary = fields.Float(string="", required=False, readonly=True)
    deserved_salary_amount = fields.Float(string="", required=False, readonly=True)
    wage = fields.Float(string="", required=False, readonly=True)
    wage_day_amount = fields.Float(string="", required=False, readonly=True)
    absence_days = fields.Float(string="Absence Days", required=False, )
    absence_days_deduction = fields.Float(string="Absence Days Deduction", required=False, readonly=True)
    total_eos = fields.Float(string="Total EOS", required=False, )
    total_eos_with_all = fields.Float(string="Total EOS With All", required=False, )
    journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    account_move_id = fields.Many2one(comodel_name="account.move", string="", )
    if_handover = fields.Boolean(string="", default=False)
    contract_date_end = fields.Date(string="", required=False, related='contract_id.date_end')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            print("qqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqqq")
            # self.onchange_termination_type()
            if not self.employee_id.joining_date:
                raise ValidationError("Sorry, this employee does not have a joining date yet")
            total = 0.0
            total_loan = 0.0
            total_days = self.env['hr.leave.report'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate')])
            loan_obj = self.env['hr.loan'].search([('employee_id', '=', self.employee_id.id), ])

            self.wage = self.employee_id.contract_id.wage
            self.wage_day_amount = self.employee_id.contract_id.wage / 30
            if self.today_date and self.joining_date:
                num_days = self.today_date - self.joining_date
                num_days = num_days.days
                num_years = num_days / 365
                self.duration_days = num_days
                self.duration_years = num_years

            if self.last_working_days:
                self.deserved_salary_amount = self.last_working_days * self.wage_day_amount

            if not self.last_working_days:
                self.deserved_salary_amount = self.last_working_days * self.wage_day_amount

            if total_days:
                for days in total_days:
                    total += days.number_of_days
                self.left_vacations_days = total
                self.left_vacations_days_amount = total * self.wage_day_amount

            if loan_obj:
                print("loan_obj", loan_obj)
                for loan in loan_obj:
                    loan_ids = loan.loan_lines.filtered(lambda x: not x.paid)
                    total_loan += sum(loan_ids.mapped('amount'))
                self.loans = total_loan
            if not loan_obj:
                self.loans = 0.0


        else:
            self.wage = 0.0
            self.wage_day_amount = 0.0
            self.duration_days = 0.0
            self.duration_years = 0.0
            self.last_working_day = 0.0
            self.last_working_days = 0.0
            self.deserved_salary_amount = 0.0
            self.left_vacations_days = 0.0
            self.left_vacations_days_amount = 0.0
            self.loans = 0.0
            self.absence_days_deduction = 0.0

    @api.onchange('last_working_day')
    def onchange_last_working_day(self):
        if self.last_working_day:
            date_from = datetime.strptime(self.last_working_day.strftime('%Y%m%d'), '%Y%m%d')
            self.last_working_days = date_from.day
            if self.wage_day_amount:
                self.deserved_salary_amount = self.last_working_days * self.wage_day_amount
            else:
                self.deserved_salary_amount = 0.0
        else:
            self.last_working_days = 0.0

    @api.onchange('absence_days')
    def onchange_absence_days(self):
        if self.absence_days:
            if self.wage_day_amount:
                self.absence_days_deduction = self.absence_days * self.wage_day_amount
            else:
                self.absence_days_deduction = 0.0
        else:
            self.absence_days_deduction = 0.0

    @api.onchange('termination_type', 'employee_id')
    def onchange_termination_type(self):
        if self.termination_type or self.employee_id:
            if self.termination_type == 'resignation':
                print("resignation")
                if self.duration_years < 2:
                    print("less than 2")
                    self.total_eos = 0.0
                if self.duration_years >= 2 and self.duration_years < 5:
                    print("2 to 5")
                    self.total_eos = ((self.wage / 2) * self.duration_years) / 3
                    print("total eos", self.total_eos)
                if self.duration_years >= 5 and self.duration_years < 10:
                    print("5 to 10")
                    self.total_eos = ((self.wage * 2.5) + (self.wage * (self.duration_years - 5)) * (2 / 3))
                if self.duration_years >= 10:
                    print("10")
                    self.total_eos = (self.wage * 2.5) + (self.wage * (self.duration_years - 5))
            if self.termination_type == 'end_contract':
                print("end_contract")
                if self.duration_years < 2:
                    print("less than 2")
                    self.total_eos = 0.0
                if self.duration_years >= 2 and self.duration_years < 5:
                    print("2 to 5")
                    self.total_eos = (self.wage / 2) * self.duration_years
                if self.duration_years >= 5 and self.duration_years < 10:
                    print("5 to 10")
                    self.total_eos = ((self.wage * 2.5) + (self.wage * (self.duration_years - 5)))
                if self.duration_years >= 10:
                    print("10")
                    self.total_eos = (self.wage * 2.5) + (self.wage * (self.duration_years - 5))
            if self.termination_type == 'terminate':
                print("terminate")
                if self.duration_years < 10:
                    print("less than 2")
                    self.total_eos = 0.0
                if self.duration_years > 10:
                    print("more than 10")
                    self.total_eos = (self.wage / 2) * 5 + (self.wage * (self.duration_years - 5))

    @api.depends('employee_id')
    def _set_name(self):
        for rec in self:
            if rec.employee_id:
                rec.name = rec.employee_id.name + "'s Termination"
            else:
                rec.name = ''

    def check_handover(self):
        if self.employee_id:
            handovers = self.env['hr.handover'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'confirm')])
            print('handovers >>>', handovers)
            if len(handovers) > 0:
                self.handover_id = handovers[0]
                self.if_handover = True
            else:
                raise ValidationError("Sorry, this employee does not have a handover request yet")

    @api.constrains('last_working_days')
    def _check_last_working_days(self):
        for record in self:
            if record.last_working_days > 31:
                raise ValidationError(_('Your Last Working Days Cant be more than 31.'))


    journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    account_move_id = fields.Many2one(comodel_name="account.move", string="", )

    left_vacation_amount_journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    left_vacation_amount_debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    left_vacation_amount_credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    left_vacation_amount_account_move_id = fields.Many2one(comodel_name="account.move", string="", )

    deserved_salary_journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    deserved_salary_debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    deserved_salary_credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    deserved_salary_move_id = fields.Many2one(comodel_name="account.move", string="", )

    outstanding_loans_journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    outstanding_loans_debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    outstanding_loans_credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    outstanding_loans_move_id = fields.Many2one(comodel_name="account.move", string="", )

    absence_days_journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    absence_days_debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    absence_days_credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    absence_days_move_id = fields.Many2one(comodel_name="account.move", string="", )

    other_allowances_journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    other_allowances_debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    other_allowances_credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    other_allowances_move_id = fields.Many2one(comodel_name="account.move", string="", )

    other_deductions_journal_id = fields.Many2one(comodel_name="account.journal", string="", )
    other_deductions_debit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    other_deductions_credit_account_id = fields.Many2one(comodel_name="account.account", string="", )
    other_deductions_move_id = fields.Many2one(comodel_name="account.move", string="", )


    def create_account_move(self):
        move_line_1 = {
            'name': self.name,
            'account_id': self.debit_account_id.id,
            'debit': self.total_eos,
            'credit': 0.0,
            'partner_id': self.employee_id.address_home_id.id,
        }
        print("move_line_1 >>>>>>>>>>", move_line_1)
        move_line_2 = {
            'name': self.name,
            'account_id': self.credit_account_id.id,
            'debit': 0.0,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
            'credit': self.total_eos,
        }
        print("move_line_2 >>>>>>>>>>", move_line_2)
        move_vals = {
            'name': self.name or '',
            'date': self.today_date or False,
            'state': 'draft',
            'journal_id': self.journal_id.id,
            'termination_id': self.id,
            'line_ids': [(0, 0, move_line_1), (0, 0, move_line_2)],
        }
        print("move_vals >>>>>>>>>>", move_vals)
        print("___________________________________________________________")
        account_move = self.env['account.move'].create(move_vals)
        print("account_move >>>>>>>>>>", account_move)
        self.account_move_id = account_move.id

        move_line_3 = {
            'name': self.name or '',
            'account_id': self.left_vacation_amount_debit_account_id.id,
            'debit': self.left_vacations_days_amount,
            'credit': 0.0,
            'partner_id': self.employee_id.address_home_id.id,
        }
        print("move_line_3 >>>>>>>>>>", move_line_3)

        move_line_33 = {
            'name': self.name or '',
            'account_id': self.left_vacation_amount_credit_account_id.id,
            'debit': 0.0,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
            'credit': self.left_vacations_days_amount,
        }
        print("move_line_33 >>>>>>>>>>", move_line_33)

        move_vals = {
            'name': self.name or '',
            'date': self.today_date or False,
            'state': 'draft',
            'journal_id': self.left_vacation_amount_journal_id.id,
            'termination_id': self.id,
            'line_ids': [(0, 0, move_line_3), (0, 0, move_line_33)],
        }

        print("move_vals >>>>>>>>>>", move_vals)
        print("___________________________________________________________")

        account_move = self.env['account.move'].create(move_vals)
        self.left_vacation_amount_account_move_id = account_move.id

        move_line_5 = {
            'name': self.name or '',
            'account_id': self.deserved_salary_debit_account_id.id,
            'debit': self.deserved_salary_amount,
            'credit': 0.0,
        }
        print("move_line_5 >>>>>>>>>>", move_line_5)

        move_line_55 = {
            'name': self.name or '',
            'account_id': self.deserved_salary_credit_account_id.id,
            'debit': 0.0,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
            'credit': self.deserved_salary_amount,
        }
        print("move_line_55 >>>>>>>>>>", move_line_55)
        move_vals = {
            'name': self.name or '',
            'date': self.today_date or False,
            'state': 'draft',
            'journal_id': self.deserved_salary_journal_id.id,
            'termination_id': self.id,
            'line_ids': [(0, 0, move_line_5), (0, 0, move_line_55)],
        }
        print("move_vals >>>>>>>>>>", move_vals)
        print("___________________________________________________________")

        account_move = self.env['account.move'].create(move_vals)
        self.deserved_salary_move_id = account_move.id

        move_line_6 = {
            'name': self.name or '',
            'account_id': self.outstanding_loans_credit_account_id.id,
            'debit': 0.0,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
            'credit': self.loans,
        }
        print("move_line_6 >>>>>>>>>>", move_line_6)

        move_line_66 = {
            'name': self.name or '',
            'account_id': self.outstanding_loans_debit_account_id.id,
            'debit': self.loans,
            'credit': 0.0,
        }
        print("move_line_66 >>>>>>>>>>", move_line_66)

        move_vals = {
            'name': self.name or '',
            'date': self.today_date or False,
            'state': 'draft',
            'journal_id': self.outstanding_loans_journal_id.id,
            'termination_id': self.id,
            'line_ids': [(0, 0, move_line_6), (0, 0, move_line_66)],
        }
        print("move_vals >>>>>>>>>>", move_vals)
        print("___________________________________________________________")

        account_move = self.env['account.move'].create(move_vals)
        self.outstanding_loans_move_id = account_move.id

        move_line_7 = {
            'name': self.name or '',
            'account_id': self.absence_days_credit_account_id.id,
            'debit': 0.0,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
            'credit': self.absence_days_deduction,
        }
        print("move_line_7 >>>>>>>>>>", move_line_7)
        move_line_77 = {
            'name': self.name or '',
            'account_id': self.absence_days_debit_account_id.id,
            'debit': self.absence_days_deduction,
            'credit': 0.0,
        }
        print("move_line_77 >>>>>>>>>>", move_line_77)
        move_vals = {
            'name': self.name or '',
            'date': self.today_date or False,
            'state': 'draft',
            'journal_id': self.absence_days_journal_id.id,
            'termination_id': self.id,
            'line_ids': [(0, 0, move_line_7), (0, 0, move_line_77)],
        }
        print("move_vals >>>>>>>>>>", move_vals)
        print("___________________________________________________________")

        account_move = self.env['account.move'].create(move_vals)
        self.absence_days_move_id = account_move.id

        move_line_8 = {
            'name': self.name or '',
            'account_id': self.other_allowances_credit_account_id.id,
            'debit': 0.0,
            'credit': self.other_allowances,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
        }
        print("move_line_8 >>>>>>>>>>", move_line_8)
        move_line_88 = {
            'name': self.name or '',
            'account_id': self.other_allowances_debit_account_id.id,
            'debit': self.other_allowances,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
            'credit': 0.0,
        }
        print("move_line_88 >>>>>>>>>>", move_line_88)
        move_vals = {
            'name': self.name or '',
            'date': self.today_date or False,
            'state': 'draft',
            'journal_id': self.other_allowances_journal_id.id,
            'termination_id': self.id,
            'line_ids': [(0, 0, move_line_8), (0, 0, move_line_88)],
        }
        print("move_vals >>>>>>>>>>", move_vals)
        print("___________________________________________________________")

        account_move = self.env['account.move'].create(move_vals)
        self.other_allowances_move_id = account_move.id
        # ///////////////////////////////////////////////////////////////////////////////////////////////////
        move_line_9 = {
            'name': self.name or '',
            'account_id': self.other_deductions_credit_account_id.id,
            'debit': 0.0,
            'credit': self.other_deductions,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,

        }
        print("move_line_9 >>>>>>>>>>", move_line_9)
        move_line_99 = {
            'name': self.name or '',
            'account_id': self.other_deductions_debit_account_id.id,
            'debit': self.other_deductions,
            'analytic_account_id': self.employee_id.contract_id.analytic_account_id.id,
            'credit': 0.0,
        }
        print("move_line_99 >>>>>>>>>>", move_line_99)
        move_vals = {
            'name': self.name or '',
            'date': self.today_date or False,
            'state': 'draft',
            'journal_id': self.other_deductions_journal_id.id,
            'termination_id': self.id,
            'line_ids': [(0, 0, move_line_9), (0, 0, move_line_99)],
        }
        print("move_vals >>>>>>>>>>", move_vals)
        print("___________________________________________________________")

        account_move = self.env['account.move'].create(move_vals)
        self.other_deductions_move_id = account_move.id

        # ///////////////////////////////////////////////////////////////////////////////////////////////////


class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    termination_id = fields.Many2one(comodel_name="'hr.termination", string="", required=False, )
