# -*- coding: utf-8 -*-
import base64
import traceback
from odoo import http
from odoo.http import request


class ArtCommissionsController(http.Controller):
    @http.route('/commission/submit', auth='user', website=True)
    def index(self, **kw):
        if request.httprequest.method == "POST":
            try:
                params = request.params
                client = request.env.user.partner_id
                description = params['description']
                category = params['category']
                if category == 'fanart':
                    product = request.env.ref('art_commissions.fanart_product')
                elif category == 'original':
                    product = request.env.ref('art_commissions.fanart_product')
                new_commission = request.env['art.commission'].sudo().create({
                    'client_id': client.id,
                    'category': category,
                    'description': description,   
                    'status': 'draft', # become submitted only when the user pays 50 % of the amount
                    'product_id': product.id
                })
                uploaded_files = request.httprequest.files.getlist('images[]')
                for f in uploaded_files:
                    file_content = f.read()
                    filename = f.filename
                    attachment = base64.b64encode(file_content).decode('utf-8')
                    attachment_rec = request.env['ir.attachment'].sudo().create({
                        'name':filename,
                        'res_name': filename,
                        'type': 'binary',   
                        'res_model': 'art.commission',
                        'res_id': new_commission.id,
                        'datas': attachment,
                        'public': True
                    })
                    new_commission.sudo().write({
                        "reference_ids": [(4, attachment_rec.id)]
                    })
                return request.render("art_commissions.commission_request_form", {
                    "success": True
                })
            except Exception as e:
                print("EXCEPTION: ", e)
                return request.render("art_commissions.commission_request_form", {
                    "error": str(e)
                })
        return request.render("art_commissions.commission_request_form", {})
