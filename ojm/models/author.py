# -*- coding: utf-8 -*-

from odoo.addons.ojm.models.constants import Titles
from odoo import models, fields, api, exceptions, _


class ArticleAuthor(models.Model):
    _name = 'ojm.article.author'
    _description = 'article author'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char("Full name", compute="generate_name", default="")
    fname = fields.Char("First Name", default="")
    mname = fields.Char("Middle Name", default="")
    lname = fields.Char("Last Name", default="")
    title = fields.Selection(Titles, default=Titles[0][0], string="Title")
    email = fields.Char("Email")
    orcid = fields.Char("ORCID")
    affiliation_ids = fields.Many2many("ojm.article.affiliation", string="Affiliations")
    active = fields.Boolean('Active', default=True, required=True)
    sequence = fields.Integer('Sequence', default=0, required=True)
   

    def generate_name(self):
        for rec in self:
            all_name = ""
            if rec.fname:
                all_name+=str(rec.fname)
            if rec.mname:
                all_name+=" "+str(rec.mname)
            if rec.lname:
                all_name+=" "+str(rec.lname)
            rec.name = all_name


    def get_articles(self):
        articles = self.env['ojm.article'].sudo().search([('author_ids', 'in', self.id)])
        return articles
    
    
    def get_affiliation_summary(self, article_id):
        affiliation_lines_rec = self.env['ojm.aaffiliation.line'].sudo().search([
                ('article_id', '=', article_id),
                ('author_id', '=', self.id)
            ],limit=1)
        affiliations = affiliation_lines_rec.affiliation_ids
        res = []
        code_ul = "<ul>{}</ul>"
        code_li = "<li>{}</li>"
        items = ""
        for aff in affiliations:
            res.append(aff.name)
        for name in res:
            items+=code_li.format(name)
        return code_ul.format(items)


class AuthorAffiliationLine(models.Model):
    """
    Article affiliation line, to store authors 
    affiliations, as this can vary from
    one article to another...
    """
    _name = 'ojm.aaffiliation.line'

    article_id = fields.Many2one('ojm.article', 'Article')
    author_id = fields.Many2one('ojm.article.author', 'Author')
    affiliation_ids = fields.Many2many(
        'ojm.article.affiliation', string='Affiliations')


class ArticleAffiliations(models.Model):
    _name = 'ojm.article.affiliation'
    _description = 'Article Affiliation'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char("Name")
    description = fields.Char("Description")
    address = fields.Char("Address")
    active = fields.Boolean('Active', default=True, required=True)
    sequence = fields.Integer('Sequence')


class AuthorDeclarationLine(models.Model):
    _name = 'author.declaration.line'
    _description = 'Article declaration line'
    _rec_name = 'declaration_id'

    declaration_id = fields.Many2one('ojm.author.declaration', string='Declaration')
    author_response = fields.Boolean("Author response")
    article_id = fields.Many2one('ojm.article', string='Article')


class AuthorOrder(models.Model):
    _name = 'author.order.line'
    _description = "Authors order"
    _rec_name = "author_id"
    _order = 'sequence'

    article_id = fields.Many2one("ojm.article", string="Article")
    author_id = fields.Many2one('ojm.article.author',string='Author')
    sequence = fields.Integer(string="Order")

    # domain=lambda self: [('author_id', 'in', self.article_id.author_ids.ids)]
