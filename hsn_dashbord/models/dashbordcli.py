# -*- coding: utf-8 -*-
import time
import math
import datetime
from datetime import timedelta
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import UserError, ValidationError
from odoo import api, fields, models, _
from dateutil.relativedelta import relativedelta

class CritereDashClient(models.Model):
    _name = "dashbord.critereclient"
    _description = "Criteres client"
    _rec_name = "kanban"    

    @api.depends('aca','amarge','afrequence','aretard','opca','opmarge','opfrequence','opretard','intca','intmarge','intfrequence','intretard','ca','marge','frequence','retard')
    def get_resumecritere(self):
        for record in self:
            critere = ''
            if record.aca == True:
               critere = critere + ' Chiffre d\'affaire '+str(record.intca)+' jours '+str(record.opca)+' '+str(record.ca)+';'
            if record.amarge == True:
               critere = critere + ' Marge '+str(record.intmarge)+' jours '+str(record.opmarge)+' '+str(record.marge)+';'
            if record.afrequence == True:
               critere = critere + ' Frequence '+str(record.intfrequence)+' jours '+str(record.opca)+' '+str(record.frequence)+';'
            if record.aretard == True:
               critere = critere + ' Retard '+str(record.opretard)+' '+str(record.retard)+';'
            record.resumecritere = critere
    def appliquer(self):
        #Formulation des requetes
        if self.aca and not self.opca:
           raise UserError("Operateur incorrect")
        if self.amarge and not self.opmarge:
           raise UserError("Opérateur incorrect")
        if self.afrequence and not self.opfrequence:
           raise UserError("Opérateur incorrect")
        if self.aretard and not self.opretard:
           raise UserError("Opérateur incorrect")
        req1_cli_ids = []
        req2_cli_ids = []
        req3_cli_ids = []
        req4_cli_ids = []
        #Critere Chiffre Affaire
        if self.aca:
            requete1 = "SELECT s.partner_id, sum(s.price_subtotal) " \
                   "FROM sale_report s, res_partner p " \
                   "WHERE s.partner_id = p.id " \
                   "AND s.date BETWEEN CURRENT_DATE-"+str(self.intca)+"  AND CURRENT_DATE " \
                   "AND s.state in ('sale','invoiced','done','pos_done') " \
                   "GROUP BY s.partner_id " \
                   "HAVING sum(s.price_subtotal)"+str(self.opca)+str(self.ca)+""                     
            self.env.cr.execute(requete1)
            resrequete1 = self.env.cr.dictfetchall()
            for res in resrequete1:
                req1_cli_ids.append(res['partner_id'])
                
        #Critere Marge
        if self.amarge:
            requete2 = "SELECT s.partner_id, sum(s.margin) " \
                   "FROM sale_report s, res_partner p " \
                   "WHERE s.partner_id = p.id " \
                   "AND s.date BETWEEN CURRENT_DATE-"+str(self.intmarge)+"  AND CURRENT_DATE " \
                   "AND s.state in ('sale','invoiced','done','pos_done') " \
                   "GROUP BY s.partner_id " \
                   "HAVING sum(s.margin)"+str(self.opmarge)+str(self.marge)+""                     
            self.env.cr.execute(requete2)
            resrequete2 = self.env.cr.dictfetchall()
            for res in resrequete2:
                req2_cli_ids.append(res['partner_id'])
                
        #Critere Frequence
        #if self.afrequence:
        #    requete3 = self.env['res.partner'].search([])  
        #    for res in requete3:
        #        nbcommande = res.sale_order_count + res.pos_order_count
        #        if self.opfrequence == '<':
        #            if nbcommande < self.frequence:
        #                req3_cli_ids.append(res.id)
        #        if self.opfrequence == '<=':
        #            if nbcommande <= self.frequence:
        #                req3_cli_ids.append(res.id)
        #        if self.opfrequence == '>':
        #            if nbcommande > self.frequence:
        #                req3_cli_ids.append(res.id) 
        #        if self.opfrequence == '>=':
        #            if nbcommande >= self.frequence:
        #                req3_cli_ids.append(res.id) 
        #        if self.opfrequence == '=':
        #            if nbcommande == self.frequence:
        #                req3_cli_ids.append(res.id)
        #Critere Frequence
        if self.afrequence:
           requete3 = self.env['res.partner'].search([])
           for res in requete3:
               nbcommande = res.get_frequence(datetime.date.today() - timedelta(days=self.intfrequence), datetime.date.today()) 
               nbcommandetot = res.sale_order_count + res.pos_order_count
               if nbcommandetot!=0:
                  #raise UserError(nbcommande)
                  if self.opfrequence == '<':
                    if nbcommande < self.frequence:
                        req3_cli_ids.append(res.id) 
                  if self.opfrequence == '<=':
                    if nbcommande <= self.frequence:
                        req3_cli_ids.append(res.id)
                  if self.opfrequence == '>':
                    if nbcommande > self.frequence:
                        req3_cli_ids.append(res.id) 
                  if self.opfrequence == '>=':
                    if nbcommande >= self.frequence:
                        req3_cli_ids.append(res.id) 
                  if self.opfrequence == '=':
                    if nbcommande == self.frequence:
                        req3_cli_ids.append(res.id) 
                        
        #Critere Retard
        #if self.aretard:
        #    requete4 = self.env['res.partner'].search([('nbjretard',self.opretard,self.retard)])
        #    for res in requete4:
        #        req4_cli_ids.append(res.id)
        #Critere retard
        if self.aretard:
            requete4 = self.env['res.partner'].search([])  
            for res in requete4:
                nbjretard = res.get_retard()
                montantdu = res.get_montantdu()
                if self.opretard == '<':
                    if nbjretard < self.retard and montantdu!=0:
                        req4_cli_ids.append(res.id) 
                if self.opretard == '<=':
                    if nbjretard <= self.retard and montantdu!=0:
                        req4_cli_ids.append(res.id)
                if self.opretard == '>':
                    if nbjretard > self.retard and montantdu!=0:
                        req4_cli_ids.append(res.id) 
                if self.opretard == '>=':
                    if nbjretard >= self.retard and montantdu!=0:
                        req4_cli_ids.append(res.id) 
                if self.opretard == '=':
                    if nbjretard == self.retard and montantdu!=0:
                        req4_cli_ids.append(res.id)
        #raise UserError(req4_cli_ids)
        #Constitution de la liste générale
        p = []
        if self.aca:
           p.append(req1_cli_ids)
        if self.amarge:
           p.append(req2_cli_ids)
        if self.afrequence:
           p.append(req3_cli_ids)
        if self.aretard:
           p.append(req4_cli_ids)

        #recuperation des elements communs
        result = {}
        if len(p) != 0:
           result = set(p[0])
           for s in p[1:]:
               result.intersection_update(s) 
        #raise UserError(requete1)
        #suppression des anciens produits
        reqsup = "DELETE FROM dashbord_client WHERE kanban ='"+str(self.kanban.code)+"'"
        self.env.cr.execute(reqsup)
        #Alimentation du kanban
        dashcli = self.env['dashbord.client']
        clients = self.env['res.partner'].search([('id','in',list(result))])
        for client in clients:
                  vals = {
                    'name':client.name,
                    'phone':client.phone,
                    'email':client.email,
                    'nbcommande':client.sale_order_count+client.pos_order_count,
                    'nbjretard':client.nbjretard,
                    'montantdu':client.montantdu,
                    'dashstate':'backlog',
                    'partner_id':client.id,
                    'kanban':self.kanban.code
                    }
                  dashcli.create(vals)
        
        #self.write({'state':'valide'})
    kanban = fields.Many2one('dashbord.kanban','Kanban', domain="[('type','=','CLIENT')]")
    date = fields.Date('Date d\'Application')
    ca = fields.Float('Chiffre d\'affaire', digits=(16,0))
    opca = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op ca')
    intca = fields.Integer('Intervalle CA')
    aca = fields.Boolean('A Chiffre d\'affaire', default=False)
    marge = fields.Float('Marge', digits=(16,0)) 
    opmarge = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op marge')
    intmarge = fields.Integer('Intervalle Marge')
    amarge = fields.Boolean('A Marge', default=False)
    frequence = fields.Float('Frequence commande', digits=(16,0))
    opfrequence = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op frequence')
    intfrequence = fields.Integer('Intervalle Marge')
    afrequence = fields.Boolean('A Frequence', default=False)
    retard = fields.Float('Retard de paiement', digits=(16,0))
    opretard = fields.Selection([('<','Inférieure'),('<=','Inférieure ou égale'),('=','Egale'),('>','Supérieure'),('>=','Supérieure ou égale')], 'Op retard')
    intretard = fields.Integer('Intervalle Retard')
    aretard = fields.Boolean('A Quantité dispo', default=False)
    resumecritere = fields.Char('Resume Critère', compute='get_resumecritere')
    state = fields.Selection([('nouveau','Nouveau'),('valide','Validé')], string='State', size=64, default='nouveau' ,track_visibility='onchange', required=True)
    
    
class ClientDash(models.Model):
    _name = "dashbord.client"
    _description = "Clients"
    _rec_name = "partner_id"

    name = fields.Char('Nom Client')
    partner_id = fields.Many2one('res.partner', 'Client')
    phone = fields.Char('Téléphone')
    email = fields.Char('Email')
    nbcommande = fields.Integer('Nombre commandes')
    nbjretard = fields.Integer('Jours de retard')
    montantdu = fields.Float('Montant dû')
    kanban = fields.Char('Kanban')
    dashstate = fields.Selection([('backlog','BACKLOG'),('afaire','A FAIRE'),('encours','EN COURS'),('termine','TERMINE')], string='Etat DASH', size=64, default='backlog' ,track_visibility='onchange', required=True, group_expand='_expand_states')
    
    def _expand_states(self, states, domain, order):
        return [key for key, val in type(self).dashstate.selection]
        
        
class Partner(models.Model):
    _description = 'Contact'
    _inherit = 'res.partner'

    def get_infoscli(self):
        for record in self:
            factures = self.env['account.move'].search([('type','=','out_invoice'),('state','=','posted'),('partner_id','=',record.id),('amount_residual','!=',0)])    
            dateech = datetime.datetime.strptime('2900-01-01','%Y-%m-%d').date()
            montantdu = 0            
            for facture in factures:
                montantdu = montantdu + facture.amount_residual
                #raise UserError(facture.invoice_date_due)
                if facture.invoice_date_due:
                   if facture.invoice_date_due < dateech:
                      dateech = facture.invoice_date_due
            if dateech != datetime.datetime.strptime('2900-01-01','%Y-%m-%d').date():
               nbj = (datetime.date.today()-dateech).days
            else:
               nbj = 0
            record.montantdu = montantdu
            record.nbjretard = nbj
    def get_retard(self):
        for record in self:
            factures = self.env['account.move'].search([('type','=','out_invoice'),('state','=','posted'),('partner_id','=',record.id),('amount_residual','!=',0)])    
            dateech = datetime.datetime.strptime('2900-01-01','%Y-%m-%d').date()
            montantdu = 0            
            for facture in factures:
                montantdu = montantdu + facture.amount_residual
                #raise UserError(facture.invoice_date_due)
                if facture.invoice_date_due:
                   if facture.invoice_date_due < dateech:
                      dateech = facture.invoice_date_due
            if dateech != datetime.datetime.strptime('2900-01-01','%Y-%m-%d').date():
               nbj = (datetime.date.today()-dateech).days
            else:
               nbj = 0
        return nbj
    def get_montantdu(self):
        for record in self:
            factures = self.env['account.move'].search([('type','=','out_invoice'),('state','=','posted'),('partner_id','=',record.id),('amount_residual','!=',0)])    
            dateech = datetime.datetime.strptime('2900-01-01','%Y-%m-%d').date()
            montantdu = 0            
            for facture in factures:
                montantdu = montantdu + facture.amount_residual
        return montantdu
    def get_frequence(self,debut,fin):
        nbcomcl = self.env['sale.order'].search_count([('state','in',('done','sale')),('partner_id','=',self.id),('date_order','>=',debut),('date_order','<=',fin)]) 
        nbcompos = self.env['pos.order'].search_count([('state','in',('paid','done','invoiced')),('partner_id','=',self.id),('date_order','>=',debut),('date_order','<=',fin)])   
        nbcom = nbcomcl + nbcompos
        return nbcom 
   
    nbjretard = fields.Integer('Jours de retard', compute='get_infoscli')
    montantdu = fields.Float('Montant dû', compute='get_infoscli')