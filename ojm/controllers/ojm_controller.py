# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import  werkzeug
from werkzeug.wrappers import Request, Response
import json
from pprint import pprint
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo.addons.web.controllers.main import Home as LoginController, ensure_db
from odoo.addons.auth_signup.controllers.main import AuthSignupHome as SignUpController
import base64
from odoo import http, _
from odoo.addons.auth_signup.models.res_users import SignupError
from odoo.addons.web.controllers.main import ensure_db, Home, SIGN_UP_REQUEST_PARAMS
from odoo.addons.base_setup.controllers.main import BaseSetup
from odoo.addons.ojm.models.article import Titles
from odoo.exceptions import UserError
from odoo.http import request
import base64
import copy
import datetime
import functools
import hashlib
import io
import itertools
import json
import logging
import operator
import os
import re
import sys
import tempfile
import unicodedata
from collections import OrderedDict, defaultdict
import time
import babel.messages.pofile
import werkzeug
import werkzeug.exceptions
import werkzeug.utils
import werkzeug.wrappers
import werkzeug.wsgi
from lxml import etree, html
from markupsafe import Markup
from werkzeug.urls import url_encode, url_decode, iri_to_uri
from werkzeug.utils import redirect

import odoo
import odoo.modules.registry
from odoo.api import call_kw
from odoo.addons.base.models.ir_qweb import render as qweb_render
from odoo.modules import get_resource_path, module
from odoo.tools import html_escape, pycompat, ustr, apply_inheritance_specs, lazy_property, float_repr, osutil
from odoo.tools.mimetypes import guess_mimetype
from odoo.tools.translate import _
from odoo.tools.misc import str2bool, xlsxwriter, file_open, file_path
from odoo.tools.safe_eval import safe_eval, time
from odoo import http
from odoo.http import content_disposition, dispatch_rpc, request, serialize_exception as _serialize_exception
from odoo.exceptions import AccessError, UserError, AccessDenied
from odoo.models import check_method_name
from odoo.service import db, security
from pprint import pprint
import requests
from slugify import slugify
from odoo.addons.web.controllers.main import Home as WebHomeBase
import ast


_logger = logging.getLogger(__name__)


ORCID_API_CLIENT_ID = "APP-XHQW5AONEYN97JDX"
ORCID_API_CLIENT_SECRET = "fa043653-ab3d-4ee2-af12-d761b1f4d722"



# FUNCTIONS
def save_authors(env, params):
    authors_data = []
    author_fnames = []
    author_mnames = []
    author_lnames = []
    author_emails = []
    author_titles = []
    author_orders = []
    for k,v in params.items():
        if str(k).startswith('author_fname'):
            author_fnames.append((k,v))
        if str(k).startswith('author_mname'):
            author_mnames.append((k,v))
        if str(k).startswith('author_lname'):
            author_lnames.append((k,v))
        if str(k).startswith('author_email'):
            author_emails.append((k,v))
        if str(k).startswith('author_title'):
            author_titles.append((k,v))
        if str(k).startswith('author_order'):
            author_orders.append((k,v))
    recs = []
    for i in range(0, len(author_fnames)):
        rec = None
        author_data = {
            'fname': author_fnames[i][1],
            'mname': author_mnames[i][1],
            'lname': author_lnames[i][1],
            'email': author_emails[i][1],
            'title': author_titles[i][1],
            'sequence': author_orders[i][1]
        }
        rec = env['ojm.article.author'].sudo().search([
            ('email', '=', author_data['email'])
        ])
        if rec:
            env['ojm.article.author'].sudo().write(author_data)
        else:
            rec = env['ojm.article.author'].sudo().create(author_data)
        recs.append(rec.id)
    return recs


def save_reviewers(env, params):
    reviewers_data = []
    reviewer_fnames = []
    reviewer_mnames = []
    reviewer_lnames = []
    reviewer_emails = []
    reviewer_titles = []
    for k,v in params.items():
        if str(k).startswith('reviewer_fname'):
            reviewer_fnames.append((k,v))
        if str(k).startswith('reviewer_mname'):
            reviewer_mnames.append((k,v))
        if str(k).startswith('reviewer_lname'):
            reviewer_lnames.append((k,v))
        if str(k).startswith('reviewer_email'):
            reviewer_emails.append((k,v))
        if str(k).startswith('reviewer_title'):
            reviewer_titles.append((k,v))
    recs = []
    for i in range(0, len(reviewer_fnames)):
        rec = None
        reviewer_data = {
            'fname': reviewer_fnames[i][1],
            'mname': reviewer_mnames[i][1],
            'lname': reviewer_lnames[i][1],
            'email': reviewer_emails[i][1],
            'title': reviewer_titles[i][1]
        }
        rec = env['ojm.article.sreviewer'].sudo().search([
            ('email', '=', reviewer_data['email'])
        ])
        if rec:
            env['ojm.article.sreviewer'].sudo().write(reviewer_data)
        else:
            rec = env['ojm.article.sreviewer'].sudo().create(reviewer_data)
        recs.append(rec.id)
    pprint(recs)
    return recs



def save_keywords(env, params):
    keywords = params.get('keywords', '')
    keywords = keywords.split(',')
    recs = []
    for keyword in keywords:
        test = str(keyword)
        if test.replace(" ", '') != '':
            rec = env['ojm.article.keyword'].sudo().search([('name', '=', keyword)])
            if not rec:
                rec = env['ojm.article.keyword'].sudo().create({
                    "name": keyword,
                    "is_published": True
                })
                recs.append(rec.id)
            else:
                recs.append(rec[0].id)
    return recs
        



###############################################
def validate_sform_step1(data):
    return {}

def validate_sform_step2(data):
    return {}


def validate_sform_step3(data):
    return {}

def validate_sform_step4(data):
    return {}

def validate_sform_step5(data):
    return {}


def get_submission_form_steps(journal_id, activate:int, submission=None, access:list = [1]):
    return {
        '1': {
            'name': 'Article type',
            'active': False if activate!=1 else True,
            'url' : f'/ojm/{journal_id}/submission/step1?submission_id={submission.id if submission else 0}',
            'access': True if 1 in access else False
        },
        '2': {
            'name': 'Attach files',
            'active': False if activate!=2 else True,
            'url' : f'/ojm/{journal_id}/submission/step2?submission_id={submission.id if submission else 0}',
            'access': True if 2 in access else False
        },
        '3': {
            'name': 'General information',
            'active': False if activate!=3 else True,
            'url' : f'/ojm/{journal_id}/submission/step3?submission_id={submission.id if submission else 0}',
            'access': True if 3 in access else False
        },
        '4': {
            'name': 'Review preferences',
            'active': False if activate!=4 else True,
            'url' : f'/ojm/{journal_id}/submission/step4?submission_id={submission.id if submission else 0}',
            'access': True if 4 in access else False
        },
        '5': {
            'name': 'Manuscript data',
            'active': False if activate!=5 else True,
            'url' : f'/ojm/{journal_id}/submission/step5?submission_id={submission.id if submission else 0}',
            'access': True if 5 in access else False
        }
    }


def validate_submission_step_data(step:int, data:dict):
    if step == 1:
        return validate_sform_step1(data)
    elif step == 2:
        return validate_sform_step2(data)
    elif step == 3:
        return validate_sform_step3(data)
    elif step == 4:
        return validate_sform_step4(data)
    elif step == 5:
        return validate_sform_step5(data)



class OJMMainController(http.Controller):

    # INFORMATION SUBMISSION
    @http.route('/ojm/<int:journal_id>/submission/step1', methods=['POST','GET'], auth='user', website=True)
    def step1(self, journal_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        article_types = request.env["ojm.article.type"].sudo().search([('active', '=', True),('is_published', '=', True)])
        submission = None
        if 'submission_id' in request.params.keys():
            submission = request.env['ojm.article'].sudo().search([('id', '=', int(request.params['submission_id']))])
        
        if request.httprequest.method == "POST":
            #handle data
            if submission:
                submission.sudo().write({
                    "journal_id": journal_id,
                    "type_id": int(request.params.get('atype', '0'))
                })
            else:
                submission = request.env['ojm.article'].sudo().create({
                    "journal_id": journal_id,
                    "type_id": int(request.params.get('atype', '0'))
                })
            return redirect(f"/ojm/{journal_id}/submission/step2?submission_id={submission.id}")
        else:
            return request.render("ojm.sform_step1", {
                'company': company,
                'user': user,
                'journal': journal,
                'steps': get_submission_form_steps(journal_id, activate=1, submission=submission, access=[1]),
                'atypes': article_types,
                'post_url': f'/ojm/{journal_id}/submission/step1',
                'submission': submission,
                'backlink':'#'
            }) 

    
    @http.route('/ojm/<int:journal_id>/submission/step2', methods=['POST','GET'], auth='user', website=True)
    def step2(self, journal_id, submission_id=None, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        article_types = request.env["ojm.article.type"].sudo().search([('active', '=', True),('is_published', '=', True)])
        article_doctypes = request.env["ojm.article.file.type"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        submission = None
        if 'submission_id' in request.params.keys():
            submission = request.env['ojm.article'].sudo().search([('id', '=', int(request.params['submission_id']))])
        if request.httprequest.method == "POST":
            #handle data
            params = request.params
            if 'new_main_manuscript' not in params.keys():
                file_name = params['main_manuscript'].filename 
                file = params['main_manuscript']
                attachment = base64.b64encode(file.read())
                attachment_rec = request.env['ir.attachment'].sudo().create({
                    'name':file_name,
                    'res_name': file_name,
                    'type': 'binary',   
                    'res_model': 'ojm.article',
                    'res_id': submission_id,
                    'datas': attachment,
                    'public': True
                })
                # print(attachment_rec)
                rec = request.env['ojm.article'].sudo().search([('id', '=', int(submission_id))])
                # print(rec)
                rec.sudo().write({
                    'file_id': attachment_rec.id
                })
            elif params['new_main_manuscript']: # parameter defined but not empty
                file_name = params['new_main_manuscript'].filename 
                file = params['new_main_manuscript']
                attachment = file.read() 
                attachment_rec = request.env['ir.attachment'].sudo().create({
                    'name':file_name,
                    'res_name': file_name,
                    'type': 'binary',   
                    'res_model': 'ojm.article',
                    'res_id': submission_id,
                    'datas': attachment,
                    'public': True
                })
                # print(attachment_rec)
                rec = request.env['ojm.article'].sudo().search([('id', '=', int(submission_id))])
                # print(rec)
                rec.sudo().write({
                    'file_id': attachment_rec.id
                })

            return redirect(f"/ojm/{journal_id}/submission/step3?submission_id={submission_id}")
        else:
            return request.render("ojm.sform_step2", {
                'company': company,
                'user': user,
                'journal': journal,
                'steps': get_submission_form_steps(journal_id, activate=2, submission=submission, access=[1,2]),
                'atypes': article_types,
                'post_url': f'/ojm/{journal_id}/submission/step2',
                'submission': submission,
                'article_doctypes': article_doctypes,
                'backlink': f'/ojm/{journal_id}/submission/step1?submission_id={submission_id}',
            })

    
    @http.route('/ojm/<int:journal_id>/submission/step3', methods=['POST','GET'], auth='user', website=True)
    def step3(self, journal_id, submission_id=None, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        article_types = request.env["ojm.article.type"].sudo().search([('active', '=', True),('is_published', '=', True)])
        article_doctypes = request.env["ojm.article.file.type"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        submission = None
        if 'submission_id' in request.params.keys():
            submission = request.env['ojm.article'].sudo().search([('id', '=', int(request.params['submission_id']))])
        if request.httprequest.method == "POST":
            #handle data
            submission.sudo().write({
                "section_id": int(request.params.get("journal_section",0))
            })
            return redirect(f"/ojm/{journal_id}/submission/step4?submission_id={submission_id}")
        else:
            return request.render("ojm.sform_step3", {
                'company': company,
                'user': user,
                'journal': journal,
                'steps': get_submission_form_steps(journal_id, activate=3, submission=submission, access=[1,2,3]),
                'post_url': f'/ojm/{journal_id}/submission/step3',
                'submission': submission,
                'article_doctypes': article_doctypes,
                'backlink': f'/ojm/{journal_id}/submission/step2?submission_id={submission_id}',
            })


    @http.route('/ojm/<int:journal_id>/submission/step4', methods=['POST','GET'], auth='user', website=True)
    def step4(self, journal_id, submission_id=None, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        article_types = request.env["ojm.article.type"].sudo().search([('active', '=', True),('is_published', '=', True)])
        article_doctypes = request.env["ojm.article.file.type"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        submission = None
        if 'submission_id' in request.params.keys():
            submission = request.env['ojm.article'].sudo().search([('id', '=', int(request.params['submission_id']))])
        if request.httprequest.method == "POST":
            #handle data
            # TODO: add connected user as default author before redirecting
            # if not submission.author_ids.ids:
            #     default_author_data = {
            #         "fname": user.name,
            #         "email": user.email,
            #         "sequence": 1,
            #     }
            #     auth_rec = request.env["ojm.article.author"].sudo().search([
            #         ('email', '=', default_author_data['email'])
            #     ], limit=1)
            #     if auth_rec:
            #         auth_rec.sudo().write(default_author_data)
            #     else:
            #         auth_rec = request.env["ojm.article.author"].sudo().create(default_author_data)
                
            #     submission.sudo().write({
            #         "author_ids": [(6,0,[auth_rec.id])]
            #     })
            return redirect(f"/ojm/{journal_id}/submission/step5?submission_id={submission_id}")
        else:
            return request.render("ojm.sform_step4", {
                'company': company,
                'user': user,
                'journal': journal,
                'steps': get_submission_form_steps(journal_id, activate=4, submission=submission, access=[1,2,3,4]),
                'post_url': f'/ojm/{journal_id}/submission/step4',
                'submission': submission,
                'article_doctypes': article_doctypes,
                'backlink': f'/ojm/{journal_id}/submission/step3?submission_id={submission_id}',
                'Titles': Titles
            })


    @http.route('/ojm/<int:journal_id>/submission/step5', methods=['POST','GET'], auth='user', website=True)
    def step5(self, journal_id, submission_id=None, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        article_types = request.env["ojm.article.type"].sudo().search([('active', '=', True),('is_published', '=', True)])
        article_doctypes = request.env["ojm.article.file.type"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        affiliations = request.env["ojm.article.affiliation"].sudo().search([('active', '=', True)])
        submission = None
        if 'submission_id' in request.params.keys():
            submission = request.env['ojm.article'].sudo().search([('id', '=', int(request.params['submission_id']))])
        if request.httprequest.method == "POST":
            #handle data
            keywords_ids = save_keywords(request.env, request.params)
            submission_data = {
                'name': request.params.get('article_full_title','---'),
                'abstract': request.params.get('article_abstract','---'),
                'highlights': request.params.get('highlights','---'),
                'funding_details': request.params.get('funding_details','---'),
                'corresponding_author': request.params.get('corresponding_author','---'),
                'state': 'back_to_author',
                'keyword_ids': [(6,0,keywords_ids)]
            }
            
            for author in submission.author_ids:
                uOrder = int(request.params.get(f'order_{author.id}'))
                aOrderRec = request.env['author.order.line'].sudo().search([
                    ('article_id', '=', submission.id),
                    ('author_id', '=', author.id)
                ])
                if aOrderRec:
                    aOrderRec.sudo().write({
                        "sequence": uOrder
                    }) 
                else:
                   request.env['author.order.line'].sudo().create({
                       'article_id': submission.id,
                       'author_id': author.id,
                       'sequence': uOrder
                   }) 

            submission.sudo().write(submission_data)
            return redirect(f"/ojm/{journal_id}/preview/{submission_id}")
        else:
            return request.render("ojm.sform_step5", {
                'company': company,
                'user': user,
                'journal': journal,
                'steps': get_submission_form_steps(journal_id, activate=5, submission=submission, access=[1,2,3,4,5]),
                'post_url': f'/ojm/{journal_id}/submission/step5',
                'submission': submission,
                'article_doctypes': article_doctypes,
                'backlink': f'/ojm/{journal_id}/submission/step4?submission_id={submission_id}',
                'Titles': Titles,
                'affiliations': affiliations
            })


    
    @http.route('/ojm/<int:journal_id>/submission/confirm', methods=['POST','GET'], auth='user', website=True)
    def confirm_submission(self, journal_id, submission_id=None, **kw):
        return request.render("ojm.sform_confirm", {})


    @http.route('/ojm/<int:journal_id>/overview', auth='user', website=True)
    def journal_overview(self, journal_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        articles_sent_back_to_author = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'back_to_author')])
        articles_incomplete = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'incomplete')])
        articles_waiting_author_approval = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'author_approved')])
        articles_in_process =  request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','in', ['submitted', 'under_review', 'typesetting'])])
        return request.render("ojm.portal_journal_overview",{
            'company': company,
            'user': user,
            'journal': journal,
            'submissions_sent_back_to_author': articles_sent_back_to_author,
            'submissions_incomplete': articles_incomplete,
            'submissions_waiting_author_approval': articles_waiting_author_approval,
            'submissions_in_process': articles_in_process,
        })


    @http.route('/ojm/get_attachments/<int:submission_id>', auth='user', website=True, csrf=False)
    def get_submission_attachments(self, submission_id, **kw):
        rec = request.env['ojm.article'].sudo().search([('id', '=', int(submission_id))])
        doc_ids = []
        doc_data = []
        if rec:
            doc_ids = rec.document_ids.ids
            doc_data = request.env['ir.attachment'].sudo().search_read([('id', 'in', doc_ids)], fields=[
                "name",
                "mimetype",
                "file_size",
                "create_date"
            ])
        ndocdata = []
        for oitem in doc_data:
            nitem = {}
            for k,v in oitem.items():
                if k=="create_date":
                    nitem[k] = v.strftime("%Y/%m/%d %H:%M:%S")
                else:
                    nitem[k] = v
            nitem['tname'] = nitem['name'].split('_')[0]
            nitem['fname'] = ' '.join(nitem['name'].split('_')[1:])
            ndocdata.append(nitem)
        headers = {'Content-Type': 'application/json'}
        body = {
            "data": ndocdata
        }
        return Response(json.dumps(body), headers=headers)

    @http.route('/ojm/delete_attachment/<int:sid>/<int:id>', auth='user', website=True, csrf=False)
    def delete_submission_attachments(self, sid, id, **kw):
        arec = request.env['ir.attachment'].sudo().browse(id)
        if arec:
            print("######DELETING----{arec}")
            arec.sudo().unlink()
        headers = {'Content-Type': 'application/json'}
        body = {
            "data": True
        }
        return Response(json.dumps(body), headers=headers)
    
    @http.route('/ojm/delete_author/<int:aid>', auth='user', website=True, csrf=False)
    def delete_author(self, aid, **kw):
        arec = request.env['ojm.article.author'].sudo().browse(aid)
        if arec:
            arec.sudo().unlink()
        headers = {'Content-Type': 'application/json'}
        body = {
            "data": True
        }
        return Response(json.dumps(body), headers=headers) 
    

    @http.route('/ojm/delete_reviewer/<int:rid>', auth='user', website=True, csrf=False)
    def delete_reviewer(self, rid, **kw):
        arec = request.env['ojm.article.sreviewer'].sudo().browse(rid)
        if arec:
            arec.sudo().unlink()
        headers = {'Content-Type': 'application/json'}
        body = {
            "data": True
        }
        return Response(json.dumps(body), headers=headers) 


    @http.route('/ojm/upload_files', auth='user', website=True, csrf=False)
    def upload_submission_attachments(self, **kw):
        print("########PARAMS########")
        params = request.params
        file_name = params['other_attachment'].filename 
        file_name = params['doctype'] +"_"+ "_".join(file_name.lower().split(" "))   
        submission_id = params['submission_id'] 
        file = params['other_attachment']
        attachment = base64.b64encode(file.read()) 
        # print(f"ATTACHMENT -- {attachment}")
        attachment_rec = request.env['ir.attachment'].sudo().create({
            'name':file_name,
            'res_name': file_name,
            'type': 'binary',   
            'res_model': 'ojm.article',
            'res_id': submission_id,
            'datas': attachment,
            'public': True
        })
        # print(attachment_rec)
        rec = request.env['ojm.article'].sudo().search([('id', '=', int(submission_id))])
        # print(rec)
        res = rec.sudo().write({
            'document_ids': [(6,0, rec.document_ids.ids + [attachment_rec.id])]
        })
        
        if res:
            headers = {'Content-Type': 'application/json'}
            body = {
                "saved": True,
                "message": "file uploaded"
            }
            return Response(json.dumps(body), headers=headers) 


    @http.route('/ojm/get_authors/<int:submission_id>', auth='user', website=True, csrf=False)
    def get_submission_authors(self, submission_id, **kw):
        rec = request.env['ojm.article'].sudo().search([('id', '=', int(submission_id))])
        doc_ids = []
        doc_data = []
        if rec:
            doc_ids = rec.author_ids.ids
            docs = rec.author_ids
            doc_data = request.env['ojm.article.author'].sudo().search_read([('id', 'in', doc_ids)], fields=[
                "name",
                "email",
                "sequence",
                "title",
                "id"
            ])
        for item in doc_data:
            irec = None
            for i in docs:
                if i.id == int(item['id']):
                    irec = i
                    break
            for title in Titles:
                if title[0] == item['title']:
                    item['title'] = title[1]
            item['author_ids'] = list(rec.author_ids.ids)
            item['order'] = rec.get_author_order(item['id'])
            item['affiliation_summary'] = irec.get_affiliation_summary(rec.id)
        headers = {'Content-Type': 'application/json'}
        
        body = {
            "data": doc_data
        }
        return Response(json.dumps(body), headers=headers) 
    

    @http.route('/ojm/get_affiliations', auth='public', website=True, csrf=False)
    def get_affiliations(self, **kw):
        search = params = request.params.get("search", '')
        if search:
            doc_data = request.env['ojm.article.affiliation'].sudo().search_read([
                ('name', 'ilike', search)
            ], fields=[
                    "id",
                    "name",
                    "description",
                ])
        else:
            doc_data = request.env['ojm.article.affiliation'].sudo().search_read([], fields=[
                    "id",
                    "name",
                    "description",
                ])
        headers = {'Content-Type': 'application/json'}
        body = {
            "data": doc_data
        }
        return Response(json.dumps(body), headers=headers) 


    @http.route('/ojm/save_affiliation', auth='user', website=True, csrf=False)
    def save_affiliation(self, **kw):
        params = request.params  
        aff_data = {
            'name': params.get('name', ''),
            'description': params.get('description', ''),
            'address': params.get('address', ''),
        }
        rec = request.env['ojm.article.affiliation'].sudo().search([
            ('name', 'ilike', aff_data['name']),
            ('address', 'ilike', aff_data['address'])
        ])
        if not rec:
            rec = request.env['ojm.article.affiliation'].sudo().create(aff_data)

        headers = {'Content-Type': 'application/json'}
        body = {
            "saved": True,
            "message": "affiliation added successfully"
        }
        return Response(json.dumps(body), headers=headers) 

    @http.route('/ojm/save_aff', auth='user',  website=True, csrf=False)
    def save_aff(self, submission_id=0, **kw):
        params = request.params  
        name = params.get('name')
        description  = params.get("description")
        rec = request.env["ojm.article.affiliation"].sudo().search([
            ('name', 'ilike', name)
        ])
        if not rec:
            rec = request.env["ojm.article.affiliation"].sudo().create({
                'name': name,
                'description': description
            })
        headers = {'Content-Type': 'application/json'}
        body = {
            "saved": True,
            "message": "author added"
        }
        return Response(json.dumps(body), headers=headers) 


    @http.route('/ojm/author_declarations/<int:submission_id>', auth='user', website=True, csrf=False)
    def save_declaration(self, submission_id, **kw):
        params = request.params  
        declarations = request.env['ojm.author.declaration'].sudo().search([
            ('active', '=', True)
        ])
        if submission_id:
            declaration_line_data = []
            for declaration in declarations:
                declaration_line_data = {
                    "article_id": submission_id,
                    "declaration_id": declaration.id,
                    "author_response": bool(params.get(f'dec_{declaration.id}', False))
                }
                request.env['author.declaration.line'].sudo().create(declaration_line_data)

            headers = {'Content-Type': 'application/json'}
            body = {
                "saved": True,
                "message": "author added"
            }
            return Response(json.dumps(body), headers=headers) 

    @http.route('/ojm/save_author', auth='user', website=True, csrf=False)
    def save_author(self, submission_id=0, **kw):
        params = request.params  
        submission_id = int(params['submission_id']) 
        submission_rec = None
        if submission_id:
            submission_rec = request.env['ojm.article'].sudo().search([('id', '=', submission_id)])
        if submission_rec:
            author_data = {
                'fname': params.get('fname', ''),
                'mname': params.get('mname', ''),
                'lname': params.get('lname', ''),
                'email': params.get('email', ''),
                'title': params.get('title', ''),
                'orcid': params.get('orcid', ''),
                'sequence': params.get('sequence', ''),
            }

            # REMOVING AUTHORS DUPLICATE CHECK
            # rec = request.env['ojm.article.author'].sudo().search([
            #     ('email', '=', author_data['email'])
            # ])
            # if rec:
            #     request.env['ojm.article.author'].sudo().write(author_data)
            # else:
            rec = request.env['ojm.article.author'].sudo().create(author_data)
            
            submission_rec.sudo().write({
                "author_ids": [(6,0, submission_rec.author_ids.ids + [rec.id])]
            })

            print("GOT AFF: --> ", params.get('aff'))
            aff_list = [ int(x) for x in ast.literal_eval(params.get('aff'))]
            print("AFF LIST: --> ", aff_list)

            if aff_list:
                aff_rec = request.env['ojm.aaffiliation.line'].sudo().create({
                        'author_id': rec.id,
                        'article_id': submission_rec.id,
                        'affiliation_ids': [(6,0, aff_list)]
                    })
            headers = {'Content-Type': 'application/json'}
            body = {
                "saved": True,
                "message": "author added"
            }
            return Response(json.dumps(body), headers=headers) 



    @http.route('/ojm/get_sreviewers/<int:submission_id>', auth='user', website=True, csrf=False)
    def get_submission_sreviewers(self, submission_id, **kw):
        rec = request.env['ojm.article'].sudo().search([('id', '=', int(submission_id))])
        doc_ids = []
        doc_data = []
        if rec:
            doc_ids = rec.suggested_reviewer_ids.ids
            doc_data = request.env['ojm.article.sreviewer'].sudo().search_read([('id', 'in', doc_ids)], fields=[
                "name",
                "email",
                "sequence",
                "title"
                # "create_date"
            ])
        for item in doc_data:
            for title in Titles:
                if title[0] == item['title']:
                    item['title'] = title[1]
        headers = {'Content-Type': 'application/json'}
        body = {
            "data": doc_data
        }
        return Response(json.dumps(body), headers=headers) 



    @http.route('/ojm/save_sreviewer', auth='user', website=True, csrf=False)
    def save_reviewer(self, submission_id=0, **kw):
        params = request.params  
        submission_id = int(params['submission_id']) 
        # print(f"###### SUB ID: {submission_id} ####")
        submission_rec = None
        if submission_id:
            submission_rec = request.env['ojm.article'].sudo().search([('id', '=', submission_id)])
        if submission_rec:
            rev_data = {
                'fname': params.get('fname', ''),
                'mname': params.get('mname', ''),
                'lname': params.get('lname', ''),
                'email': params.get('email', ''),
                'title': params.get('title', ''),
                'description': params.get('comment', ''),
                # 'sequence': int(params.get('sequence', '0')),
                # 'affiliation_ids': 
            }
            # REMOVING DUPLICATES CHECK, CONFLICTING
            # print(f"###### REV DATA: {rev_data} ####")
            # rec = request.env['ojm.article.sreviewer'].sudo().search([
            #     ('email', '=', rev_data['email'])
            # ])
            # if rec:
            #     request.env['ojm.article.sreviewer'].sudo().write(rev_data)
            # else:
            rec = request.env['ojm.article.sreviewer'].sudo().create(rev_data)
            
            submission_rec.sudo().write({
                "suggested_reviewer_ids": [(6,0, submission_rec.suggested_reviewer_ids.ids + [rec.id])]
            })

            headers = {'Content-Type': 'application/json'}
            body = {
                "saved": True,
                "message": "reviewer added"
            }
            return Response(json.dumps(body), headers=headers) 



    
    @http.route('/ojm/<int:journal_id>/save_progress/<int:submission_id>', methods=['POST'], type='http', auth='user', csrf=False, website=True)
    def save_progress(self, journal_id, submission_id, **kw):
        params = json.loads(str((list(request.params.keys())[0])))
        author_ids = save_authors(request.env, params)
        reviewer_ids = save_reviewers(request.env, params)
        submission_data = {
            'journal_id': int(journal_id),
            'section_id': int(params.get('journal_section', False)),
            'type_id': int(params.get('atype', False)),
            'name': params.get('article_full_title','---'),
            'abstract': params.get('article_abstract','---'),
            'author_ids': [(6,0,author_ids)],
            'suggested_reviewer_ids': [(6, 0, reviewer_ids)],
            'state': 'incomplete'
        }
        # if  not (
        #         submission_data['journal_id'] and \
        #         submission_data['section_id'] != -1 and \
        #         submission_data['type_id'] != -1 and \
        #         submission_data['name'] and \
        #         submission_data['abstract'] and \
        #         submission_data['author_ids'] and \
        #         submission_data['suggested_reviewer_ids']\
        #     ):
        #     headers = {'Content-Type': 'application/json'}
        #     body = {
        #         "saved": False,
        #         "id": 0,
        #         "error": "Required fiels is not defined"
        #     }
        #     return Response(json.dumps(body), headers=headers) 
                
        rec = None
        if submission_id:
            rec = request.env['ojm.article'].sudo().search([('id', '=', int(submission_id))])
            if rec:
                rec[0].sudo().write(submission_data)
        else:
            rec = request.env['ojm.article'].sudo().create(submission_data) 

        # TODO: manage file upload via javascript
        attachments = request.env['ir.attachment'].sudo().search_read([
                ('id', 'in', rec.document_ids.ids)
            ], 
            fields=['name','mimetype','file_size','type','local_url'])
        headers = {'Content-Type': 'application/json'}
        body = {
            "saved": True,
            "id": rec.id,
            # "attachments": attachments
        }
        return Response(json.dumps(body), headers=headers)        

    
    @http.route('/ojm/<int:journal_id>/submit_data', methods=['POST','GET'], auth='user', website=True)
    def submit_paper_data(self, journal_id, **kw):
        params = request.params
        submission_id = int(params.get('submission_id', '0'))
        print(f"### SUBMISSION --> {submission_id}")
        author_ids = save_authors(request.env, params)
        reviewer_ids = save_reviewers(request.env, params)
        keywords_ids = save_keywords(request.env, params)
        pprint(f"SAVED REVIEWERS : {reviewer_ids}")
        submission_data = {
            'journal_id': int(journal_id),
            'section_id': int(params.get('journal_section', '0')),
            'type_id': int(params.get('atype', '0')),
            'name': params.get('article_full_title','---'),
            'abstract': params.get('article_abstract','---'),
            'author_ids': [(6,0,author_ids)],
            'suggested_reviewer_ids': [(6,0, reviewer_ids)],
            'state': 'back_to_author',
            'keyword_ids': [(6,0,keywords_ids)]
        }
        rec = None
        if submission_id:
            rec = request.env['ojm.article'].sudo().search([('id', '=', int(submission_id))])
            if rec:
                rec[0].sudo().write(submission_data)
        else:
            rec = request.env['ojm.article'].sudo().create(submission_data) 

        # file_name = params['manuscript'].filename    
        # file = params['manuscript']
        # attachment = file.read() 
        # attachment_id = request.env['ir.attachment'].sudo().create({
        #     'name':file_name,
        #     'res_name': file_name,
        #     'type': 'binary',   
        #     'res_model': 'ojm.article',
        #     'res_id': rec.id,
        #     'datas': attachment
        # })
        # rec.sudo().write({
        #     'file_id': attachment_id
        # })
        other_files = request.httprequest.files.getlist('others')
        for attachment in other_files:
            attached_file = attachment.read()
            attachment_rec = request.env['ir.attachment'].sudo().create({
                'name': attachment.filename,
                'res_model': 'ojm.article',
                'res_id': rec.id,
                'type': 'binary',
                'datas': attached_file,
                'public': True
            })
            rec.sudo().write({
                'document_ids': [(6,0,[attachment_rec.id])]
            })
            
        # journals = request.env["ojm.journal"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        # article_types = request.env["ojm.article.type"].sudo().search([('active', '=', True),('is_published', '=', True)])
        # submission_rules = request.env["ojm.submission.rule"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        # good_submission = True
        return redirect(f"/ojm/{journal_id}/preview/{rec.id}")


    @http.route('/ojm/<int:journal_id>/preview/<int:submission_id>', methods=['POST','GET'], auth='user', website=True)
    def preview_and_confirm(self, journal_id, submission_id, **kw):
        submission = request.env['ojm.article'].sudo().search([('id', '=', submission_id)])
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        author_declarations = request.env['ojm.author.declaration'].sudo().search([
            ('active', '=', True)
        ])
        if request.httprequest.method == "POST":
            selected_value = request.params.get('user_decision', '')
            if selected_value == "save":
                submission.sudo().write({
                    'state': 'saved'
                })
            elif selected_value == "confirm":
                submission.sudo().write({
                    'state': 'submitted'
                })
                submission.sudo().action_send_email() # notify corresponding author by mail
            else:
                submission.sudo().write({
                    "active": False
                })
            return redirect(f"/ojm/{journal_id}/ahome")
        return request.render("ojm.ojm_submission_preview", {
            "submission": submission,
            "authors": [],
            "reviewers": [],
            'company': company,
            'user': user,
            'journal': journal,
            'author_declarations': author_declarations
        })
    

    @http.route('/ojm/<int:journal_id>/in_preview/<int:submission_id>', methods=['POST','GET'], auth='user', website=True)
    def preview_inprocess_sub(self, journal_id, submission_id, **kw):
        submission = request.env['ojm.article'].sudo().search([('id', '=', submission_id)])
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        return request.render("ojm.ojm_insubmission_preview", {
            "submission": submission,
            "authors": [],
            "reviewers": [],
            'company': company,
            'user': user,
            'journal': journal,
        })


    @http.route('/ojm/<int:journal_id>/reviewed/<int:submission_id>', methods=['POST','GET'], auth='user', website=True)
    def view_reviews(self, journal_id, submission_id, **kw):
        submission = request.env['ojm.article'].sudo().search([('id', '=', submission_id)])
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        return request.render("ojm.ojm_reviewer_comments", {
            "submission": submission,
            "authors": [],
            "reviewers": [],
            'company': company,
            'user': user,
            'journal': journal,
        })


    @http.route('/ojm/<int:journal_id>/saved', methods=['POST','GET'], auth='user', website=True)
    def submission_saved_for_later(self, journal_id, **kw):
        submissions = request.env['ojm.article'].sudo().search([('state', 'in', ['saved'])])
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        return request.render("ojm.portal_saved_submission", {
            "submissions": submissions,
            'company': company,
            'user': user,
            'journal': journal,
        })
    
    
    @http.route('/ojm/<int:journal_id>/inprocess', methods=['POST','GET'], auth='user', website=True)
    def submission_in_process(self, journal_id, **kw):
        user = request.env.user
        submissions = request.env['ojm.article'].sudo().search([
            ('state', 'in', ['submitted', 'under_review', 'under_revision', 'revision_submitted', 'revised', 'reviewed', 'typesetting', 'published', 'revoked']),
            ('submitted_by', '=', user.id)
        ])
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        # if request.httprequest.method == "POST":
        #     selected_value = request.params.get('user_decision', '')
        #     if selected_value == "confirm":
        #         submission.sudo().write({
        #             'state': 'submitted'
        #         })
        #     else:
        #         submission.sudo().unlink()
        #     return redirect(f"/ojm/{journal_id}/home")
        return request.render("ojm.portal_inprocess_submission", {
            "submissions": submissions,
            'company': company,
            'user': user,
            'journal': journal,
        })
    

    @http.route('/ojm/<int:journal_id>/in_revision', methods=['POST','GET'], auth='user', website=True)
    def submission_in_revision(self, journal_id, **kw):
        user = request.env.user
        submissions = request.env['ojm.article'].sudo().search([
            ('state', 'in', ['revision_submitted']),
            ('submitted_by', '=', user.id)
        ])
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        # if request.httprequest.method == "POST":
        #     selected_value = request.params.get('user_decision', '')
        #     if selected_value == "confirm":
        #         submission.sudo().write({
        #             'state': 'submitted'
        #         })
        #     else:
        #         submission.sudo().unlink()
        #     return redirect(f"/ojm/{journal_id}/home")
        return request.render("ojm.portal_in_revision_submission", {
            "submissions": submissions,
            'company': company,
            'user': user,
            'journal': journal,
        })


    @http.route('/ojm/<int:journal_id>/to_revise', methods=['POST','GET'], auth='user', website=True)
    def submission_to_revise(self, journal_id, **kw):
        user = request.env.user
        submissions = request.env['ojm.article'].sudo().search([
            ('state', 'in', ['under_revision']),
            ('submitted_by', '=', user.id)
        ])
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        # if request.httprequest.method == "POST":
        #     selected_value = request.params.get('user_decision', '')
        #     if selected_value == "confirm":
        #         submission.sudo().write({
        #             'state': 'submitted'
        #         })
        #     else:
        #         submission.sudo().unlink()
        #     return redirect(f"/ojm/{journal_id}/home")
        return request.render("ojm.portal_in_revision_submission", {
            "submissions": submissions,
            'company': company,
            'user': user,
            'journal': journal,
        })
    

    @http.route('/ojm/<int:journal_id>/in_revision/<int:submission_id>', methods=['POST','GET'], auth='user', website=True)
    def submission_in_revision_details(self, journal_id, submission_id, **kw):
        user = request.env.user
        submission = request.env['ojm.article'].sudo().search([('id', '=',submission_id)])
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        # if request.httprequest.method == "POST":
        #     selected_value = request.params.get('user_decision', '')
        #     if selected_value == "confirm":
        #         submission.sudo().write({
        #             'state': 'submitted'
        #         })
        #     else:
        #         submission.sudo().unlink()
        #     return redirect(f"/ojm/{journal_id}/home")
        return request.render("ojm.portal_revision_details", {
            "submission": submission,
            'company': company,
            'user': user,
            'journal': journal,
        })
    
    @http.route('/ojm/<int:journal_id>/revision/submit/<int:submission_id>', methods=['POST','GET'], auth='user', website=True)
    def post_revision(self, journal_id, submission_id, **kw):
        user = request.env.user
        submission = request.env['ojm.article'].sudo().search([('id', '=',submission_id)])
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        if request.httprequest.method == "POST":
            file_name = request.params['ufile'].filename 
            file = request.params['ufile']
            attachment = file.read() 
            attachment_rec = request.env['ir.attachment'].sudo().create({
                'name':file_name,
                'res_name': file_name,
                'type': 'binary',   
                'res_model': 'ojm.article.revision',
                'res_id': submission_id,
                'datas': attachment,
                'public': True
            })
            # print(attachment_rec)
            revision_rec = request.env['ojm.article.revision'].sudo().create({
                "article_id": submission.id,
                "author_report": request.params["acomment"],
                "state": "submitted"
            })
            # print(rec)
            revision_rec.sudo().write({
                'file_id': attachment_rec.id
            })
            submission.sudo().write({
                "revision_ids": [(6,0,[revision_rec.id])],
                "state": "revision_submitted"
            })
        return redirect(f"/ojm/{journal_id}/in_revision")
    

    @http.route('/ojm/<int:journal_id>/deleteba/<int:submission_id>', methods=['POST', 'GET'], auth='user', website=True)
    def delete_basubmission(self, journal_id, submission_id, **kw):
        request.env['ojm.article'].sudo().search([('id', '=',submission_id)]).unlink()
        pprint(request.params)
        return redirect(f"/ojm/{journal_id}/btauthor")
    

    @http.route('/ojm/<int:journal_id>/delete/<int:submission_id>', methods=['POST', 'GET'], auth='user', website=True)
    def delete_insubmission(self, journal_id, submission_id, **kw):
        request.env['ojm.article'].sudo().search([('id', '=',submission_id)]).unlink()
        pprint(request.params)
        return redirect(f"/ojm/{journal_id}/insubmissions")


    @http.route('/ojm/<int:journal_id>/edit/<int:submission_id>', methods=['POST', 'GET'], auth='user', website=True)
    def edit_preview(self, journal_id, submission_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        articles_sent_back_to_author = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'back_to_author')])
        articles_incomplete = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'incomplete')])
        # articles_waiting_author_approval = request.env['ojm.article'].sudo().search([
        #     ('submitted_by', '=', user.id),
        #     ('state','=', 'author_approved')])
        articles_in_process =  request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','in', ['submitted', 'under_review', 'typesetting'])])
        article_types = request.env["ojm.article.type"].sudo().search([('active', '=', True),('is_published', '=', True)])
        submission_rules = request.env["ojm.submission.rule"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        submission = request.env['ojm.article'].sudo().search([('id', '=', submission_id)])
        # journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        article_doctypes = request.env["ojm.article.file.type"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        
        return request.render("ojm.portal_edit_submission", {
            "submission": submission,
            "authors": [],
            "reviewers": [],
            'company': company,
            'user': user,
            'company': company,
            'user': user,
            'journal': journal,
            'submissions_sent_back_to_author': articles_sent_back_to_author,
            'submissions_incomplete': articles_incomplete,
            # 'submissions_waiting_author_approval': articles_waiting_author_approval,
            'submissions_in_process': articles_in_process,
            'journals': [journal],
            'atypes': article_types,
            'article_doctypes': article_doctypes,
            'submission_rules': submission_rules
        })


    @http.route('/ojm/<int:journal_id>/inauthor', auth='user', website=True)
    def in_author(self, journal_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        articles_sent_back_to_author = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'back_to_author')])
        articles_incomplete = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'incomplete')])
        articles_waiting_author_approval = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'author_approved')])
        articles_in_process =  request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','in', ['submitted', 'under_review', 'typesetting'])])
        return request.render("ojm.portal_author_in",{
            'company': company,
            'user': user,
            'journal': journal,
            'submissions_sent_back_to_author': articles_sent_back_to_author,
            'submissions_incomplete': articles_incomplete,
            'submissions_waiting_author_approval': articles_waiting_author_approval,
            'submissions_in_process': articles_in_process,
        })


    @http.route('/ojm/<int:journal_id>/inreviewer', auth='user', website=True)
    def in_reviewer(self, journal_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        articles_sent_back_to_author = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'back_to_author')])
        articles_incomplete = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'incomplete')])
        articles_waiting_author_approval = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'author_approved')])
        articles_in_process =  request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','in', ['submitted', 'under_review', 'typesetting'])])
        return request.render("ojm.portal_review_in",{
            'company': company,
            'user': user,
            'journal': journal,
            'submissions_sent_back_to_author': articles_sent_back_to_author,
            'submissions_incomplete': articles_incomplete,
            'submissions_waiting_author_approval': articles_waiting_author_approval,
            'submissions_in_process': articles_in_process,
        })

    @http.route('/ojm/<int:journal_id>/contact', auth='user', website=True)
    def journal_contact(self, journal_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        articles_sent_back_to_author = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'back_to_author')])
        articles_incomplete = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'incomplete')])
        articles_waiting_author_approval = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'author_approved')])
        articles_in_process =  request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','in', ['submitted', 'under_review', 'typesetting'])])
        return request.render("ojm.portal_journal_contact",{
            'company': company,
            'user': user,
            'journal': journal,
            'submissions_sent_back_to_author': articles_sent_back_to_author,
            'submissions_incomplete': articles_incomplete,
            'submissions_waiting_author_approval': articles_waiting_author_approval,
            'submissions_in_process': articles_in_process,
        })


    @http.route('/ojm/<int:journal_id>/insubmissions', auth='user', website=True)
    def incomplete_submissions(self, journal_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        articles_sent_back_to_author = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'back_to_author')])
        articles_incomplete = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'incomplete')])
        articles_waiting_author_approval = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'author_approved')])
        articles_in_process =  request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','in', ['submitted', 'under_review', 'typesetting'])])
        return request.render("ojm.portal_incomplete_submission",{
            'company': company,
            'user': user,
            'journal': journal,
            'submissions_sent_back_to_author': articles_sent_back_to_author,
            'submissions_incomplete': articles_incomplete,
            'submissions_waiting_author_approval': articles_waiting_author_approval,
            'submissions_in_process': articles_in_process,
        })


    @http.route('/ojm/<int:journal_id>/submissions/<int:submission_id>', auth='user', website=True)
    def submission_details(self, journal_id, submission_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        submission = request.env['ojm.article'].sudo().browse(int(submission_id))
        return request.render("ojm.submission_details",{
            'company': company,
            'user': user,
            'journal': journal,
            'submission': submission,
        })


    
    @http.route('/ojm/<int:journal_id>/btauthor', auth='user', website=True)
    def back_to_author(self, journal_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        articles_sent_back_to_author = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'back_to_author')])
        articles_incomplete = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'incomplete')])
        articles_waiting_author_approval = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'author_approved')])
        articles_in_process =  request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','in', ['submitted', 'under_review', 'typesetting', 'under_revision'])])
        articles_to_revised = request.env["ojm.article"].sudo().search([
            ('submitted_by', '=', user.id),
            ('state', 'in', ['under_revision'])
        ])
        return request.render("ojm.portal_back_to_author",{
            'company': company,
            'user': user,
            'journal': journal,
            'submissions_sent_back_to_author': articles_sent_back_to_author,
            'submissions_incomplete': articles_incomplete,
            'submissions_waiting_author_approval': articles_waiting_author_approval,
            'submissions_in_process': articles_in_process,
            'submissions_to_revise': articles_to_revised
        })

    
    @http.route("/ojm/submission/step/<int:step_id>", auth="user", website=True, csrf=False)
    def get_submission_step(self, step_id, **kw):
        data_page = request.render(f"ojm.submission_form_step_{step_id}", {
            "data": "this is a test"
        })
        print(data_page.template)
        headers = {'Content-Type': 'application/json'}
        body = {
            "saved": True,
            "page_data": str(data_page) 
        }
        return Response(json.dumps(body), headers=headers) 
        


    @http.route('/ojm/<int:journal_id>/new_submission', auth='user', website=True)
    def journal_submission(self, journal_id, **kw):
        journal = request.env['ojm.journal'].sudo().browse(journal_id)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        articles_sent_back_to_author = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'back_to_author')])
        articles_incomplete = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'incomplete')])
        articles_waiting_author_approval = request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','=', 'author_approved')])
        articles_in_process =  request.env['ojm.article'].sudo().search([
            ('submitted_by', '=', user.id),
            ('state','in', ['submitted', 'under_review', 'typesetting'])])
        article_types = request.env["ojm.article.type"].sudo().search([('active', '=', True),('is_published', '=', True)])
        submission_rules = request.env["ojm.submission.rule"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        article_doctypes = request.env["ojm.article.file.type"].sudo().search([('active', '=', True), ('is_published', '=', True)])
        return request.render("ojm.portal_submission",{
            'company': company,
            'user': user,
            'journal': journal,
            'submissions_sent_back_to_author': articles_sent_back_to_author,
            'submissions_incomplete': articles_incomplete,
            'submissions_waiting_author_approval': articles_waiting_author_approval,
            'submissions_in_process': articles_in_process,
            'journals': [journal],
            'atypes': article_types,
            'article_doctypes': article_doctypes,
            'submission_rules': submission_rules 
        })


    @http.route('/handle_orcid_response', auth='public')
    def handle_orcid_response(self, *kw):
        pprint(kw)
        return redirect('/')


    # REVIEWER MANAGEMENT
    @http.route('/ojm/<int:jid>/rinvitations', type='http', auth='user', website=True)
    def reviewer_invitations(self, jid, **args):
        journal = request.env['ojm.journal'].sudo().browse(jid)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        invitations = request.env['ojm.reviewer.invitation'].sudo().search([
            ('journal_id', '=', jid), ('state', '=', 'pending')])

        return request.render("ojm.reviewer_invitations", {
            "invitations": invitations,
            'company': company,
            'user': user,
            'journal': journal,
            })


    @http.route('/ojm/<int:jid>/rinvitation/<int:id>', type='http', auth='user', website=True)
    def reviewer_invitation(self, jid, id, **args):
        journal = request.env['ojm.journal'].sudo().browse(jid)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        invitation = request.env['ojm.reviewer.invitation'].sudo().browse(id)

        return request.render("ojm.reviewer_invitation_details", {
            "invitation": invitation,
            'company': company,
            'user': user,
            'journal': journal,
            })


    @http.route('/ojm/<int:jid>/rassignments', type='http', auth='user', website=True)
    def reviewer_assignments(self, jid, **args):
        journal = request.env['ojm.journal'].sudo().browse(jid)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        assignments = request.env['ojm.reviewer.assignment'].sudo().search([
            ('journal_id', '=', jid), ('decision', '=', False), ('reviewer_id', '=', user.id)])

        return request.render("ojm.reviewer_assignments", {
            "assignments": assignments,
            'company': company,
            'user': user,
            'journal': journal,
            })

    @http.route('/ojm/<int:jid>/cassignments', type='http', auth='user', website=True)
    def reviewer_assignments_completed(self, jid, **args):
        journal = request.env['ojm.journal'].sudo().browse(jid)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        assignments = request.env['ojm.reviewer.assignment'].sudo().search([
            ('journal_id', '=', jid), ('decision', '!=', False), ('reviewer_id', '=', user.id)])

        return request.render("ojm.reviewer_assignments_completed", {
            "assignments": assignments,
            'company': company,
            'user': user,
            'journal': journal,
            })


    @http.route('/ojm/<int:jid>/rassignments/<int:id>', type='http', auth='user', website=True)
    def reviewer_assignment(self, jid, id, **args):
        journal = request.env['ojm.journal'].sudo().browse(jid)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        assignment = request.env['ojm.reviewer.assignment'].sudo().browse(id)

        return request.render("ojm.reviewer_assignment_details", {
            "assignment": assignment,
            "submission": assignment.invitation_id.article_id if assignment else None,
            'company': company,
            'user': user,
            'journal': journal,
            })


    @http.route('/ojm/<int:jid>/review/asg/<int:ass_id>', type='http', auth='user', website=True)
    def submit_review(self, jid, ass_id, **args):
        journal = request.env['ojm.journal'].sudo().browse(jid)
        company_id = request.env.context['allowed_company_ids'] and request.env.context['allowed_company_ids'][0]
        company = request.env['res.company'].sudo().search([('id', '=', company_id)]) if company_id else None
        user = request.env.user
        assignment = request.env['ojm.reviewer.assignment'].sudo().browse(ass_id)

        if assignment:
            if 'rufile' in request.params.keys():
                file_name = request.params['rufile'].filename 
                file = request.params['rufile']
                attachment = file.read() 
                attachment_rec = request.env['ir.attachment'].sudo().create({
                    'name':file_name,
                    'res_name': file_name,
                    'type': 'binary',   
                    'res_model': 'ojm.reviewer.assignment',
                    'res_id': ass_id,
                    'datas': attachment,
                    'public': True
                })
                assignment.sudo().write({
                    'reviewed_manuscript': attachment_rec.id
                })
            assignment.sudo().write({
                'decision': request.params.get('decision'),
                'general_comment': request.params.get('rcomment'),
                'comment_severity': request.params.get('comment_severity'),
                'english_flow': request.params.get('english_flow'),
                'statistic': request.params.get('statistic'),
                'scientific_rigor': request.params.get('scientific_rigor'),
                'impact_relevance': request.params.get('impact_relevance'),
                'structure_and_content': request.params.get('structure_and_content'),
                'references': request.params.get('references'),
            })

        return request.redirect(f"/ojm/{jid}/rassignments")
    
