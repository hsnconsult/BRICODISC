# -*- coding: utf-8 -*-

# class BricoBase(http.Controller):
#     @http.route('/brico_base/brico_base/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/brico_base/brico_base/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('brico_base.listing', {
#             'root': '/brico_base/brico_base',
#             'objects': http.request.env['brico_base.brico_base'].search([]),
#         })

#     @http.route('/brico_base/brico_base/objects/<model("brico_base.brico_base"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('brico_base.object', {
#             'object': obj
#         })
