# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime
from slugify import slugify



class Journal(models.Model):
    _name = 'ojm.journal'
    _description = 'journal'
    _rec_name = 'name'
    _inherit = [
        'portal.mixin', 
        'mail.thread.cc', 
        'mail.activity.mixin'
    ]

    code = fields.Char("Code", required=True, default='New')
    name = fields.Char("Title")
    issn = fields.Char("ISSN")
    cover = fields.Image("Banner")
    logo = fields.Image("Logo")
    periodicity = fields.Selection([
        ("yearly", "Yearly"),
        ("monthly", "Monthly"),
        ("weekly", "Weekly"),
    ], default="monthly", string="Periodicity")
    description = fields.Html("Description")
    brief_description = fields.Text("Brief Description")
    mission_scope = fields.Html("Mission & scope")
    editor_ad_board = fields.Html("Editorial board description")
    editorial_policies = fields.Html("Editorial policies")
    inff_author = fields.Html("Information for authors")
    inff_reviewer = fields.Html("Information for reviewers")
    journal_metrics = fields.Html("Journal metrics")
    journal_contact = fields.Html("Contact Details")
    volumes_count = fields.Integer("Volumes", compute='count_volumes', default="0")
    # journal_contact = fields.Html("Contact us")
    active = fields.Boolean("Active", required=True, default=True)
    is_published = fields.Boolean("Published") 
    volumes_ids = fields.One2many(
        string='Volumes',
        comodel_name='ojm.journal.volume',
        inverse_name='journal_id',
    )
    section_ids = fields.One2many(comodel_name='ojm.journal.section', string='Sections', inverse_name='journal_id')
    sequence = fields.Integer("Sequence", required=True, default=0)
    latest_issue = fields.Many2one("ojm.journal.volume", store=False, compute="get_latest_issue_rec", default=False, string="Latest Issue")
    category_id = fields.Many2one("ojm.journal.category", string="Category")
    impact = fields.Float("Impact Factor", default=0, compute="_compute_IF")
    citescore = fields.Float("Cite score", default=0, compute="_computeCiteScore")
    editor_ids = fields.One2many('ojm.editor.line', inverse_name="journal_id", string="Editors")
    
    # editor_ids = fields.Many2many("ojm.editor", string="Editors", domain=lambda self: [('id', 'in', self.env.ref('ojm.group_ojm_editor').users.ids)])
    # editor_in_chief_id = fields.Many2one("ojm.editor", string="Editor in chief", domain=lambda self: [('id', 'in', self.env.ref('ojm.group_ojm_editor').users.ids)])


    def get_editor_in_chief(self):
        for editor_line in self.editor_ids:
            if editor_line.position_id.name.lower() == 'editor in chief':
                return editor_line.editor_id
        return None

    # @api.onchange('editor_ids')
    # def editor_ids_onchange(self):
    #     users = self.env.ref('ojm.group_ojm_editor').users.ids
    #     return {'domain': {'editor_ids': [('id', 'in', users)]}}


    # @api.onchange('editor_in_chief_id')
    # def onchange_editor_in_chief_id(self):
    #     users = self.env.ref('ojm.group_ojm_editor').users.ids
    #     return {'domain': {'editor_in_chief_id': [('id', 'in', users)]}}


    def getYearPublicationCount(self, back_from = 0):
        """
        Get number of yearly publication of year = curent - back_from
        """
        current_year = datetime.now().year
        target_year = current_year - back_from
        publication_count = self.env['ojm.article'].sudo().search_count([
            ('state', '=', 'published'),
            ('publish_year', '=', target_year)
        ])
        return publication_count


    def _compute_IF(self):
        for rec in self:
            curr_year_citations = 0 # total number of current year citations
            publications_y_1 = self.getYearPublicationCount(back_from=1) # number of last year publications
            publications_y_2 = self.getYearPublicationCount(back_from=2) # number of publications 2 years back
            total_publications = publications_y_1 + publications_y_2
            impact_factor = 0
            if total_publications > 0:
                impact_factor = curr_year_citations / total_publications
            rec.impact = impact_factor
    

    def _computeCiteScore(self):
        for rec in self:
            citations_y = 0 # total number of current year citations
            citations_y_1 = 0 # total number of past year citations
            citations_y_2 = 0 # total number of citations 2 years before 
            citations_y_3 = 0 # total number of citations 3 years before
            publications_y = self.getYearPublicationCount(back_from=0) # number of current year publications
            publications_y_1 = self.getYearPublicationCount(back_from=1) # number of last year publications
            publications_y_2 = self.getYearPublicationCount(back_from=2) # number of publications 2 years back
            publications_y_3 = self.getYearPublicationCount(back_from=3) # number of publications 3 years back
            total_publications = publications_y + publications_y_1 + publications_y_2 + publications_y_3
            total_citations = citations_y + citations_y_1 + citations_y_2 + citations_y_3
            cite_score = 0
            if total_publications > 0:
                cite_score = total_citations / total_publications
            rec.citescore = cite_score


    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('ojm.journal.sequence') or 'New'
        result = super(Journal, self).create(vals)
        return result

    def get_volumes(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Volumes',
            'view_mode': 'tree',
            'res_model': 'ojm.journal.volume',
            'domain': [('journal_id', '=', self.id)],
            'context': "{'create': False}"
        }


    def action_publish(self):
        self.is_published = True


    def action_unpublish(self):
        self.is_published = False


    def count_volumes(self):
        for rec in self:
            rec.volumes_count = len(rec.volumes_ids)

        
    def get_latest_issue_rec(self):
        for rec in self:
            rec.latest_issue = rec.get_latest_issue()
    

    def get_latest_issue(self):
        """returns the latest volume issue number"""
        latest_issue = False
        latest = self.env["ojm.journal.volume"].sudo().search([
            ('journal_id', '=', self.id),
            ('is_published', '=', True),
        ], limit=1, order="code desc")
        # the latest one just gettin published is also part of the lst so just 
        # getting the issue before it which is the lastest published issue before the current one.
        latest_issue = latest[0] if latest else False
        return latest_issue
        

class JournalVolume(models.Model):
    _name = 'ojm.journal.volume'
    _description = 'journal volume'
    _rec_name = 'name'
    _inherit = ['portal.mixin', 'mail.thread.cc', 'mail.activity.mixin']

    code = fields.Char("Code", required=True, default='New')
    name = fields.Char("Name", compute="set_volume_name", default="")
    description = fields.Html("Description")
    active = fields.Boolean("Active", required=True, default=True)
    is_published = fields.Boolean("Published")
    journal_id = fields.Many2one("ojm.journal", string="Journal", required=True, ondelete='cascade')
    cover = fields.Image("Volume cover")
    article_ids = fields.One2many(
        string='Articles',
        comodel_name='ojm.article',
        inverse_name='volume_id',
    )
    sequence = fields.Integer("Sequence", required=True, default=0)
    issue_number = fields.Integer("Issue Number", default=0)

    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('ojm.journal.volume.sequence') or 'New'
        vals['issue_number'] = self.compute_issue_number()
        result = super(JournalVolume, self).create(vals)
        return result

    @api.depends("issue_number","journal_id")
    def set_volume_name(self):
        for rec in self:
            rec.name = rec.journal_id.name + " | " + str(datetime.now().year) + " | "+ "Issue: " + str(rec.issue_number)

    def action_publish(self):
        self.issue_number = self.compute_issue_number()
        self.is_published = True

    def action_unpublish(self):
        self.is_published = False

    def compute_issue_number(self):
        """
        evaluate and return journal issue number based on volume number
        and journal periodicity. 
        """ 
        journal_period = self.journal_id.periodicity
        latest_issue = self.journal_id.get_latest_issue()
        issue_number = 1
        if journal_period == 'weekly':
            all_issues = list(range(1,49))
            if latest_issue:
                latest_issue_number = latest_issue.issue_number
                issue_number = latest_issue_number + 1 if latest_issue_number < len(all_issues) else 1
        elif journal_period == 'monthly':
            all_issues = list(range(1,13))
            if latest_issue:
                latest_issue_number = latest_issue.issue_number
                issue_number = latest_issue_number + 1 if latest_issue_number < len(all_issues) else 1
        elif journal_period == 'yearly':
            all_issues = list(range(1,1))
            if latest_issue:
                latest_issue_number = latest_issue.issue_number
                issue_number = latest_issue_number + 1 if latest_issue_number < len(all_issues) else 1
        return issue_number



class JournalSection(models.Model):
    _name = 'ojm.journal.section'
    _description = 'Journal section'
    _rec_name = 'name'
    _order = 'sequence'

    journal_id = fields.Many2one('ojm.journal', string='Journal')
    name = fields.Char('Name')
    description = fields.Html('Description')
    active = fields.Boolean('Active', default=True, required=True)
    is_published = fields.Boolean('Publish')
    sequence = fields.Integer('Sequence')



class JournalSubmissionRule(models.Model):
    _name = 'ojm.submission.rule'
    _description = 'Submission rule'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char('Name')
    code = fields.Char('Code', compute='generate_code')
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True, required=True)
    is_published = fields.Boolean('Published')
    sequence = fields.Integer('Sequence')

    def generate_code(self):
        for rec in self:
            rec.code = ("-".join(str(rec.name).lower().split(" ")))


class JournalCategory(models.Model):
    _name = "ojm.journal.category"
    _description = 'Journal category'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char("Name", required=True)
    description = fields.Html("Description")
    sequence = fields.Integer("Sequence")
    active = fields.Boolean("Active", default=True, required=True)




class AuthorDeclaration(models.Model):
    _name = 'ojm.author.declaration'
    _description = 'Authors declaration'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char("Name", required=True)
    description = fields.Text("Description")
    sequence = fields.Integer("Sequence")
    active = fields.Boolean("Active", default=True, required=True)
