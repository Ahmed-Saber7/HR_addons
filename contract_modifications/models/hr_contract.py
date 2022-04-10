from odoo import models, fields, api
from odoo.exceptions import Warning, UserError, ValidationError


class employee_contract(models.Model):
    _inherit = 'hr.contract'

    # insurance_wage = fields.Float(string="Insurance Wage")
    # employee_percent = fields.Float(string="Employee Percent")
    # company_percent = fields.Float('Company Percent')
    # employee_insurance_amount = fields.Float(string="Employee Insurance Amount", compute='_compute_amounts')
    # company_insurance_amount = fields.Float(string="Company Insurance Amount", compute='_compute_amounts')
    # profit_tax_percent = fields.Float(string="Profit Tax Percent")
    # profit_tax_amount = fields.Float(string="Profit Tax Amount", compute='_compute_amounts')

    # @api.depends('wage', 'profit_tax_percent', 'insurance_wage', 'employee_percent', 'company_percent')
    # def _compute_amounts(self):
    #     for rec in self:
    #         rec.profit_tax_amount = rec.wage * (rec.profit_tax_percent / 100)
    #         rec.employee_insurance_amount = rec.insurance_wage * (rec.employee_percent / 100)
    #         rec.company_insurance_amount = rec.insurance_wage * (rec.company_percent / 100)

    # //////////////////////////////////////////////////////////////
    # TODO Allowances fields

    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account')
    house_allowances = fields.Float(string="")
    overtime_allowance = fields.Float(string="")
    treatment_allowance = fields.Float(string="")
    transport_allowances = fields.Float(string="")
    living_allowances = fields.Float(string="")
    nature_of_work_allowances = fields.Float(string="")
    telephone_allowance = fields.Float(string="")

    # TODO NEW Allowances fields
    Regular_bonus_for_managers = fields.Float(string="",  required=False, )
    Regular_regularity_equivalent = fields.Float(string="",  required=False, )
    Incentive_bonus = fields.Float(string="",  required=False, )
    motivation = fields.Float(string="",  required=False, )
    profit_account = fields.Float(string="",  required=False, )

    # TODO Deductions fields
    general_deductions = fields.Float(string="")
    social_insurance_deductions = fields.Float(string="")
    medical_insurance_deductions = fields.Float(string="")
    fingerprint_deductions = fields.Float(string="")
    administrative_deductions = fields.Float(string="")
    absence_without_permission_deductions = fields.Float(string="")
    absence_discount_without_credit_deductions = fields.Float(string="")
    # //////////////////////////////////////////////////////////////

    type_of_company_offices = fields.Selection(string="Types of company offices",
                                               selection=[('saudi_office', 'Saudi office'),
                                                          ('egyptian_office', 'Egyptian office'), ], required=False, )

    # TODO Social Insurance fields
    insurance_date = fields.Date()
    insurance_salary = fields.Float()
    employee_percentage = fields.Float()
    company_percentage = fields.Float()
    employee_amount = fields.Float(compute='get_employee_percentage')
    company_amount = fields.Float(compute='get_employee_percentage')
    employee_gosi = fields.Float(string="Employee Gosi", required=False, compute='get_employee_percentage')
    company_gosi = fields.Float(string="Company Gosi", required=False, compute='get_employee_percentage')

    @api.depends('employee_percentage', 'company_percentage')
    def get_employee_percentage(self):
        if self.type_of_company_offices == 'egyptian_office':
            print("aaaaaa")
            self.employee_amount = self.get_amount_insurance(self.insurance_salary, self.employee_percentage)
            self.company_amount = self.get_amount_insurance(self.insurance_salary, self.company_percentage)
            self.employee_gosi = 0.0
            self.company_gosi = 0.0
        elif self.type_of_company_offices == 'saudi_office':
            print("bbbbbb")
            self.employee_gosi = self.get_amount_insurance(self.insurance_salary, self.employee_percentage)
            self.company_gosi = self.get_amount_insurance(self.insurance_salary, self.company_percentage)
            self.employee_amount = 0.0
            self.company_amount = 0.0
        else:
            self.employee_gosi = 0.0
            self.company_gosi = 0.0
            self.employee_amount = 0.0
            self.company_amount = 0.0


    def get_amount_insurance(self, insurance_salary, insurance_percentage):
        return insurance_salary * (insurance_percentage / 100)

    @api.onchange('type_of_company_offices')
    def set_insurance_salary(self):
        print("11111")
        for rec in self:
            if rec.type_of_company_offices == 'saudi_office':
                rec.insurance_salary = rec.wage + rec.house_allowances
            elif self.type_of_company_offices == 'egyptian_office':
                rec.insurance_salary = rec.wage
            else:
                return

    @api.onchange('house_allowances')
    def set_insurance_salaryy(self):
        print("22222")
        for rec in self:
            if rec.type_of_company_offices == 'saudi_office':
                rec.insurance_salary = rec.wage + rec.house_allowances
            elif self.type_of_company_offices == 'egyptian_office':
                rec.insurance_salary = rec.wage
            else:
                return

    def write(self, values):
        res = super(employee_contract, self).write(values)
        if 'house_allowances' in values or 'wage' in values:
            self.insurance_salary = self.wage + self.house_allowances
        return res