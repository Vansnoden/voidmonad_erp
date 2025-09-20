# -*- coding: utf-8 -*-

import json
from odoo import models, fields, api, exceptions, _
from datetime import datetime
import html2text
from odoo.addons.http_routing.models.ir_http import slug, unslug
from odoo.addons.website.tools import text_from_html
from odoo.tools.json import scriptsafe as json_scriptsafe
from odoo.tools.translate import html_translate
from odoo.addons.website.models.theme_models import Theme



class ArticleRevision(models.Model):
    _name = "ojm.article.revision"
    _rec_name = 'code'

    code = fields.Char("Code", required=True, default='New')
    article_id = fields.Many2one("ojm.article", "Submission")
    title = fields.Text("Title", related='article_id.short_title')
    description = fields.Html("Description")
    author_report = fields.Html("Author report")
    file_id = fields.Many2one("ir.attachment", "Revised File")
    state = fields.Selection([
        ("draft", "Open"),
        ("submitted", "Submitted"),
    ], default="draft")
    journal_id = fields.Many2one('ojm.journal', related="article_id.journal_id")
    submitted_on = fields.Datetime("Submission date", default=datetime.now())

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('ojm.article.revision.sequence') or 'New'
        result = super(ArticleRevision, self).create(vals)
        return result
    