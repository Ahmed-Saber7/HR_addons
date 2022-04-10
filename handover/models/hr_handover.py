# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import Warning, ValidationError


class HREmployeesEvalution(models.Model):
    _name = 'hr.handover'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(compute='_set_name')
    sales_person = fields.Many2one('res.users', string='Sales Person', default=lambda self: self.env.uid,
                                   track_visibility='always')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True)

    state = fields.Selection(string="", selection=[('d_manager', 'Direct Manager'), ('purchase', 'Purchase Manager'),
                                                   ('hr_manager', 'HR Manager'), ('accounting_manager', 'Accounting Manager'),
                                                   ('confirm', 'Confirmed'), ('rejected', 'Rejected')], required=False,
                             default='d_manager')
    d_manager_notes = fields.Text()
    purchase_notes = fields.Text()
    hr_manager_notes = fields.Text()
    accounting_manager_notes = fields.Text()

    def d_manager_confirm(self):
        for rec in self:
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

    def reject(self):
        self.state = 'rejected'


    def reject(self):
        self.state = 'rejected'

    employee_company_id = fields.Many2one('res.comapny', readonly=True)
    employee_department_id = fields.Many2one('hr.department', related='employee_id.department_id')
    joining_date = fields.Date(readonly=True)
    line_ids = fields.One2many('hr.handover.approvals', 'handover_id', "Approvals", readonly=True)

    @api.onchange('employee_id')
    def set_employee_info(self):
        if self.employee_id:
            self.employee_company_id = self.employee_id.company_id.id
            contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id)])
            if len(contracts) > 0:
                self.joining_date = contracts[0].date_start
        else:
            self.joining_date = False
            self.employee_company_id = False

    @api.constrains('employee_id')
    def survey_id_constrains(self):
        if self.employee_id:
            same_employee_count = self.env['hr.handover'].search_count([('employee_id', '=', self.employee_id.id)])
            if same_employee_count > 1:
                raise ValidationError(_('Employee must be unique'))

    @api.depends('employee_id')
    def _set_name(self):
        for rec in self:
            if rec.employee_id:
                rec.name = rec.employee_id.name + "'s Handover"
            else:
                rec.name = ''

    # TODO NEW WORKFLOW


class HREmployeesEvalutionQuestions(models.Model):
    _name = 'hr.handover.approvals'

    handover_id = fields.Many2one('hr.handover')
    user_id = fields.Many2one('res.users', required=True)
    date_of_approval = fields.Date()
