# -*- coding: utf-8 -*-
from odoo import models, fields, api
from lxml import html
from bs4 import BeautifulSoup


class OJMEditor(models.Model):
	_name = 'ojm.editor'
	_rec_name = 'name'
	_order = 'sequence'


	name = fields.Char("Name", required=True)
	email = fields.Char("Email", required=True)
	image = fields.Image("Image")
	orcid = fields.Char("ORCID")
	orcid_link = fields.Char("ORCID Link")
	user_id = fields.Many2one("res.users", "Account")
	affiliation_ids = fields.Many2many("ojm.article.affiliation", string="Affiliations")
	bio = fields.Html("Biography")
	sequence = fields.Integer("Sequence", default=0)
	active = fields.Boolean("Active", default=True)

	def action_create_user(self):
		rec = self.env['res.users'].sudo().create({
				"login": self.email,
				"name": self.name,
				"image_1920": self.image
			})
		group_id = self.env.ref('ojm.group_ojm_editor')
		group_id.users = [(4, rec.id)]
		self.user_id = rec



class OJMEditorPosition(models.Model):
	_name = 'ojm.editor.position'
	_rec_name = 'name'

	name = fields.Char("Name", required=True)
	description = fields.Text("Description")
	active = fields.Boolean("Active", default=True)




class OJMEditorLine(models.Model):
	_name = 'ojm.editor.line'
	_rec_name = 'editor_id'

	journal_id = fields.Many2one('ojm.journal', string='Journal')
	editor_id = fields.Many2one('ojm.editor', string="Editor")
	position_id = fields.Many2one("ojm.editor.position", string="Position")

