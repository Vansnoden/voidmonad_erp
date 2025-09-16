# -*- coding: utf-8 -*-
# from odoo import http


# class ArtCommissions(http.Controller):
#     @http.route('/art_commissions/art_commissions', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/art_commissions/art_commissions/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('art_commissions.listing', {
#             'root': '/art_commissions/art_commissions',
#             'objects': http.request.env['art_commissions.art_commissions'].search([]),
#         })

#     @http.route('/art_commissions/art_commissions/objects/<model("art_commissions.art_commissions"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('art_commissions.object', {
#             'object': obj
#         })
