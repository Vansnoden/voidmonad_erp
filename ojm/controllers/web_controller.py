# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import content_disposition, request, serialize_exception
import  werkzeug
from werkzeug.wrappers import Request, Response
import json
from pprint import pprint
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
import base64
import math


BATCH = 6

class OJMController(http.Controller):
    @http.route('/journals', auth='public', website=True)
    def journals(self, **kw):
        search_text=request.params.get('search_text')
        # page= int(request.params.get('page')) if request.params.get('page') else 1
        # offset = BATCH * (int(page) - 1)
        # limit = BATCH
        domain = [
            ('name', 'ilike', search_text),
            ('active', '=', True),
            ('is_published', '=', True),
        ]
        journals = request.env['ojm.journal'].sudo().search(domain, order="sequence asc")
        categories = []
        for journal in journals:
            if journal.category_id not in categories:
                categories.append(journal.category_id)
        category_ids = [item.id for item in categories]
        # the following is to garantee the ordering according to sequence automatically
        categories = request.env['ojm.journal.category'].sudo().search([('id', 'in', category_ids)], order="sequence asc")
        total_views = 0
        articles = request.env['ojm.article'].sudo().search([('state', '=', 'published'), ('active','=', True)])
        for article in articles:
            total_views+=article.view_count
        merged_data = {}
        first_category = {}
        most_cited = []
        if categories:
            first_category = {
                categories[0]: []
            }
        for journal in journals:
            if journal.category_id:
                if journal.category_id.id == categories[0].id:
                    first_category[categories[0]].append(journal)
        for categ in categories[1:]:
            merged_data[categ] = []
            for journal in journals:
                if journal.category_id.id == categ.id:
                    merged_data[categ].append(journal)
        for journal in journals:
            if journal.latest_issue:
                most_cited.append(journal.latest_issue)
        return request.render("ojm.journals",{
            "journals": journals,
            "journals_count": len(journals),
            "first_category":first_category,
            "merged_data": merged_data,
            "categories": categories,
            # 'pages': list(range(1,pages+1)),
            # 'active_page': page,
            # 'next_page': page + 1 if page < pages else 1,
            # 'previous_page': page - 1 if page > 1 else pages,
            'search': search_text,
            'most_cited': most_cited,
            # 'pages_num': pages,
            'total_views': total_views
        })


    @http.route('/journal/<model("ojm.journal"):journal>', auth='public', website=True)
    def journal_details(self, journal, **kw):
        # journal = request.env["ojm.journal"].sudo().browse(journal_id)
        journal = journal.sudo()
        latest_issue = journal.get_latest_issue()
        other_issues = None
        if latest_issue:
            other_issues = request.env['ojm.journal.volume'].sudo().search([('journal_id', '=', journal.id), ('id', '!=', latest_issue.id)])
        return http.request.render('ojm.journal_details', {
            'journal': journal,
            'other_issues': other_issues[:8] if other_issues else []
        })


    @http.route('/journal/<model("ojm.journal"):journal>/current_issue', auth='public', website=True)
    def current_issue(self, journal, **kw):
        # journal = request.env["ojm.journal"].sudo().browse(journal_id)
        journal = journal.sudo()
        issue = journal.sudo().get_latest_issue()
        search_text=request.params.get('search_text')
        page= int(request.params.get('page')) if request.params.get('page') else 1
        offset = BATCH * (int(page) - 1)
        limit = BATCH
        domain = []
        if issue:
            domain = [
                ('name', 'ilike', search_text),
                ('active', '=', True),
                ('state', '=', 'published'),
                ('volume_id', '=', issue.id)
            ]
        else:
            domain = [
                ('name', 'ilike', search_text),
                ('active', '=', True),
                ('state', '=', 'published'),
                ('volume_id', '=', 0)
            ]
        if issue:
            domain.append(('volume_id', '=', issue.id))
        articles = request.env['ojm.article'].sudo().search(domain, limit=limit, offset=offset, order="publish_date desc")
        pages = math.ceil(len(articles) / BATCH)
        return http.request.render('ojm.journal_issue', {
            'journal': journal,
            'issue': issue,
            'articles': articles,
            'pages': list(range(1,pages+1)),
            'active_page': page,
            'next_page': page + 1 if page < pages else 1,
            'previous_page': page - 1 if page > 1 else pages,
            'search': search_text,
            'pages_num': pages,
        })
    

    @http.route('/journal/<model("ojm.journal"):journal>/archive', auth='public', website=True)
    def archive(self, journal, **kw):
        # journal = request.env["ojm.journal"].sudo().browse(journal_id)
        journal = journal.sudo()
        volume_id = int(request.params.get("volume", "0"))
        volumes = request.env['ojm.journal.volume'].sudo().search([
            ('journal_id', '=', journal.id),
            ('active', '=', True)
        ])
        search_text=request.params.get('search_text')
        page= int(request.params.get('page')) if request.params.get('page') else 1
        offset = BATCH * (int(page) - 1)
        limit = BATCH
        domain = [
            ('name', 'ilike', search_text),
            ('active', '=', True),
            ('state', '=', 'published'),
            ('journal_id', '=', journal.id)
        ]
        if volume_id:
            domain.append(('volume_id', '=', volume_id))
        articles = request.env['ojm.article'].sudo().search(domain, limit=limit, offset=offset, order="publish_date desc")
        pages = math.ceil(len(articles) / BATCH)
        return http.request.render('ojm.journal_archive', {
            'journal': journal,
            'volumes': volumes,
            'volume_id': volume_id,
            'articles': articles,
            'pages': list(range(1,pages+1)),
            'active_page': page,
            'next_page': page + 1 if page < pages else 1,
            'previous_page': page - 1 if page > 1 else pages,
            'search': search_text,
            'pages_num': pages,
        })
        
    
    @http.route('/journal/<model("ojm.journal"):journal>/issue/<int:issue_id>', auth='public', website=True)
    def issue_details(self, journal, issue_id, **kw):
        # journal = request.env["ojm.journal"].sudo().browse(journal_id)
        journal = journal.sudo()
        issue = request.env["ojm.journal.volume"].sudo().browse(issue_id)
        search_text=request.params.get('search_text')
        page= int(request.params.get('page')) if request.params.get('page') else 1
        offset = BATCH * (int(page) - 1)
        limit = BATCH
        domain = [
            ('name', 'ilike', search_text),
            ('active', '=', True),
            ('state', '=', 'published'),
        ]
        if issue:
            domain.append(('volume_id', '=', issue.id))
        articles = request.env['ojm.article'].sudo().search(domain, limit=limit, offset=offset, order="publish_date desc")
        pages = math.ceil(len(articles) / BATCH)
        return http.request.render('ojm.journal_issue', {
            'journal': journal,
            'issue': issue,
            'articles': articles,
            'pages': list(range(1,pages+1)),
            'active_page': page,
            'next_page': page + 1 if page < pages else 1,
            'previous_page': page - 1 if page > 1 else pages,
            'search': search_text,
            'pages_num': pages,
        })
    

    @http.route('/publications', auth='public', website=True)
    def all_pubs(self, **kw):
        search_text=request.params.get('search_text')
        page= int(request.params.get('page')) if request.params.get('page') else 1
        offset = BATCH * (int(page) - 1)
        limit = BATCH
        domain = [
            '|',('name', 'ilike', search_text),
            ('journal_id.name', 'ilike', search_text),
            ('active', '=', True),
            ('state', '=', 'published'),
        ]
        articles = request.env['ojm.article'].sudo().search(domain, limit=limit, offset=offset, order="publish_date desc")
        pages = math.ceil(len(articles) / BATCH)
        return http.request.render('ojm.all_pub', {
            'articles': articles,
            'pages': list(range(1,pages+1)),
            'active_page': page,
            'next_page': page + 1 if page < pages else 1,
            'previous_page': page - 1 if page > 1 else pages,
            'search': search_text,
            'pages_num': pages,
        })
        
    

    @http.route('/journal/<model("ojm.journal"):journal>/about', auth='public', website=True)
    def about(self, journal, **kw):
        journal = journal.sudo()
        # journal = request.env["ojm.journal"].sudo().browse(journal_id)
        return http.request.render('ojm.journal_about', {
            'journal': journal
        })
    

    @http.route('/journal/<model("ojm.journal"):journal>/article/<model("ojm.article"):article>', auth='public', website=True)
    def article_page(self, journal, article, **kw):
        journal = journal.sudo()
        article = article.sudo()
        current_vc = article.view_count
        article.sudo().write({
                'view_count': current_vc + 1
            })
        if article.state == 'published' and article.journal_id.id == journal.id:
            return request.render("ojm.article_page", {
                'article': article
            })
        else:
            return request.redirect('/')
    

    @http.route('/journal/<model("ojm.journal"):journal>/read/<model("ojm.article"):article>', auth='public', website=True)
    def read_article(self, journal, article, **kw):
        journal = journal.sudo()
        article = article.sudo()
        return request.render("ojm.article_pdf_reader", {
            'article': article,
            'journal': journal
        })
    

    @http.route('/journal/submit', methods=['GET'], auth='user', website=True)
    def submit_paper(self, **kw):
        journals = request.env["ojm.journal"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        article_types = request.env["ojm.article.type"].sudo().search([('active', '=', True),('is_published', '=', True)])
        submission_rules = request.env["ojm.submission.rule"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        return http.request.render('ojm.ojm_manuscript_form', {
            'journals': journals,
            'atypes': article_types,
            'submission_rules': submission_rules 
        })

    
    @http.route('/journal/<model("ojm.journal"):journal>/sections', auth='user', website=True)
    def journal_sections(self, journal, **kw):
        journal = journal.sudo()
        journal_sections = request.env["ojm.journal.section"].sudo().search([
            ('journal_id', '=', journal.id),
            ('active', '=', True), 
            ('is_published', '=', True)
        ])
        sections = []
        for section in journal_sections:
            sections.append({
                'id': section.id,
                'name': section.name
            })
        headers = {'Content-Type': 'application/json'}
        body = sections
        return Response(json.dumps(body), headers=headers)
    

    
    @http.route('/web/binary/download_document', type='http', auth="public")
    def download_documents(self, model, field, id, filename=None, **args):
        """ Download link for files stored as binary fields.
        :param str model: name of the model to fetch the binary from
        :param str field: binary field
        :param str id: id of the record from which to fetch the binary
        :param str filename: field holding the file's name, if any
        :returns: :class:`werkzeug.wrappers.Response`
        """
        Model = request.env[model].sudo()
        fields = [field]
        res = Model.search_read([('id','in', [int(id)])], fields=fields)
        res = res[0] if res else None
        if res:
            filecontent = base64.b64decode(res.get(field) or '')
            if not filecontent:
                return request.not_found()
            else:
                if not filename:
                    filename = '%s_%s' % (model.replace('.', '_'), id)
                return request.make_response(filecontent,
                            [('Content-Type', 'application/octet-stream'),
                            ('Content-Disposition', content_disposition(filename))])
        

    
    # accept or reject review
    @http.route('/ojm/reviewer/invite/<int:id>/accept', type='http', auth="user")
    def accept_review_invitation(self, id, **args):
        invitation = request.env['ojm.reviewer.invitation'].sudo().browse(id)
        if invitation:
            if invitation.state != 'accepted':
                invitation.sudo().write({
                        'state': 'accepted',
                        'reviewer_id': request.env.user.id
                    })
                # create assignment
                rec = request.env['ojm.reviewer.assignment'].sudo().search([('invitation_id', '=', id)])
                if not rec:
                    request.env['ojm.reviewer.assignment'].sudo().create({
                            'invitation_id': invitation.id,
                        })
                return request.redirect(f"/ojm/{invitation.article_id.journal_id.id}/rhome")
            else:
                return request.redirect("/")



    @http.route('/ojm/reviewer/invite/<int:id>/decline', type='http', auth="public")
    def decline_review_invitation(self, id, **args):
        invitation = request.env['ojm.reviewer.invitation'].sudo().browse(id)
        if invitation:
            invitation.sudo().write({
                    'state': 'declined'
                })
            return request.redirect("/")
    
