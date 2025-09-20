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

DEFAULT_BG_COLOR = 'rgba(120,120,120,1)'
DEFAULT_LABEL_COLOR = 'rgba(255,255,255,1)'


Titles = [
    ("mr", "Mr."),
    ("mrs", "Mrs."),
    ("ms", "Ms."),
    ("miss", "Miss"),
    ("dr", "Dr."),
    ("prof", "Prof."),
    ("sir", "Sir"),
    ("dame", "Dame"),
    ("rev", "Rev."),
    ("capt", "Capt."),
    ("lt", "Lt."),
    ("sgt", "Sgt."),
    ("hon", "Hon.")
]


COMMENT_TEMPLATE = """
    \n
    {rname}, --- Decision: {rdecision}\n
    \n
    {rcomment}
"""


class Article(models.Model):
    _name = "ojm.article"
    _description = "Article"
    _rec_name = "code"
    _inherit = [
        'mail.thread.cc', 
        'mail.activity.mixin', 
        'mail.thread', 
        'website.seo.metadata', 
        'website.published.multi.mixin', 
        'website.searchable.mixin' 
    ]
    _mail_post_access = 'read'
    _order = "sequence"


    def _compute_my_field_readonly(self):
        return not (
            self.user.has_group("ojm.group_ojm_admin")
        )


    code = fields.Char("Code", required=True, default='New')
    name = fields.Html("Title", readonly=_compute_my_field_readonly)
    short_title = fields.Text("Short title", compute="compute_short_title", default="")
    unformated_abstract = fields.Text("Unformated abstract",  
                                      compute="compute_unformated_abstract", default="")

    # upon type setting
    content = fields.Html('Content', translate=html_translate, sanitize=False)
    snapshot = fields.Html('Snapshot', translate=html_translate, sanitize=False)
    references = fields.Html("References", translate=html_translate, sanitize=False)
    typesetted_document = fields.Many2one("ir.attachment", "Final PDF version")


    def _compute_website_url(self):
        super(Article, self)._compute_website_url()
        for article in self:
            article.website_url = "/journal/%s/article/%s" % (slug(article.journal_id), slug(article))


    def _default_content(self):
        return '''
            <p class="o_default_snippet_text">''' + _("Start writing here...") + '''</p>
        '''
    

    doi = fields.Char("DOI", tracking=True)
    issn = fields.Char("ISSN")
    state = fields.Selection([
        ('incomplete', 'Incomplete'),
        ('back_to_author', 'Back to author'),
        ('author_approved', 'Approved by author'),
        ('saved', 'Saved'),
        ('submitted', 'Submitted'),
        ('under_review', 'Under review'),
        ('under_revision', 'Under Revision'),
        ('revision_submitted', 'Revision submitted'),
        ('revised', 'Revised'),
        ('reviewed', 'Reviewed'),
        ('typesetting', 'TypeSetting'),
        ('published', 'Published'),
        ('revoked', 'Revoked'),
    ], string="Stage", default="incomplete", required=True, tracking=True)
    decision = fields.Selection([
        ('accepted', 'Accepted'),
        ('minor_revisions', 'Minor revisions'),
        ('major_revisions', 'Major revisions'),
        ('rejected', 'Rejected')
    ], string="Final decision")
    editorial_decision_rationale = fields.Text("Editorial decision rationale")
    type_id = fields.Many2one('ojm.article.type', string="Article type", 
                              readonly=_compute_my_field_readonly)
    author_ids = fields.Many2many('ojm.article.author', string="Authors", 
                                  readonly=_compute_my_field_readonly)
    author_names = fields.Char("Author names", default="", compute="get_author_names", 
                               readonly=_compute_my_field_readonly)
    corresponding_author = fields.Many2one("res.users", string="Corresponding author")
    abstract = fields.Html("Abstract", readonly=_compute_my_field_readonly)
    highlights = fields.Html("Highlights", readonly=_compute_my_field_readonly)
    active = fields.Boolean("Active", required=True, default=True) 
    journal_id = fields.Many2one("ojm.journal", string="Journal", ondelete="cascade", 
                                 readonly=_compute_my_field_readonly)
    volume_id = fields.Many2one("ojm.journal.volume", string="Volume", 
                                ondelete="cascade", tracking=True)
    section_id = fields.Many2one("ojm.journal.section", string="Section", ondelete="cascade")
    document_ids = fields.Many2many(
        comodel_name="ir.attachment", 
        string="Data & Images", readonly=_compute_my_field_readonly)
    file_id = fields.Many2one("ir.attachment", string="Manuscript", 
                              readonly=_compute_my_field_readonly)
    sequence = fields.Integer("Sequence", required=True, default=0)
    scope = fields.Text("Scope")
    suggested_reviewer_ids = fields.Many2many('ojm.article.sreviewer', 
                                              string="Suggested reviewers", 
                                              readonly=_compute_my_field_readonly)
    keyword_ids = fields.Many2many('ojm.article.keyword', string="Keywords", 
                                   readonly=_compute_my_field_readonly)
    submitted_by = fields.Many2one('res.users', string='Submitted by', 
                                   default=lambda self: self.env.user.id, 
                                   readonly=_compute_my_field_readonly)
    reviewer_ids = fields.One2many('ojm.reviewer.invitation', 
                                   string='Invited Reviewers', inverse_name="article_id")
    revision_ids = fields.One2many('ojm.article.revision', 
                                   string="Revisions", inverse_name="article_id")
    assignments_ids = fields.One2many('ojm.reviewer.assignment', 
                                    string="Reviewer Assignments", inverse_name="article_id")
    reviewer_invite_count = fields.Integer("Invited Reviewers", compute="count_invited_reviewers", default=0)
    reviewer_assg_count = fields.Integer("Assignments", compute="count_reviewer_assignements", default=0)
    revision_count = fields.Integer("Revisions", compute="count_revisions", default=0)
    citations_count = fields.Integer("Citations", default=0, compute="_computeCitationsCount")
    publish_year = fields.Integer("Publish year",  default=datetime.now().year)
    funding_details = fields.Html("Funding Information", readonly=_compute_my_field_readonly)
    authors_order_ids = fields.One2many("author.order.line", inverse_name="article_id", 
                                        string="Authors orders", 
                                        readonly=_compute_my_field_readonly)
    author_declaration_ids = fields.One2many("author.declaration.line", 
                                             inverse_name="article_id", string="Author declarations", 
                                             readonly=_compute_my_field_readonly)
    is_open = fields.Boolean("Is Open Access", default=True)
    submission_date = fields.Datetime("Submitted on", readonly=_compute_my_field_readonly)
    reviewed_start_date = fields.Datetime("Review started on")
    reviewed_end_date = fields.Datetime("Review end date")
    revision_start_date = fields.Datetime("Revision started on")
    revision_end_date = fields.Datetime("Revision end date")
    type_setting_start_date = fields.Datetime("Typesetting started on")
    type_setting_end_date = fields.Datetime("Typesetting ended on")
    online_first_date = fields.Datetime("Online First Date")
    publish_date = fields.Datetime("Published on")
    revoked_date = fields.Datetime("Revoked on")
    citation_string = fields.Text("How to cite")
    citation_bib = fields.Binary("BIB citation")
    citation_ris = fields.Binary("RIS citation")
    affiliation_line_ids = fields.One2many('ojm.aaffiliation.line', 
                                           inverse_name="article_id", 
                                           string="Author Affiliations", readonly=_compute_my_field_readonly)
    view_count = fields.Integer("View count", default=0, readonly=_compute_my_field_readonly)
    revision_deadline = fields.Date("Revision deadline")
    product_id = fields.Many2one("product.template", "Related Product", required=True)
    order_id = fields.Many2one("sale.order", "Related Order", ondelete="cascade")


    @api.model
    def create(self, vals):
        if vals.get('code', 'New') == 'New':
            vals['code'] = self.env['ir.sequence'].next_by_code('ojm.article.sequence') or 'New'
        rec = super(Article, self).create(vals)
        product = rec.product_id
        partner = rec.corresponding_author.partner_id
        if partner and product:
            order = self.env['sale.order'].create({
                'partner_id': partner.id,
                'order_line': [(0, 0, {
                    'product_id': product.product_variant_id.id, 
                    'product_uom_qty': 1,
                    'price_unit': product.list_price,
                })]
            })
            rec.order_id = order.id
        return rec
    
    
    def write(self, vals):
        if 'state' in list(vals.keys()):
            if vals['state'] == 'submitted':
                vals['submission_date'] = datetime.now()
        result = super(Article, self).write(vals)
        return result


    def count_invited_reviewers(self):
        for rec in self:
            rec.reviewer_invite_count = len(rec.reviewer_ids)


    def count_reviewer_assignements(self):
        for rec in self:
            rec.reviewer_assg_count = len(rec.assignments_ids)


    def count_revisions(self):
        for rec in self:
            rec.revision_count = len(rec.revision_ids)


    def compute_summary_comment(self):
        for rec in self:
            rec.reviewer_comments = ""
            for assignment in rec.assignments_ids:
                if assignment.decision:
                    h = html2text.HTML2Text()
                    h.ignore_links = True
                    h.ignore_emphasis = True
                    if rec.reviewer_comments:
                        rec.reviewer_comments += COMMENT_TEMPLATE.format(
                            rname=assignment.reviewer_id.name, 
                            rdecision=assignment.decision, 
                            rcomment=h.handle(assignment.general_comment).replace("*","").replace("_"," ")
                        )
                    else:
                        rec.reviewer_comments = COMMENT_TEMPLATE.format(
                            rname=assignment.reviewer_id.name, 
                            rdecision=assignment.decision, 
                            rcomment=h.handle(assignment.general_comment).replace("*","").replace("_"," ")
                        )

    
    def get_documents(self):
        files = self.env['ir.attachment'].sudo().search([
            ('id', 'in', self.document_ids.ids)
        ], order="sequence asc")
        return files
    
    def has_non_image_doc(self):
        files = self.env['ir.attachment'].sudo().search([
            ('id', 'in', self.document_ids.ids)
        ], order="sequence asc")
        for file in files:
            if not file.name.lower().startswith('image'):
                return True
        else:
            return False

    
    def _computeCitationsCount(self):
        for rec in self:
            # TODO: research the process of counting article citations use by other journal
            # and maybe event get information on paper who cited the work
            rec.citations_count = 0


    def html_to_text(self, ht):
        h = html2text.HTML2Text()
        h.ignore_links = True
        h.ignore_emphasis = True
        ft = ""
        try:
            if ht:
                ft = h.handle(ht).replace("\n", " ").replace("*", "").replace("_", "")
        except Exception as e:
            return ""
        return ft

    
    def compute_short_title(self):
        for rec in self:
            if rec.name:
                h = html2text.HTML2Text()
                h.ignore_links = True
                h.ignore_emphasis = True
                rec.short_title = h.handle(rec.name).replace("\n", " ").replace("*", "").replace("_", "")
            else:
                rec.short_title = ""
    

    def compute_unformated_abstract(self):
        for rec in self:
            if rec.abstract:
                rec.unformated_abstract = html2text.html2text(rec.abstract).replace("\n", " ").replace("*", "").replace("_", "")
            else:
                rec.unformated_abstract = ""

    
    def action_send_back_to_author(self):
        self.state = 'back_to_author'
    

    def action_send_for_revision(self):
        self.state = 'under_revision'


    def action_author_approved(self):
        self.state = 'author_approved'


    def action_reset(self):
        self.state = 'submitted'


    def action_review(self):
        self.state = 'under_review'
        self.reviewed_start_date = datetime.now()


    def action_typeset(self):
        self.reviewed_end_date = datetime.now()
        self.state = 'typesetting'
        self.type_setting_start_date = datetime.now()


    def action_publish(self):
        self.state = 'published'
        self.type_setting_end_date = datetime.now()
        self.publish_date = datetime.now()

    def action_close_review(self):
        self.state = 'reviewed'
        self.reviewed_end_date = datetime.now()


    def action_close_revisions(self):
        self.state = 'revised'


    def action_send_for_revisions(self):
        self.state = 'under_revision'


    def action_notify_review_end(self):
        # send review completion notification
        reviewer_email_template = self.env.ref('ojm.review_end_notif_email_template')
        reviewer_email_template.send_mail(self.id, force_send=True)

    
    def action_notify_revision_start(self):
        # send revision start notification
        revision_email_template = self.env.ref('ojm.revision_start_notif_email_template')
        revision_email_template.send_mail(self.id, force_send=True)


    def action_revoke(self):
        self.state = 'revoked'
        self.revoked_date = datetime.now()


    def action_open_invitations(self):
        return {
            'name': 'Invited Reviewers',
            'res_model': 'ojm.reviewer.invitation',
            'view_mode': 'tree,form',
            'context':{
                'default_article_id': self.id
            },
            'domain':[('article_id', '=', self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }


    def action_open_assignments(self):
        return {
            'name': 'Reviewer Assignments',
            'res_model': 'ojm.reviewer.assignment',
            'view_mode': 'tree,form',
            'context':{
                'default_article_id': self.id
            },
            'domain':[('article_id', '=', self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }
    

    def action_open_revisions(self):
        return {
            'name': 'Revisions',
            'res_model': 'ojm.article.revision',
            'view_mode': 'tree,form',
            'context':{
                'default_article_id': self.id
            },
            'domain':[('article_id', '=', self.id)],
            'target': 'current',
            'type': 'ir.actions.act_window',
        }
        

    def _notify_email_editor(self):
        reviewer_email_template = self.env.ref('ojm.submission_notif_editor_email_template')
        reviewer_email_template.send_mail(self.id, force_send=True)


    def _notify_email_author(self):
        """Send email notification: shall be used at the end of the submission when submission is at submitted state"""
        mail_template = self.env.ref('ojm.submission_completion_email_template')
        mail_template.send_mail(self.id, force_send=True)
        

    def action_send_email(self):
        self.sudo()._notify_email_author()
        self.sudo()._notify_email_editor()


    def get_author_names(self):
        for rec in self:
            res = rec.get_authors()
            names = ""
            if res:
                names_arr = []
                for x in res:
                    if x and x.name:
                        names_arr.append(x.name)
                names = ", ".join(names_arr)
            rec.author_names = names


    @api.constrains('authors_order_ids')
    def _check_authors_order_ids(self):
        """ 
        make 2 authors do not have the same 
        sequence number, and that order is strict
        """
        for rec in self:
            actual_sequence = []
            for item in rec.authors_order_ids:
                actual_sequence.append(item.sequence)
            good_sequence = list(range(1,len(actual_sequence) + 1))
            actual_sequence.sort()
            if good_sequence != actual_sequence:
                raise exceptions.ValidationError(_('Authors order is invalid, please check and correct'))
            
    
    def get_author_order(self, aid:int):
        for author_order in self.authors_order_ids:
            if author_order.author_id == aid:
                return author_order.sequence
        return 0    
    

    def get_authors(self):
        res = []
        sorted_lines = self.env['author.order.line'].sudo().search([
            ('article_id','=', self.id),
            ('id', 'in', self.authors_order_ids.ids)
        ], order="sequence asc")
        for line in sorted_lines:
            res.append(line.author_id)
        return res


    def get_affiliations(self):
        res_dict = {}
        for item in self.author_ids:
            if item.affiliation_ids:
                for aff in item.affiliation_ids:
                    res_dict[aff.id] = aff.name
        return " * ".join(list(res_dict.values()))


    def get_author_affiliations(self, aid):
        res_dict = {}
        for item in self.author_ids:
            if item.affiliation_ids:
                for aff in item.affiliation_ids:
                    if aff.author_id == aid:
                        res_dict[aff.id] = aff.name
        return " * ".join(list(res_dict.values()))
                

class ArticleData(models.Model):
    _name = 'ojm.article.data'
    _description = 'article data'
    _rec_name = 'name'

    name = fields.Char("Name", related='file_id.name')
    file_id = fields.Many2one("ir.attachment", string="File")
    article_id = fields.Many2one("ojm.article", string="Article")
    active = fields.Boolean('Active', required=True, default=True)


class ArticleType(models.Model):
    _name = 'ojm.article.type'
    _description = 'Article type'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char('Name')
    description = fields.Text('Description')
    active = fields.Boolean('Active', default=True, required=True)
    is_published = fields.Boolean('Publish')
    sequence = fields.Integer('Sequence')


class ArticleFileType(models.Model):
    _name = 'ojm.article.file.type'
    _description = 'Article file type'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char('Name')
    description = fields.Text('Description')
    sextensions = fields.Char("Supported extensions")
    active = fields.Boolean('Active', default=True, required=True)
    is_published = fields.Boolean('Publish')
    sequence = fields.Integer('Sequence')


class ArticleKeyword(models.Model):
    _name = 'ojm.article.keyword'
    _description = 'Article keyword'
    _rec_name = 'name'
    _order = 'sequence'

    name = fields.Char('Name')
    active = fields.Boolean('Active', default=True, required=True)
    is_published = fields.Boolean('Publish')
    sequence = fields.Integer('Sequence')


class CustomAttachment(models.Model):
    _inherit = 'ir.attachment'

    formatted_description = fields.Html("Formatted document description")
    web_title = fields.Char("Web title")
    sequence = fields.Integer("Sequence")


