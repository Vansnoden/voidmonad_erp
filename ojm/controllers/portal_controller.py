# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import werkzeug
from collections import OrderedDict
from operator import itemgetter
from markupsafe import Markup

from odoo import conf, http, _
from odoo.exceptions import AccessError, MissingError
from odoo.http import request
from werkzeug.wrappers import Request, Response
import json
from pprint import pprint
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.tools import groupby as groupbyelem
from odoo.osv.expression import OR


class OJMCustomerPortal(CustomerPortal):
    def _prepare_home_portal_values(self, counters):
        values = super()._prepare_home_portal_values(counters)
        if 'submission_count' in counters:
            values['submission_count'] = request.env['ojm.article'].search_count([
                ('submitted_by', '=', request.env.user.id),
                ('active', '=', True),
                ('state', 'not in', [
                    'incomplete',
                    'back_to_author',
                    'author_approved',
                    'saved',
                    'published'
                ])
            ])
        if 'isubmission_count' in counters:
            values['isubmission_count'] = request.env['ojm.article'].search_count([
                ('submitted_by', '=', request.env.user.id),
                ('active', '=', True),
                ('state', 'in', [
                    'incomplete',
                    'back_to_author',
                    'author_approved',
                    'saved',
                ])
            ])

        if 'publication_count' in counters:
            values['publication_count'] = request.env['ojm.article'].search_count([
                ('submitted_by', '=', request.env.user.id),
                ('active', '=', True),
                ('state', '=', 'published')
            ])
        return values

    # ------------------------------------------------------------
    # My Sayans
    # ------------------------------------------------------------

    @http.route(['/my/submissions', '/my/submissions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_submissions(self, page=1, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = self._article_get_searchbar_sortings()
        searchbar_sortings = dict(sorted(self._article_get_searchbar_sortings().items(),
                                         key=lambda item: item[1]["sequence"]))
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }

        searchbar_inputs = self._article_get_searchbar_inputs()
        searchbar_groupby = self._article_get_searchbar_groupby()

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        # default group by value
        if not groupby:
            groupby = 'none'

        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            domain += self._article_get_search_domain(search_in, search)

        domain += [
            ('state', 'not in', [
                'incomplete',
                'back_to_author',
                'author_approved',
                'saved',
                'published'
            ]),
            ('submitted_by', '=', request.env.user.id),
            ('active', '=', True)
        ]
        article_count = request.env['ojm.article'].search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/submissions",
            url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in,
                      'search': search},
            total=article_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        order = self._article_get_order(order, groupby)

        articles = request.env['ojm.article'].search(domain, order=order, limit=self._items_per_page,
                                                     offset=pager['offset'])
        request.session['my_articles_history'] = articles.ids[:100]

        groupby_mapping = self._article_get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if group:
            grouped_articles = [request.env['ojm.article'].concat(*g) for k, g in
                                groupbyelem(articles, itemgetter(group))]
        else:
            grouped_articles = [articles]

        article_states = dict(request.env['ojm.article']._fields['state']._description_selection(request.env))
        if sortby == 'state':
            if groupby == 'none' and grouped_articles:
                grouped_articles[0] = grouped_articles[0].sorted(lambda articles: article_states.get(articles.state))
            else:
                grouped_articles.sort(key=lambda articles: article_states.get(articles[0].state))

        values.update({
            'grouped_articles': grouped_articles,
            'page_name': 'article',
            'default_url': '/my/submissions',
            'article_url': False,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("ojm.portal_my_submissions", values)

    @http.route(['/my/isubmissions', '/my/submissions/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_incomplete_submissions(self, page=1, sortby=None, filterby=None, search=None, search_in='content', groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = self._article_get_searchbar_sortings()
        searchbar_sortings = dict(sorted(self._article_get_searchbar_sortings().items(),
                                         key=lambda item: item[1]["sequence"]))
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }

        searchbar_inputs = self._article_get_searchbar_inputs()
        searchbar_groupby = self._article_get_searchbar_groupby()

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        # default group by value
        if not groupby:
            groupby = 'none'

        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            domain += self._article_get_search_domain(search_in, search)

        domain += [
            ('state', 'in', [
                'incomplete',
                'back_to_author',
                'author_approved',
                'saved'
            ]),
            ('submitted_by', '=', request.env.user.id),
            ('active', '=', True)
        ]
        article_count = request.env['ojm.article'].search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/submissions",
            url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in,
                      'search': search},
            total=article_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        order = self._article_get_order(order, groupby)

        articles = request.env['ojm.article'].search(domain, order=order, limit=self._items_per_page,
                                                     offset=pager['offset'])
        request.session['my_articles_history'] = articles.ids[:100]

        groupby_mapping = self._article_get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if group:
            grouped_articles = [request.env['ojm.article'].concat(*g) for k, g in
                                groupbyelem(articles, itemgetter(group))]
        else:
            grouped_articles = [articles]

        article_states = dict(request.env['ojm.article']._fields['state']._description_selection(request.env))
        if sortby == 'state':
            if groupby == 'none' and grouped_articles:
                grouped_articles[0] = grouped_articles[0].sorted(lambda articles: article_states.get(articles.state))
            else:
                grouped_articles.sort(key=lambda articles: article_states.get(articles[0].state))

        values.update({
            'grouped_articles': grouped_articles,
            'page_name': 'article',
            'default_url': '/my/submissions',
            'article_url': False,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("ojm.portal_my_submissions", values)

    @http.route(['/my/publications', '/my/publications/page/<int:page>'], type='http', auth="user", website=True)
    def portal_my_publications(self, page=1, sortby=None, filterby=None, search=None, search_in='content',
                                         groupby=None, **kw):
        values = self._prepare_portal_layout_values()
        searchbar_sortings = self._article_get_searchbar_sortings()
        searchbar_sortings = dict(sorted(self._article_get_searchbar_sortings().items(),
                                         key=lambda item: item[1]["sequence"]))
        searchbar_filters = {
            'all': {'label': _('All'), 'domain': []},
        }

        searchbar_inputs = self._article_get_searchbar_inputs()
        searchbar_groupby = self._article_get_searchbar_groupby()

        # default sort by value
        if not sortby:
            sortby = 'date'
        order = searchbar_sortings[sortby]['order']

        # default filter by value
        if not filterby:
            filterby = 'all'
        domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']

        # default group by value
        if not groupby:
            groupby = 'none'

        # if date_begin and date_end:
        #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]

        # search
        if search and search_in:
            domain += self._article_get_search_domain(search_in, search)

        domain += [
            ('state', '=', 'published'),
            ('submitted_by', '=', request.env.user.id),
            ('active', '=', True)
        ]
        article_count = request.env['ojm.article'].search_count(domain)
        # pager
        pager = portal_pager(
            url="/my/publications",
            url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in,
                      'search': search},
            total=article_count,
            page=page,
            step=self._items_per_page
        )
        # content according to pager and archive selected
        order = self._article_get_order(order, groupby)

        articles = request.env['ojm.article'].search(domain, order=order, limit=self._items_per_page,
                                                     offset=pager['offset'])
        request.session['my_articles_history'] = articles.ids[:100]

        groupby_mapping = self._article_get_groupby_mapping()
        group = groupby_mapping.get(groupby)
        if group:
            grouped_articles = [request.env['ojm.article'].concat(*g) for k, g in
                                groupbyelem(articles, itemgetter(group))]
        else:
            grouped_articles = [articles]

        article_states = dict(request.env['ojm.article']._fields['state']._description_selection(request.env))
        if sortby == 'state':
            if groupby == 'none' and grouped_articles:
                grouped_articles[0] = grouped_articles[0].sorted(lambda articles: article_states.get(articles.state))
            else:
                grouped_articles.sort(key=lambda articles: article_states.get(articles[0].state))

        values.update({
            'grouped_articles': grouped_articles,
            'page_name': 'article',
            'default_url': '/my/publications',
            'article_url': True,
            'pager': pager,
            'searchbar_sortings': searchbar_sortings,
            'searchbar_groupby': searchbar_groupby,
            'searchbar_inputs': searchbar_inputs,
            'search_in': search_in,
            'search': search,
            'sortby': sortby,
            'groupby': groupby,
            'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
            'filterby': filterby,
        })
        return request.render("ojm.portal_my_submissions", values)

    @http.route(['/my/submission/<int:article_id>'], type='http', auth="user", website=True)
    def portal_my_submission(self, article_id, **kw):
        article_sudo = request.env['ojm.article'].sudo()
        values = article_sudo.browse(article_id)
        return request.render("ojm.portal_my_submission", {
            'submission': values
        })

    # COPIED FROM PROJECT
    # ------------------------------------------------------------
    # My Task
    # ------------------------------------------------------------
    def _article_get_page_view_values(self, submission, access_token, **kwargs):
        page_name = 'submission'
        history = 'my_submissions_history'
        values = {
            'page_name': page_name,
            'article': submission,
            'user': request.env.user,
        }
        return self._get_page_view_values(submission, access_token, values, history, False, **kwargs)

    def _article_get_searchbar_sortings(self):
        return {
            'date': {'label': _('Newest'), 'order': 'create_date desc', 'sequence': 1},
            'name': {'label': _('Title'), 'order': 'name', 'sequence': 2},
            'journal': {'label': _('Journal'), 'order': 'volume_id', 'sequence': 3},
            'state': {'label': _('Stage'), 'order': 'state', 'sequence': 4},
        }

    def _article_get_searchbar_groupby(self):
        values = {
            'none': {'input': 'none', 'label': _('None'), 'order': 1},
            'journal': {'input': 'journal', 'label': _('Journal'), 'order': 2},
            'state': {'input': 'state', 'label': _('Stage'), 'order': 4},
        }
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _article_get_groupby_mapping(self):
        return {
            'journal': 'volume_id',
            'state': 'state',
        }

    def _article_get_order(self, order, groupby):
        groupby_mapping = self._article_get_groupby_mapping()
        field_name = groupby_mapping.get(groupby, '')
        if not field_name:
            return order
        return '%s, %s' % (field_name, order)

    def _article_get_searchbar_inputs(self):
        values = {
            'all': {'input': 'all', 'label': _('Search in All'), 'order': 1},
            'content': {'input': 'content', 'label': Markup(_('Search <span class="nolabel"> (in Content)</span>')),
                        'order': 1},
            'code': {'input': 'code', 'label': _('Search in Ref'), 'order': 1},
            'state': {'input': 'state', 'label': _('Search in Status'), 'order': 5},
        }
        return dict(sorted(values.items(), key=lambda item: item[1]["order"]))

    def _article_get_search_domain(self, search_in, search):
        search_domain = []
        if search_in in ('content', 'all'):
            search_domain.append([('name', 'ilike', search)])
            # search_domain.append([('description', 'ilike', search)])
        if search_in in ('state', 'all'):
            search_domain.append([('state', 'ilike', search)])
        if search_in in ('code', 'all'):
            search_domain.append([('code', 'ilike', search)])
        return OR(search_domain)

    # @http.route(['/my/submissions', '/my/submissions/page/<int:page>'], type='http', auth="user", website=True)
    # def portal_my_articles(self, page=1, sortby=None, filterby=None, search=None, search_in='content', groupby=None,
    #                        **kw):
    #     values = self._prepare_portal_layout_values()
    #     searchbar_sortings = self._article_get_searchbar_sortings()
    #     searchbar_sortings = dict(sorted(self._article_get_searchbar_sortings().items(),
    #                                      key=lambda item: item[1]["sequence"]))
    #
    #     searchbar_filters = {
    #         'all': {'label': _('All'), 'domain': []},
    #     }
    #
    #     searchbar_inputs = self._article_get_searchbar_inputs()
    #     searchbar_groupby = self._article_get_searchbar_groupby()
    #
    #     # extends filterby criteria with project the customer has access to
    #     # projects = request.env['project.project'].search([])
    #     # for project in projects:
    #     #     searchbar_filters.update({
    #     #         str(project.id): {'label': project.name, 'domain': [('project_id', '=', project.id)]}
    #     #     })
    #
    #     # extends filterby criteria with project (criteria name is the project id)
    #     # Note: portal users can't view projects they don't follow
    #     # project_groups = request.env['project.task'].read_group([('project_id', 'not in', projects.ids)],
    #     #                                                         ['project_id'], ['project_id'])
    #     # for group in project_groups:
    #     #     proj_id = group['project_id'][0] if group['project_id'] else False
    #     #     proj_name = group['project_id'][1] if group['project_id'] else _('Others')
    #     #     searchbar_filters.update({
    #     #         str(proj_id): {'label': proj_name, 'domain': [('project_id', '=', proj_id)]}
    #     #     })
    #
    #     # default sort by value
    #     if not sortby:
    #         sortby = 'date'
    #     order = searchbar_sortings[sortby]['order']
    #
    #     # default filter by value
    #     if not filterby:
    #         filterby = 'all'
    #     domain = searchbar_filters.get(filterby, searchbar_filters.get('all'))['domain']
    #
    #     # default group by value
    #     if not groupby:
    #         groupby = 'none'
    #
    #     # if date_begin and date_end:
    #     #     domain += [('create_date', '>', date_begin), ('create_date', '<=', date_end)]
    #
    #     # search
    #     if search and search_in:
    #         domain += self._article_get_search_domain(search_in, search)
    #
    #     # task count
    #     article_count = request.env['ojm.article'].search_count(domain)
    #     # pager
    #     pager = portal_pager(
    #         url="/my/submissions",
    #         url_args={'sortby': sortby, 'filterby': filterby, 'groupby': groupby, 'search_in': search_in,
    #                   'search': search},
    #         total=article_count,
    #         page=page,
    #         step=self._items_per_page
    #     )
    #     # content according to pager and archive selected
    #     order = self._article_get_order(order, groupby)
    #
    #     articles = request.env['ojm.article'].search(domain, order=order, limit=self._items_per_page,
    #                                                  offset=pager['offset'])
    #     request.session['my_articles_history'] = articles.ids[:100]
    #
    #     groupby_mapping = self._article_get_groupby_mapping()
    #     group = groupby_mapping.get(groupby)
    #     if group:
    #         grouped_articles = [request.env['ojm.article'].concat(*g) for k, g in
    #                             groupbyelem(articles, itemgetter(group))]
    #     else:
    #         grouped_articles = [articles]
    #
    #     article_states = dict(request.env['ojm.article']._fields['state']._description_selection(request.env))
    #     if sortby == 'state':
    #         if groupby == 'none' and grouped_articles:
    #             grouped_articles[0] = grouped_articles[0].sorted(lambda articles: article_states.get(articles.state))
    #         else:
    #             grouped_articles.sort(key=lambda articles: article_states.get(articles[0].state))
    #
    #     values.update({
    #         'grouped_articles': grouped_articles,
    #         'page_name': 'article',
    #         'default_url': '/my/submissions',
    #         'article_url': 'submission',
    #         'pager': pager,
    #         'searchbar_sortings': searchbar_sortings,
    #         'searchbar_groupby': searchbar_groupby,
    #         'searchbar_inputs': searchbar_inputs,
    #         'search_in': search_in,
    #         'search': search,
    #         'sortby': sortby,
    #         'groupby': groupby,
    #         'searchbar_filters': OrderedDict(sorted(searchbar_filters.items())),
    #         'filterby': filterby,
    #     })
    #     return request.render("ojm.portal_my_submissions", values)

    @http.route(['/my/submission/<int:article_id>'], type='http', auth="public", website=True)
    def portal_my_article(self, article_id, access_token=None, **kw):
        try:
            article_sudo = self._document_check_access('ojm.article', article_id, access_token)
        except (AccessError, MissingError):
            return request.redirect('/my')

        # ensure attachment are accessible with access token inside template
        for attachment in article_sudo.file_id:
            attachment.generate_access_token()
        values = self._article_get_page_view_values(article_sudo, access_token, **kw)
        return request.render("ojm.portal_my_submission", values)


class PortalController(http.Controller):
    
    # @http.route('/ojm/<int:journal_id>/home', auth='user', website=True)
    # def journal_portal_home(self, journal_id, **kwargs):
    #     journal = request.env['ojm.journal'].sudo().browse(journal_id)
    #     company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
    #     company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
    #     user = request.env.user
    #     submissions = request.env['ojm.article'].sudo().search([('state', 'in', ['submitted', 'under_review', 'typesetting'])])
    #     return request.render("ojm.portal_home",{
    #         'company': company,
    #         'user': user,
    #         'journal': journal,
    #         'submissions': submissions
    #     })


    @http.route('/ojm/<int:journal_id>/ahome', auth='user', website=True)
    def journal_portal_ahome(self, journal_id, **kwargs):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        articles_sent_back_to_author = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'back_to_author')])
        articles_saved = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'saved')])
        articles_incomplete = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'incomplete')])
        articles_waiting_author_approval = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'author_approved')])
        articles_in_process =  request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','in', ['submitted', 'under_review', 'typesetting', 'under_revision', 'revision_submitted', 'revised'])])
        articles_to_revised = request.env["ojm.article"].sudo().search([
            ('submitted_by', '=', user.id),
            ('state', 'in', ['under_revision'])
        ])
        articles_in_revision = request.env["ojm.article"].sudo().search([
            ('submitted_by', '=', user.id),
            ('state', 'in', ['revision_submitted'])
        ])
        return request.render("ojm.author_home",{
            'company': company,
            'user': user,
            'journal': journal,
            'submissions_sent_back_to_author': articles_sent_back_to_author,
            'submissions_incomplete': articles_incomplete,
            'submissions_waiting_author_approval': articles_waiting_author_approval,
            'submissions_in_process': articles_in_process,
            'submissions_saved': articles_saved,
            'submissions_to_revise': articles_to_revised,
            'submission_being_revised': articles_in_revision
        })
    

    @http.route('/ojm/<int:journal_id>/rhome', auth='user', website=True)
    def journal_portal_rhome(self, journal_id, **kwargs):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        invitations = request.env['ojm.reviewer.invitation'].sudo().search([
            ('reviewer_id', '=', user.id),
            ('state','=', 'pending')])
        accepted_inv = request.env['ojm.reviewer.invitation'].sudo().search([
            ('reviewer_id', '=', user.id),
            ('state','=', 'accepted')])
        assignments = request.env['ojm.reviewer.assignment'].sudo().search([
            ('reviewer_id', '=', user.id),
            ('decision', '=', False)
            ])
        completed_ass = request.env['ojm.reviewer.assignment'].sudo().search([
            ('reviewer_id', '=', user.id),
            ('decision', '!=', False)
            ])

        return request.render("ojm.reviewer_home",{
            'company': company,
            'user': user,
            'journal': journal,
            'invitations': invitations,
            'assignments_count': len(assignments),
            'assignments': assignments,
            'completed_ass': completed_ass
        })
     