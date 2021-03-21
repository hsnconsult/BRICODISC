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
    

class CritereDash(models.Model):
    _name = "dashbord.critere"
    _description = "Criteres"
    _rec_name = "kanban"    

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
               critere = critere + ' CA '+str(record.intca)+' jours '+str(record.opca)+' '+str(record.ca)+';'
            if record.aqtedispo2 == True:
               critere = critere + ' Stock '+str(record.opqtedispo2)+' '+str(record.qtedispo2)+';'
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
        if self.acoutrevient and not self.opcoutrevient:
           raise UserError("Opérateur incorrect")
        if self.amargepercent and not self.opmargepercent:
           raise UserError("Opérateur incorrect")
        if self.amargevaleur and not self.opmargevaleur:
           raise UserError("Opérateur incorrect")
        if self.aca and not self.opca:
           raise UserError("Opérateur incorrect")
        if self.aqtedispo2 and not self.opqtedispo2:
           raise UserError("Opérateur incorrect")
        req1_prod_ids = []
        req2_prod_ids = []
        req3_prod_ids = []
        req4_prod_ids = []
        req5_prod_ids = []
        req6_prod_ids = []
        req7_prod_ids = []
        req8_prod_ids = []
        req9_prod_ids = []
        req10_prod_ids = []
        #Critere Quantité vendue
        if self.aqtevendue:
            requete1 = "SELECT s.product_tmpl_id as id, sum(s.product_uom_qty) " \
                   "FROM sale_report s, product_template t " \
                   "WHERE s.product_tmpl_id = t.id " \
                   "AND s.date BETWEEN CURRENT_DATE-"+str(self.intqtevendue)+"  AND CURRENT_DATE " \
                   "AND s.state in ('sale','invoiced','done','pos_done') " \
                   "GROUP BY s.product_tmpl_id " \
                   "HAVING sum(s.product_uom_qty)"+str(self.opqtevendue)+str(self.qtevendue)+""
            self.env.cr.execute(requete1)
            resrequete1 = self.env.cr.dictfetchall()
            for res in resrequete1:
                req1_prod_ids.append(res['id'])
        
        #Critere Quantité achetée
        if self.aqteachetee:
            requete2 = "SELECT p.product_tmpl_id as id, sum(p.qty_ordered) " \
                   "FROM purchase_report p, product_template t " \
                   "WHERE p.product_tmpl_id = t.id " \
                   "AND p.date_order BETWEEN CURRENT_DATE-"+str(self.intqtevendue)+"  AND CURRENT_DATE "\
                   "AND p.state in ('purchase','done') " \
                   "GROUP BY p.product_tmpl_id " \
                   "HAVING sum(p.qty_ordered)"+str(self.opqteachetee)+str(self.qteachetee)+""   
            self.env.cr.execute(requete2)
            resrequete2 = self.env.cr.dictfetchall()
            for res in resrequete2:
                req2_prod_ids.append(res['id'])
        
        #Critere Quantité disponible
        if self.aqtedispo:
            requete3 = self.env['product.template'].search([('qty_available',self.opqtedispo,self.qtedispo)])
            for res in requete3:
                req3_prod_ids.append(res.id)
                
        #Critere Quantité disponible 2
        if self.aqtedispo2:
            requete10 = self.env['product.template'].search([('qty_available',self.opqtedispo2,self.qtedispo2)])
            for res in requete10:
                req10_prod_ids.append(res.id)
        #Critere Valeur revente 
        if self.avaleurvendue:         
            requete4 = self.env['product.template'].search([])
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
        
        #Critere Valeur achat  
        if self.avaleurachetee:         
            requete5 = self.env['product.template'].search([])
            for res in requete5:
                if self.opvaleurachetee == '<':
                    if res.qty_available*res.standard_price < self.valeurachetee:
                        req5_prod_ids.append(res.id)
                if self.opvaleurachetee == '<=':
                    if res.qty_available*res.standard_price <= self.valeurachetee:
                        req5_prod_ids.append(res.id)
                if self.opvaleurachetee == '>':
                    if res.qty_available*res.standard_price > self.valeurachetee:
                        req5_prod_ids.append(res.id)
                if self.opvaleurachetee == '>=':
                    if res.qty_available*res.standard_price >= self.valeurachetee:
                        req5_prod_ids.append(res.id)
                if self.opvaleurachetee == '=':
                    if res.qty_available*res.standard_price == self.valeurachetee:
                        req5_prod_ids.append(res.id)
        
        #Critere Cout de revient 
        if self.acoutrevient:
            requete6 = self.env['product.template'].search([('standard_price',self.opcoutrevient,self.coutrevient)])
            for res in requete6:
                req6_prod_ids.append(res.id)
    
        #Critere Marge pourcentage
        if self.amargepercent:
            requete7 = self.env['product.template'].search([])  
            for res in requete7:
                marge = (res.list_price-res.standard_price)/res.standard_price if res.standard_price!=0 else 1
                if self.opmargepercent == '<':
                    if marge*100 < self.margepercent:
                        req7_prod_ids.append(res.id) 
                if self.opmargepercent == '<=':
                    if marge*100 <= self.margepercent:
                        req7_prod_ids.append(res.id)
                if self.opmargepercent == '>':
                    if marge*100 > self.margepercent:
                        req7_prod_ids.append(res.id) 
                if self.opmargepercent == '>=':
                    if marge*100 >= self.margepercent:
                        req7_prod_ids.append(res.id) 
                if self.opmargepercent == '=':
                    if marge*100 == self.margepercent:
                        req7_prod_ids.append(res.id) 

        #Critere Marge valeur
        if self.amargevaleur:
            requete8 = self.env['product.template'].search([])  
            for res in requete8:
                marge = res.list_price-res.standard_price
                if self.opmargevaleur == '<':
                    if marge < self.margevaleur:
                        req8_prod_ids.append(res.id) 
                if self.opmargevaleur == '<=':
                    if marge <= self.margevaleur:
                        req8_prod_ids.append(res.id)
                if self.opmargevaleur == '>':
                    if marge > self.margevaleur:
                        req8_prod_ids.append(res.id) 
                if self.opmargevaleur == '>=':
                    if marge >= self.margevaleur:
                        req8_prod_ids.append(res.id) 
                if self.opmargevaleur == '=':
                    if marge == self.margevaleur:
                        req8_prod_ids.append(res.id)  

        #Critere Chiffre Affaire
        if self.aca:
            requete9 = "SELECT s.product_id, t.id, sum(s.price_subtotal) " \
                   "FROM sale_report s, product_template t, product_product p " \
                   "WHERE p.product_tmpl_id = t.id " \
                   "AND s.product_id = p.id " \
                   "AND s.date BETWEEN CURRENT_DATE-"+str(self.intca)+"  AND CURRENT_DATE " \
                   "AND s.state in ('sale','invoiced','done','pos_done') " \
                   "GROUP BY s.product_id, t.id " \
                   "HAVING sum(s.price_subtotal)"+str(self.opca)+str(self.ca)+""  
            #raise UserError(requete9)                   
            self.env.cr.execute(requete9)
            resrequete9 = self.env.cr.dictfetchall()
            for res in resrequete9:
                req9_prod_ids.append(res['id'])
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
        if self.acoutrevient:
           p.append(req6_prod_ids)
        if self.amargepercent:
           p.append(req7_prod_ids)
        if self.amargevaleur:
           p.append(req8_prod_ids)
        if self.aca:
           p.append(req9_prod_ids)
        if self.aqtedispo2:
           p.append(req10_prod_ids)
        #recuperation des elements communs
        result = {}
        if len(p) != 0:
           result = set(p[0])
           for s in p[1:]:
               result.intersection_update(s) 
        #raise UserError(requete1)
        #suppression des anciens produits
        reqsup = "DELETE FROM dashbord_produitstock WHERE kanban ='"+str(self.kanban.code)+"'"
        self.env.cr.execute(reqsup)
        #Alimentation du kanban
        dashprod = self.env['dashbord.produitstock']
        #dashprodexist = self.env['dashbord.produitstock'].search([('kanban','=',self.kanban.code)])
        #tempexist = []
        #for exist in dashprodexist:
        #    tempexist.append(exist.product_id.id)
        #raise UserError(tempexist)
        prods = self.env['product.template'].search([('id','in',list(result))])
        for prod in prods:
            #if prod.id in list(result):
                  vals = {
                    'name':prod.name,
                    'default_code':prod.default_code,
                    'lst_price':prod.lst_price,
                    'qty_available':prod.qty_available,
                    'uom_id':prod.uom_id.name,
                    'dashstate':'backlog',
                    'product_id':prod.id,
                    'kanban':self.kanban.code,
                    'categ_id':prod.categ_id.id 
                    }
                  dashprod.create(vals)
        
        #self.write({'state':'valide'})
    kanban = fields.Many2one('dashbord.kanban','Kanban', domain="[('type','=','STOCK')]")
    date = fields.Date('Date d\'Application')
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
    qtedispo2 = fields.Float('Quantité disponible', digits=(16,0))
    opqtedispo2 = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op qtedispo2')
    aqtedispo2 = fields.Boolean('A Quantité dispo', default=False)
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
    intmargepercent = fields.Integer('Intervalle Marge percent') 
    margevaleur = fields.Float('Marge', digits=(16,0))
    opmargevaleur = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op margevaleur')    
    amargevaleur = fields.Boolean('A Marge valeur', default=False)
    intmargevaleur = fields.Integer('Intervalle Marge valeur') 
    ca = fields.Float('Chiffre d\'affaire', digits=(16,0))
    opca = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op ca')
    aca = fields.Boolean('A CA', default=False)
    intca = fields.Integer('Intervalle CA') 
    #Choix des kanbans
    #kanban = fields.Selection([('psolde','Produits à solder'),('pmav','Produits à mettre en avant'),('pinv','Produits à inventorier'),('pneg','Produits à négocier'),('pnpc','Produits à ne plus commander')], 'Appliquer au KANBAN')
    #kanban = fields.Many2one('dashbord.kanban','Kanban')
    #kanbancol = fields.Selection([('sol1','SOL1 PROMO'),('sol2','SOL2 PROMO'),('sol3','SOL3 PROMO')], 'Colonne')
    resumecritere = fields.Char('Resume Critère', compute='get_resumecritere')
    state = fields.Selection([('nouveau','Nouveau'),('valide','Validé')], string='State', size=64, default='nouveau' ,track_visibility='onchange', required=True)

class DashKanban(models.Model):
    _name = "dashbord.kanban"
    _description = "Kanban"

    name = fields.Char('Kanban')
    code = fields.Char('Code')
    type = fields.Selection([('STOCK','STOCK'),('CLIENT','CLIENT'),('VENTE','VENTE')])

class ProductDashStock(models.Model):
    _name = "dashbord.produitstock"
    _description = "Stocks"
    _rec_name = "product_id"

    name = fields.Char('Nom produit')
    product_id = fields.Many2one('product.template', 'Article')
    categ_id = fields.Many2one('product.category', 'Catégorie')
    default_code = fields.Char('Référence')
    barcode = fields.Char('Code barre')
    lst_price = fields.Float('Prix')
    qty_available = fields.Float('Quantité')
    uom_id = fields.Char('Udm')
    kanban = fields.Char('Kanban')
    dashstate = fields.Selection([('backlog','BACKLOG'),('afaire','A FAIRE'),('encours','EN COURS'),('termine','TERMINE')], string='Etat DASH', size=64, default='backlog' ,track_visibility='onchange', required=True, group_expand='_expand_states')
    
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).dashstate.selection]
