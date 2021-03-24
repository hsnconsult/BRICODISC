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
    

class prix_criteremarge(models.Model):
    _name = "prix.criteremarge"
    _description = "Criteres de marge"

    def valider(self):
        articles = self.env['product.template'].search([])
        pricelist_item = self.env['product.pricelist.item']
        for article in articles:
            margeb = round(((article.list_price - article.standard_price) / article.standard_price) * 100, 2) if article.standard_price!=0 else 0
            if margeb>=self.margemin and margeb<=self.margemax:
                vals = {
                    'pricelist_id':self.pricelist_id.id,
                    'idcritere':self.id,
                    'applied_on':'1_product',
                    'product_tmpl_id':article.id,
                    'compute_price':'percentage',
                    'percent_price':self.taux               
                }
                pricelist_item.create(vals)
        self.write({'state':'valide'})
    pricelist_id = fields.Many2one('product.pricelist', 'Liste de prix') 
    margemin = fields.Float('Marge Min')
    margemax = fields.Float('Marge Max')
    taux = fields.Float('Taux de remise')
    ligne_prix = fields.One2many('product.pricelist.item','idcritere','prix')
    state = fields.Selection([('brouillon','Brouillon'),('valide','Validé'),('annule','Annulé')], string='Etat', size=64, default='brouillon',track_visibility='onchange', readonly=True, required=True)
    
class Pricelist(models.Model):
    _name = "product.pricelist"
    _inherit = "product.pricelist"
    
    critere_ids = fields.One2many('prix.criteremarge', 'pricelist_id', 'Criteres', copy=True)
 
class PricelistItem(models.Model):
    _name = "product.pricelist.item"
    _inherit = "product.pricelist.item"
    
    idcritere = fields.Many2one('prix.criteremarge', 'Critere', ondelete='cascade')