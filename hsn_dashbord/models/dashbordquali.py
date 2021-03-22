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


class Product(models.Model):
    _description = 'Product'
    _inherit = 'product.template'
 
   
    algamil = fields.Float('Al Gamil')
    naif = fields.Float('Naif')
    basset = fields.Float('Basset')
    doubai = fields.Float('Doubai')
    geantcasino = fields.Float('Géant/Casino')
    cashcenter = fields.Float('Cash center')
    modeconsom = fields.Selection([('jour','Journalier'),('hebdo','Hebdomadaire'),('mensuel','Mensuel'),('unan','Renouvellement par an'),('troisan','Renouvellement par 3 ans'),('unefois','1 seule fois dans la vie')], string='Mode de conso')
    necessite = fields.Selection([('obligatoire','Besoin obligatoire'),('important','Besoin important'),('coupcoeur','Coup de coeur')], string='Nécessité - Besoin')     
    technicite = fields.Selection([('fortedemande','Elevé avec forte demande'),('eleve','Elevé'),('moyenne','Moyenne')], string='Technicité')