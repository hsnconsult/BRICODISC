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
                    'dashstate':'sol1',
                    'initstate':'sol1'
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
                    'dashstate':'sol2',
                    'initstate':'sol2'
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
                    'dashstate':'sol3',
                    'initstate':'sol3'
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
    initstate = fields.Selection([('sol1','SOL 1 PROMO'),('sol2','SOL 2 PROMO'),('sol3','SOL 3 PROMO')], string='Etat DEPART', size=64)
    dashstate = fields.Selection([('sol1','SOL 1 PROMO'),('sol2','SOL 2 PROMO'),('sol3','SOL 3 PROMO'),('afaire','A FAIRE'),('encours','EN COURS'),('termine','TERMINE')], string='Etat DASH', size=64, default='sol1' ,track_visibility='onchange', required=True, group_expand='_expand_states')
    
    def write(self, values):
        if 'dashstate' in values:
           previous_state = self.dashstate
           new_state = values.get('dashstate')
           if (new_state in ['sol1','sol2','sol3'] and previous_state in ['sol1','sol2','sol3']):
              raise ValidationError(_("Operations permises: A FAIRE, EN COURS ou TERMINE"))
           if (new_state in ['sol1','sol2','sol3'] and new_state!=self.initstate):
              raise ValidationError(_("Operations permises: POSITION DE DEPART"))
        return super(ProductDash, self).write(values) 
        
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).dashstate.selection] 

class CritereDash(models.Model):
    _name = "dashbord.critere"
    _description = "Criteres"  

    @api.depends('aqtevendue','aqteachetee','aqtedispo','avaleurachetee','avaleurvendue','acoutrevient','amargepercent','amargevaleur','aca','opqteachetee','opqtevendue','opqtedispo','opvaleurachetee','opvaleurvendue','opcoutrevient','opmargepercent','opmargevaleur','opca','intqteachetee','intqtevendue','intvaleurachetee','intvaleurvendue','intcoutrevient','qteachetee','qtevendue','qtedispo','valeurachetee','valeurvendue','coutrevient','margepercent','margevaleur','ca')
    def get_resumecritere(self):
        for record in self:
            critere = ''
            if record.aqtevendue == True:
               critere = critere + ' Quantité vendue '+str(record.intqtevendue)+' jours '+str(record.opqtevendue)+' '+str(record.qtevendue)+';'
            if record.aqteachetee == True:
               critere = critere + ' Quantité achetee '+str(record.intqteachetee)+' jours '+str(record.opqteachetee)+' '+str(record.qteachetee)+';'
            if record.aqtedispo == True:
               critere = critere + ' Stock '+str(record.opqtedispo)+' '+str(record.qtedispo)+';'
            if record.avaleurvendue == True:
               critere = critere + ' Valeur revente '+str(record.opvaleurvendue)+' '+str(record.valeurvendue)+';'
            if record.avaleurachetee == True:
               critere = critere + ' Valeur achat '+str(record.opvaleurachetee)+' '+str(record.valeurachetee)+';'
            if record.acoutrevient == True:
               critere = critere + ' Coutrevient '+str(record.opcoutrevient)+' '+str(record.coutrevient  )+';'
            if record.amargepercent == True:
               critere = critere + ' Marge (%) '+str(record.opmargepercent)+' '+str(record.margepercent)+';'
            if record.margevaleur == True:
               critere = critere + ' Marge valeur '+str(record.opmargevaleur)+' '+str(record.margevaleur)+';'
            if record.aca == True:
               critere = critere + ' CA '+str(record.opca)+' '+str(record.ca)+';'
            record.resumecritere = critere
    def appliquer(self):
        #Formulation des requetes
        if self.aqtevendue and not self.opqtevendue:
           raise UserError("Operateur incorrect")
        if self.aqteachetee and not self.opqteachetee:
           raise UserError("Opérateur incorrect")
        if self.aqtedispo and not self.opqtedispo:
           raise UserError("Opérateur incorrect")
        if self.avaleurvendue and not self.opvaleurvendue:
           raise UserError("Opérateur incorrect")
        if self.avaleurachetee and not self.opvaleurachetee:
           raise UserError("Opérateur incorrect")
        requete1 = "SELECT s.product_id, t.id, sum(s.product_uom_qty) " \
                   "FROM sale_report s, product_template t, product_product p " \
                   "WHERE p.product_tmpl_id = t.id " \
                   "AND s.product_id = p.id " \
                   "AND s.date BETWEEN CURRENT_DATE-"+str(self.intqtevendue)+"  AND CURRENT_DATE "\
                   "GROUP BY s.product_id, t.id " \
                   "HAVING sum(s.product_uom_qty)"+str(self.opqtevendue)+str(self.qtevendue)+""
        if self.aqtevendue:
           self.env.cr.execute(requete1)
        resrequete1 = self.env.cr.dictfetchall()
        req1_prod_ids = []
        for res in resrequete1:
            req1_prod_ids.append(res['id'])
        
        
        requete2 = "SELECT p.product_id, t.id, sum(p.qty_ordered) " \
                   "FROM purchase_report p, product_template t, product_product pr " \
                   "WHERE p.product_tmpl_id = t.id " \
                   "AND p.product_id = pr.id " \
                   "AND p.date_order BETWEEN CURRENT_DATE-"+str(self.intqtevendue)+"  AND CURRENT_DATE "\
                   "GROUP BY p.product_id, t.id " \
                   "HAVING sum(p.qty_ordered)"+str(self.opqteachetee)+str(self.qteachetee)+""
        if self.aqteachetee:
           self.env.cr.execute(requete2)
        resrequete2 = self.env.cr.dictfetchall()
        req2_prod_ids = []
        for res in resrequete2:
            req2_prod_ids.append(res['id'])
        
        
        requete3 = self.env['product.template'].search([('qty_available',self.opqtedispo,self.qtedispo)])
        req3_prod_ids = []
        for res in requete3:
            req3_prod_ids.append(res.id)
            
        requete4 = self.env['product.template'].search([])
        req4_prod_ids = []
        for res in requete4:
            if self.opvaleurvendue == '<':
               if res.qty_available*res.list_price < self.valeurvendue:
                  req4_prod_ids.append(res.id)
            if self.opvaleurvendue == '<=':
               if res.qty_available*res.list_price <= self.valeurvendue:
                  req4_prod_ids.append(res.id)
            if self.opvaleurvendue == '>':
               if res.qty_available*res.list_price > self.valeurvendue:
                  req4_prod_ids.append(res.id)
            if self.opvaleurvendue == '>=':
               if res.qty_available*res.list_price >= self.valeurvendue:
                  req4_prod_ids.append(res.id)
            if self.opvaleurvendue == '=':
               if res.qty_available*res.list_price == self.valeurvendue:
                  req4_prod_ids.append(res.id)
                  
        requete5 = self.env['product.template'].search([])
        req5_prod_ids = []
        for res in requete5:
            if self.opvaleurachetee == '<':
               if res.qty_available*res.list_price < self.valeurachetee:
                  req5_prod_ids.append(res.id)
            if self.opvaleurachetee == '<=':
               if res.qty_available*res.list_price <= self.valeurachetee:
                  req5_prod_ids.append(res.id)
            if self.opvaleurachetee == '>':
               if res.qty_available*res.list_price > self.valeurachetee:
                  req5_prod_ids.append(res.id)
            if self.opvaleurachetee == '>=':
               if res.qty_available*res.list_price >= self.valeurachetee:
                  req5_prod_ids.append(res.id)
            if self.opvaleurachetee == '=':
               if res.qty_available*res.list_price == self.valeurachetee:
                  req5_prod_ids.append(res.id)
               
        #Constitution de la liste générale
        p = []
        if self.aqtevendue:
           p.append(req1_prod_ids)
        if self.aqteachetee:
           p.append(req2_prod_ids)
        if self.aqtedispo:
           p.append(req3_prod_ids)
        if self.avaleurvendue:
           p.append(req4_prod_ids)
        if self.avaleurachetee:
           p.append(req5_prod_ids)
        #recuperation des elements communs
        result = {}
        if len(p) != 0:
           result = set(p[0])
           for s in p[1:]:
               result.intersection_update(s) 
        #raise UserError(requete1)
        #suppression des anciens produits
        reqsup = "DELETE FROM dashbord_templatestocksolde WHERE dashstate ='"+str(self.kanbancol)+"'"
        self.env.cr.execute(reqsup)
        #Alimentation du kanban
        dashprod = self.env['dashbord.templatestocksolde']
        dashprodexist = self.env['dashbord.templatestocksolde'].search([])
        tempexist = []
        for exist in dashprodexist:
            tempexist.append(exist.product_id.id)
        #raise UserError(tempexist)
        prods = self.env['product.template'].search([])
        for prod in prods:
            if prod.id in list(result) and prod.id not in tempexist:
                  vals = {
                    'name':prod.name,
                    'default_code':prod.default_code,
                    'lst_price':prod.lst_price,
                    'qty_available':prod.qty_available,
                    'uom_id':prod.uom_id.name,
                    'dashstate':str(self.kanbancol),
                    'initstate':str(self.kanbancol),
                    'product_id':prod.id
                    }
                  dashprod.create(vals)
        
        #self.write({'state':'valide'})
    name = fields.Char('Description')
    qtevendue = fields.Float('Quantité vendue', digits=(16,0))
    opqtevendue = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op qtevendue')
    intqtevendue = fields.Integer('Intervalle Qte vendue')
    aqtevendue = fields.Boolean('A Quantité vendue', default=False)
    qteachetee = fields.Float('Quantité achetée', digits=(16,0)) 
    opqteachetee = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op qteachetee')
    intqteachetee = fields.Integer('Intervalle Qte achetee')
    aqteachetee = fields.Boolean('A Quantité achetée', default=False)
    qtedispo = fields.Float('Quantité disponible', digits=(16,0))
    opqtedispo = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op qtedispo')
    aqtedispo = fields.Boolean('A Quantité dispo', default=False)
    valeurvendue = fields.Float('Valeur vendue', digits=(16,0))
    opvaleurvendue = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op valeurvendue')
    intvaleurvendue = fields.Integer('Intervalle Valeur vendue')
    avaleurvendue = fields.Boolean('A Valeur vendue', default=False)
    valeurachetee = fields.Float('Valeur achetée', digits=(16,0))
    opvaleurachetee = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op valeurachetee')
    intvaleurachetee = fields.Integer('Intervalle Valeur achetee')
    avaleurachetee = fields.Boolean('A Valeur achetée', default=False)    
    coutrevient = fields.Float('Coût de revient', digits=(16,0))
    opcoutrevient = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op coutrevient')
    intcoutrevient = fields.Integer('Intervalle Cout de revient') 
    acoutrevient = fields.Boolean('A Coût revient', default=False)    
    margepercent = fields.Float('Marge(%)', digits=(16,0)) 
    opmargepercent = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op margepercent')
    amargepercent = fields.Boolean('A Margeper', default=False)
    margevaleur = fields.Float('Marge', digits=(16,0))
    opmargevaleur = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op margevaleur')    
    amargevaleur = fields.Boolean('A Marge valeur', default=False)
    ca = fields.Float('Chiffre d\'affaire', digits=(16,0))
    opca = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op ca')
    aca = fields.Boolean('A CA', default=False)
    #Choix des kanbans
    kanban = fields.Selection([('psolde','Produits à solder'),('pmav','Produits à mettre en avant'),('pinv','Produits à inventorier'),('pneg','Produits à négocier'),('pnpc','Produits à ne plus commander')], 'Appliquer au KANBAN')
    kanbancol = fields.Selection([('sol1','SOL1 PROMO'),('sol2','SOL2 PROMO'),('sol3','SOL3 PROMO')], 'Colonne')
    resumecritere = fields.Char('Resume Critère', compute='get_resumecritere')
    state = fields.Selection([('nouveau','Nouveau'),('valide','Validé')], string='State', size=64, default='nouveau' ,track_visibility='onchange', required=True)

class ProductDashsolde(models.Model):
    _name = "dashbord.templatestocksolde"
    _description = "Produit a solder"
    
    name = fields.Char('Nom produit')
    product_id = fields.Many2one('product.template', 'Article')
    default_code = fields.Char('Référence')
    barcode = fields.Char('Code barre')
    lst_price = fields.Float('Prix')
    qty_available = fields.Float('Quantité')
    uom_id = fields.Char('Udm')
    initstate = fields.Selection([('sol1','SOL 1 PROMO'),('sol2','SOL 2 PROMO'),('sol3','SOL 3 PROMO')], string='Etat DEPART', size=64)
    dashstate = fields.Selection([('sol1','SOL 1 PROMO'),('sol2','SOL 2 PROMO'),('sol3','SOL 3 PROMO'),('afaire','A FAIRE'),('encours','EN COURS'),('termine','TERMINE')], string='Etat DASH', size=64, default='sol1' ,track_visibility='onchange', required=True, group_expand='_expand_states')
    
    def write(self, values):
        if 'dashstate' in values:
           previous_state = self.dashstate
           new_state = values.get('dashstate')
           if (new_state in ['sol1','sol2','sol3'] and previous_state in ['sol1','sol2','sol3']):
              raise ValidationError(_("Operations permises: A FAIRE, EN COURS ou TERMINE"))
           if (new_state in ['sol1','sol2','sol3'] and new_state!=self.initstate):
              raise ValidationError(_("Operations permises: POSITION DE DEPART"))
        return super(ProductDashsolde, self).write(values) 
        
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).dashstate.selection] 