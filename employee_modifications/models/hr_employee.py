from odoo import models, fields, _


class HrEmployeeFamilyInfo(models.Model):
    _name = 'hr.employee.family'
    _rec_name = "member_name"
    _description = 'HR Employee Family'

    member_name = fields.Char(string='Name')
    employee_ref = fields.Many2one(string="Is Employee",
                                   help='If family member currently is an employee of same company, '
                                        'then please tick this field',
                                   comodel_name='hr.employee')
    employee_id = fields.Many2one(string="Employee", help='Select corresponding Employee', comodel_name='hr.employee',
                                  invisible=1)
    relation = fields.Selection([('father', 'Father'),
                                 ('mother', 'Mother'),
                                 ('daughter', 'Daughter'),
                                 ('son', 'Son'),
                                 ('wife', 'Wife')], string='Relationship', help='Relation with employee')
    member_contact = fields.Char(string='Contact No',)

    ticket_price = fields.Float(string="Ticket Price", required=False, )
    member_age = fields.Integer(string='Age', store=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    fam_ids = fields.One2many('hr.employee.family', 'employee_id', string='Family', help='Family Information')
    joining_date = fields.Date(readonly=False, )




