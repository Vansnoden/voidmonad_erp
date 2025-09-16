# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request


class ArtCommissionsController(http.Controller):
    @http.route('/commission/submit', auth='user', website=True)
    def index(self, **kw):
        return request.render("art_commissions.commission_request_form", {
            "data": "test"
        })
