# -*- coding: utf-8 -*-
import time
import math
import datetime
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta
    


class DashFonction(models.Model):
    _name = "dashbord.fonction"
    _description = "Fonction"
    
    
    def asolder(self):
        dashprod = self.env['dashbord.templatestock']
        prods = self.env['product.template'].search([('qty_available','>',30)])
        vendus = self.env['sale.report'].read_group([('date','>','2020-12-11'),('date','<=','2021-01-13')],fields=['product_uom_qty'], groupby=['product_id'])
        ventes = dict([(data['product_id'][0], data['product_uom_qty']) for data in vendus if data['product_uom_qty']>20])
        prodvendus = list(ventes.keys())
        for prod in prods:
            if prod.qty_available*prod.standard_price > 600000:
               prodid = self.env['product.product'].search([('product_tmpl_id','=',prod.id)])[0].id
               if prodid in prodvendus:
                  vals = {
                    'name':prod.name,
                    'default_code':prod.default_code,
                    'lst_price':prod.lst_price,
                    'qty_available':prod.qty_available,
                    'uom_id':prod.uom_id.name,
                    'dashstate':'sol1'
                    }
                  dashprod.create(vals)
                  
    def asolder2(self):
        dashprod = self.env['dashbord.templatestock']
        prods = self.env['product.template'].search([('qty_available','>',10)])
        vendus = self.env['sale.report'].read_group([('date','>','2020-12-11'),('date','<=','2021-01-13')],fields=['product_uom_qty'], groupby=['product_id'])
        ventes = dict([(data['product_id'][0], data['product_uom_qty']) for data in vendus if data['product_uom_qty']<2])
        prodvendus = list(ventes.keys())
        for prod in prods:
            #if prod.qty_available*prod.standard_price > 600000:
               prodid = self.env['product.product'].search([('product_tmpl_id','=',prod.id)])[0].id
               if prodid in prodvendus:
                  vals = {
                    'name':prod.name,
                    'default_code':prod.default_code,
                    'lst_price':prod.lst_price,
                    'qty_available':prod.qty_available,
                    'uom_id':prod.uom_id.name,
                    'dashstate':'sol2'
                    }
                  dashprod.create(vals)        
    name = fields.Char('Nom')

    def asolder3(self):
        dashprod = self.env['dashbord.templatestock']
        prods = self.env['product.template'].search([('qty_available','>',20)])
        vendus = self.env['sale.report'].read_group([('date','>','2020-10-11'),('date','<=','2021-01-13')],fields=['product_uom_qty'], groupby=['product_id'])
        ventes = dict([(data['product_id'][0], data['product_uom_qty']) for data in vendus if data['product_uom_qty']<10])
        prodvendus = list(ventes.keys())
        for prod in prods:
               prodid = self.env['product.product'].search([('product_tmpl_id','=',prod.id)])[0].id
               if prodid in prodvendus:
                  vals = {
                    'name':prod.name,
                    'default_code':prod.default_code,
                    'lst_price':prod.lst_price,
                    'qty_available':prod.qty_available,
                    'uom_id':prod.uom_id.name,
                    'dashstate':'sol3'
                    }
                  dashprod.create(vals)        
    name = fields.Char('Nom')
    
class ProductDash(models.Model):
    _name = "dashbord.templatestock"
    _description = "Produit"
    
    name = fields.Char('Nom produit')
    default_code = fields.Char('Référence')
    barcode = fields.Char('Code barre')
    lst_price = fields.Float('Prix')
    qty_available = fields.Float('Quantité')
    uom_id = fields.Char('Udm')
    dashstate = fields.Selection([('sol1','SOL 1 PROMO'),('sol2','SOL 2 PROMO'),('sol3','SOL 3 PROMO'),('afaire','A FAIRE'),('encours','EN COURS'),('termine','TERMINE')], string='Etat DASH', size=64, default='sol1' ,track_visibility='onchange', required=True, group_expand='_expand_states')
    
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).dashstate.selection]    