# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.addons.ojm.models.constants import Titles


class ArticleSuggestedReviewer(models.Model):
    _name = 'ojm.article.sreviewer'
    _description = 'Article suggested reviewer'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char("Full name", compute="generate_name", default="")
    fname = fields.Char("First Name", default="")
    mname = fields.Char("Middle Name", default="")
    lname = fields.Char("Last Name", default="")
    title = fields.Selection(Titles, default=Titles[0][0], string="Title")
    email = fields.Char("Email", default="")
    affiliation_ids = fields.Many2many("ojm.article.affiliation", string="Affiliations")
    active = fields.Boolean('Active', default=True, required=True)
    sequence = fields.Integer('Sequence')
    description = fields.Text('Description')


    def generate_name(self):
        for rec in self:
            rec.name = str(rec.fname) 
            +" "
            + str(rec.mname)
            +" "
            + str(rec.lname)


    def get_affiliation_summary(self):
        res = []
        for aff in self.affiliation_ids:
            res.append(aff.name)
        return "; ".join(res)



class ReviewerInvitation(models.Model):
    _name = 'ojm.reviewer.invitation'
    _rec_name = 'name'
    _order = 'sequence'

    article_id = fields.Many2one("ojm.article", string="Article")
    name = fields.Char("Reviewer Name")
    email = fields.Char("Email")
    reviewer_id = fields.Many2one("res.users", string="Reviewer")
    active = fields.Boolean("Active", default=True, required=True)
    sequence = fields.Integer("Sequence")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('declined', 'Declined')
    ], default='draft', string="State")
    decline_link = fields.Char("Declination link", compute="compute_declination_link")
    accept_link = fields.Char("Acceptation link", compute="compute_acceptation_link")
    # reviewer_email = fields.Char(related="reviewer_id.email")
    journal_id = fields.Many2one('ojm.journal', related="article_id.journal_id")

    def compute_declination_link(self):
        for rec in self:
            rec.decline_link = ""

    def compute_acceptation_link(self):
        for rec in self:
            rec.accept_link = ""

    def action_invite(self):
        mail_template = self.env.ref('ojm.reviewer_invitation_email_template')
        mail_template.send_mail(self.id, force_send=True)
        self.state = 'pending'


class ReviewerAssignment(models.Model):
    _name = 'ojm.reviewer.assignment'
    _order = 'create_date desc'
    _rec_name = 'invitation_id'

    invitation_id = fields.Many2one("ojm.reviewer.invitation", string="Invitation")
    article_id = fields.Many2one("ojm.article", related="invitation_id.article_id")
    reviewer_email = fields.Char("Email", related="invitation_id.email")
    reviewer_id = fields.Many2one("res.users", related="invitation_id.reviewer_id", string="Reviewer")
    initial_manuscript = fields.Many2one("ir.attachment", related="invitation_id.article_id.file_id")
    reviewed_manuscript = fields.Many2one("ir.attachment", string="Rewiewed document")
    general_comment = fields.Html("General comment")
    allow_me_to_author = fields.Boolean("Allow author to see reviewer name", default=False)
    comment_severity = fields.Selection([
        ('minor', 'Minor Comment'),
        ('major', 'Major Comment')
    ])
    english_flow = fields.Integer("English flow")
    statistic = fields.Integer("Statistic")
    scientific_rigor = fields.Integer("Scientific Rigor and Novelty")
    impact_relevance = fields.Integer("Impact and Relevance")
    structure_and_content = fields.Integer("Structure and Content")
    references = fields.Integer("References")
    decision = fields.Selection([
        ('accept', 'Accept'),
        ('reject', 'Reject')
    ], string="Reviewer decision")
    journal_id = fields.Many2one('ojm.journal', related="invitation_id.article_id.journal_id")

    def write(self, vals):
        if "decision" in vals.keys():
            self.notify_author()
        res = super(ReviewerAssignment, self).write(vals)
        return res

    def notify_author(self):
        mail_template = self.env.ref('ojm.review_single_end_notif_template')
        mail_template.send_mail(self.id, force_send=True)

    def remind_reviewer(self):
        mail_template = self.env.ref('ojm.remind_reviewer_email_template')
        mail_template.send_mail(self.id, force_send=True)
