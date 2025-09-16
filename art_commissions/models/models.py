# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime


class Commission(models.Model):
    _name = "art.commission"
    _description = "Art commission"
    _rec_name = 'code'

    code = fields.Char("Code", required=True, default='New')
    client_id = fields.Many2one("res.partner", "Client", required=True)
    category = fields.Selection([
        ('fanart', 'Fanart'),
        ('original', 'Original')
    ], default="fanart", string="Category", required=True)
    status = fields.Selection([
        ('draft', "Draft"),
        ('submitted', "Submitted"),
        ("accepted", "Accepted"),
        ("sketching", "Sketching"),
        ("rendering", "Rendering"),
        ("completed", "Completed")
    ], default="draft", string="Status")
    description = fields.Text("Description", required=True)
    reference_ids = fields.Many2many("ir.attachment", string="References")
    accept_date = fields.Datetime("Accepted on")
    sketch_start_date = fields.Datetime("Sketch started on")
    rendering_start_date = fields.Datetime("Rendering started on")
    completion_date = fields.Datetime("Completed on")
    product_id = fields.Many2one("product.product", "Related Product", required=True)
    order_id = fields.Many2one("sale.order", "Related Order", required=True)


    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('art.commission') or 'New'
        result = super(Commission, self).create(vals)
        return result
    

    def action_accept(self):
        for rec in self:
            rec.status = "accepted"
            # TODO: add email notification and background processes
            rec.accept_date = datetime.now()

    
    def action_start_sketching(self):
        for rec in self:
            rec.status = "sketching"
            # TODO: add email notification and background processes
            rec.sketch_start_date = datetime.now()

    
    def action_start_rendering(self):
        for rec in self:
            rec.status =  "rendering"
            # TODO: add email notification and background processes
            rec.rendering_start_date = datetime.now()

        
    def action_complete_commission(self):
        for rec in self:
            rec.status = "completed"
            # TODO: add email notification and background processes
            rec.completion_date = datetime.now()




# class art_commissions(models.Model):
#     _name = 'art_commissions.art_commissions'
#     _description = 'art_commissions.art_commissions'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
