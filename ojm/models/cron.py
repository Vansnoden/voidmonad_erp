# -*- coding: utf-8 -*-
from odoo import models, fields, api


class CustomCron(models.Model):
    _inherit = "ir.cron"

    def remind_reviewers(self):
        assignments = self.env["ojm.reviewer.assignment"].sudo().search([('decision', '=', False)])
        for assignment in assignments:
            assignment.remind_reviewer()
