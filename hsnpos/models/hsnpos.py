# -*- coding: utf-8 -*-

import math
import os
import pysftp
import re
import sys
import time
import zipfile
from ftplib import FTP
from odoo import api, fields, models, _
from odoo import tools
from odoo.osv import expression
from odoo.tools.float_utils import float_round as round


class ProductProduct(models.Model):
    _name = "product.product"
    _description = "Product"
    _inherit = "product.product"

    ligne_gencod = fields.One2many('iwel.wgencode', 'idproduit', 'gencode')

    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        if not args:
            args = []
        if name:
            positive_operators = ['=', 'ilike', '=ilike', 'like', '=like']
            product_ids = []
            if operator in positive_operators:
                product_ids = self._search([('default_code', '=', name)] + args, limit=limit,
                                           access_rights_uid=name_get_uid)
                if not product_ids:
                    product_ids = self._search([('barcode', '=', name)] + args, limit=limit,
                                               access_rights_uid=name_get_uid)
                    if not product_ids:
                        product_ids = self._search([('ligne_gencod.c1', '=', name)] + args, limit=limit,
                                                   access_rights_uid=name_get_uid)
            if not product_ids and operator not in expression.NEGATIVE_TERM_OPERATORS:
                # Do not merge the 2 next lines into one single search, SQL search performance would be abysmal
                # on a database with thousands of matching products, due to the huge merge+unique needed for the
                # OR operator (and given the fact that the 'name' lookup results come from the ir.translation table
                # Performing a quick memory merge of ids in Python will give much better performance
                product_ids = self._search(args + [('default_code', operator, name)], limit=limit)
                if not limit or len(product_ids) < limit:
                    # we may underrun the limit because of dupes in the results, that's fine
                    limit2 = (limit - len(product_ids)) if limit else False
                    product2_ids = self._search(args + [('name', operator, name), ('id', 'not in', product_ids)],
                                                limit=limit2, access_rights_uid=name_get_uid)
                    product_ids.extend(product2_ids)
            elif not product_ids and operator in expression.NEGATIVE_TERM_OPERATORS:
                domain = expression.OR([
                    ['&', ('default_code', operator, name), ('name', operator, name)],
                    ['&', ('default_code', '=', False), ('name', operator, name)],
                ])
                domain = expression.AND([args, domain])
                product_ids = self._search(domain, limit=limit, access_rights_uid=name_get_uid)
            if not product_ids and operator in positive_operators:
                ptrn = re.compile('(\[(.*?)\])')
                res = ptrn.search(name)
                if res:
                    product_ids = self._search([('default_code', '=', res.group(2))] + args, limit=limit,
                                               access_rights_uid=name_get_uid)
            # still no results, partner in context: search on supplier info as last hope to find something
            if not product_ids and self._context.get('partner_id'):
                suppliers_ids = self.env['product.supplierinfo']._search([
                    ('name', '=', self._context.get('partner_id')),
                    '|',
                    ('product_code', operator, name),
                    ('product_name', operator, name)], access_rights_uid=name_get_uid)
                if suppliers_ids:
                    product_ids = self._search([('product_tmpl_id.seller_ids', 'in', suppliers_ids)], limit=limit,
                                               access_rights_uid=name_get_uid)
        else:
            product_ids = self._search(args, limit=limit, access_rights_uid=name_get_uid)
        return self.browse(product_ids).name_get()


class IwelArticleTmp(models.Model):
    _name = "iwel.articletmp"
    _description = "Articles"

    def reception(self):
        repentree = "/home/odoo/iwel/entree"
        repentreeserv = "/home/brico/entree"
        reparchiveserv = "/home/brico/archives"
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys = None
        with pysftp.Connection('192.241.159.38', username='brico', password='brico', cnopts=cnopts) as sftp:
            with sftp.cd('/home/brico/entree'):  # temporarily chdir to allcode
                os.chdir(repentree)
                fichiers = [f for f in sftp.listdir() if f != "." and f != ".."]
                for fichier in fichiers:
                    nomfichier = repentreeserv + "/" + fichier
                    nomarchive = reparchiveserv + "/" + fichier + '-' + time.strftime("%Y%m%d-%H%M%S")
                    sftp.get(nomfichier)  # get a remote file
                    sftp.rename(nomfichier, nomarchive)
                    if '.zip' in fichier or '.ZIP' in fichier:
                        self.unzip(fichier, '/home/odoo/iwel/entree')

    def unzip(self, fichier, rep):
        with zipfile.ZipFile(fichier, "r") as zip_ref:
            zip_ref.extractall(rep)

    def deplace(self):
        source = '/home/odoo/iwel/entree/'
        dest = '/home/odoo/iwel/archives/'
        files = os.listdir(source)
        for f in files:
            if not (f.startswith("B")):
                nomfic = source + f
                nomarc = dest + f + '-' + time.strftime("%Y%m%d-%H%M%S")
                os.rename(nomfic, nomarc)

    def maj_base(self):
        # Creation des nouveaux articles
        fichier = "/home/odoo/iwel/entree/WEFICTAR"
        fic_csv = open(fichier, "r", encoding='cp437')
        self.env.cr.execute("delete from articletemp")
        self.env.cr.copy_from(fic_csv, 'articletemp', sep=';')
        self.env.cr.commit()
        fic_csv.close()
        self.env.cr.execute(
            "delete from articletemp where c3 in (select default_code from product_template where default_code is not null)")
        self.env.cr.execute(
            "delete from articletemp where c23 in (select c23 from product_template where c23 is not null)")
        self.env.cr.execute("select * from articletemp")
        results = self.env.cr.dictfetchall()
        for result in results:
            vals = {
                'name': result['c11'],
                'sale_ok': True,
                'purchase_ok': True,
                'type': 'product',
                'default_code': result['c3'],
                'categ_id': 12,
                'barcode': result['c23'],
                'coeff': 2,
                'frais': 27.05,
                'c1': result['c1'],
                'c2': result['c2'],
                'c3': result['c3'],
                'refuniq': result['c3'],
                'c4': result['c4'],
                'c5': result['c5'],
                'c6': result['c6'],
                'c7': result['c7'],
                'c8': result['c8'],
                'c9': result['c9'],
                'c10': result['c10'],
                'c11': result['c11'],
                'c12': result['c12'],
                'c13': result['c13'],
                'c14': result['c14'],
                'c15': result['c15'],
                'c16': result['c16'],
                'c17': result['c17'],
                'c18': result['c18'],
                'c19': result['c19'],
                'c20': result['c20'],
                'c21': result['c21'],
                'c22': result['c22'],
                'c23': result['c23'],
                'c24': result['c24'],
                'c25': result['c25'],
                'c26': result['c26'],
                'c27': result['c27'],
                'c28': result['c28'],
                'c29': result['c29'],
                'c30': result['c30'],
                'c31': result['c31'],
                'c32': result['c32'],
                'c33': result['c33'],
                'c34': result['c34'],
                'c35': result['c35'],
                'c36': result['c36'],
                'c37': result['c37'],
                'c38': result['c38'],
                'c39': result['c39'],
                'c40': result['c40'],
                'c41': result['c41'],
                'c42': result['c42'],
                'c43': result['c43'],
                'c44': result['c44'],
                'c45': result['c45'],
                'c46': result['c46'],
            }
            p = self.env['product.template'].create(vals)
        # Mise a jour des tarifs
        fichiert = "/home/odoo/iwel/entree/WTARIF"
        fic_csvt = open(fichiert, "r", encoding='cp437')
        self.env.cr.execute("delete from tariftemp")
        self.env.cr.copy_from(fic_csvt, 'tariftemp', sep=';')
        self.env.cr.commit()
        fic_csvt.close()
        self.env.cr.execute("delete from tariftemp where c1 in (select c1 from iwel_wtarif where c1 is not null)")
        self.env.cr.execute("select * from tariftemp")
        results = self.env.cr.dictfetchall()
        for result in results:
            self.env.cr.execute("select id from product_template where default_code = '" + str(result['c1']) + "'")
            idp = self.env.cr.fetchone()
            if idp:
                vals = {
                    'idarticle': idp[0],
                    'c1': result['c1'],
                    'c2': result['c2'],
                    'c3': result['c3'],
                    'c4': result['c4'],
                    'c5': result['c5'],
                    'c6': result['c6'],
                    'c7': result['c7'],
                    'c8': result['c8'],
                    'c9': result['c9'],
                }
                t = self.env['iwel.wtarif'].create(vals)
        # Mise a jour des gencodes
        fichierg = "/home/odoo/iwel/entree/wgencod"
        fic_csvg = open(fichierg, "r", encoding='cp437')
        self.env.cr.execute("delete from gencodetemp")
        self.env.cr.copy_from(fic_csvg, 'gencodetemp', sep=';')
        self.env.cr.commit()
        fic_csvg.close()
        self.env.cr.execute("delete from gencodetemp where c2 in (select c2 from iwel_wgencode where c2 is not null)")
        self.env.cr.execute("select * from gencodetemp")
        results = self.env.cr.dictfetchall()
        for result in results:
            self.env.cr.execute("select id from product_template where default_code = '" + str(result['c2']) + "'")
            idp = self.env.cr.fetchone()
            if idp is not None:
                self.env.cr.execute("select id from product_product where product_tmpl_id = " + str(idp[0]) + "")
                idpr = self.env.cr.fetchone()
                vals = {
                    'idarticle': idp[0],
                    'idproduit': idpr[0],
                    'c1': result['c1'],
                    'c2': result['c2'],
                    'c3': result['c3'],
                }
                g = self.env['iwel.wgencode'].create(vals)
                # Mise a jour des prix de vente
        self.env.cr.execute("select * from articletemp")
        results = self.env.cr.dictfetchall()
        for result in results:
            art = self.env['product.template'].search([('default_code', '=', result['c3'])])[0]
            prixcessioneur = self.env['iwel.wtarif'].search([('idarticle', '=', art.id)])
            if prixcessioneur:
                prixcession = int(prixcessioneur[0]['c6']) / 100
                # raise UserError(prixcession)
                prixbase_dj = prixcession * self.env['res.company'].search([('name', '=', 'bricodiscount.dj')])[
                    0].tauxdevise
                art.prixbase = prixcession
                art.prixbase_dj = prixbase_dj
                art.prixbase_brico = prixcession * self.env['res.company'].search([('name', '=', 'bricodiscount.dj')])[
                    0].tauxdevise
                art.cout = prixbase_dj * (1 + art.frais / 100)
                art.standard_price = prixbase_dj * (1 + art.frais / 100)
                art.list_price = round((prixbase_dj * (1 + art.frais / 100) * art.coeff) / 5, 0) * 5
        # Mise a jour des rayons et famille

    def maj_fam(self):
        self.env.cr.execute("select * from articletemp")
        results = self.env.cr.dictfetchall()
        for result in results:
            art = self.env['product.template'].search([('default_code', '=', result['c3'])])[0]
            codefam = self.env['iwel.wnomfam'].search([('c2', '=', '0' + art.c25[3:5]), ('c1', '=', art.c25[0:3])])
            # codefam = self.env['iwel.wnomfam'].search([('c2','=','63'),('c1','=','004')])
            # raise UserError(art.c25[0:3] + ' '+art.c25[3:5]+' '+art.c25)
            codefourn = self.env['iwel.fournisseur'].search([('c1', '=', art.c4)])
            if codefam:
                # raise UserError(codefam[0].c2 + ' ' +codefam[0].c1)
                art.idfamille = codefam[0].id
            if codefourn:
                art.idfournisseur = codefourn[0].id
        # Mise a jour des fourniseurs

    def maj_fourn(self):
        fichierf = "/home/odoo/iwel/entree/WECOFOUR"
        fic_csvf = open(fichierf, "r", encoding='cp437')
        self.env.cr.execute("delete from fournisseurtemp")
        self.env.cr.copy_from(fic_csvf, 'fournisseurtemp', sep=';')
        self.env.cr.commit()
        fic_csvf.close()
        self.env.cr.execute(
            "delete from fournisseurtemp where c1 in (select c1 from iwel_fournisseur where c1 is not null)")
        self.env.cr.execute("select * from fournisseurtemp")
        results = self.env.cr.dictfetchall()
        for result in results:
            vals = {
                'c1': result['c1'],
                'c2': result['c2'],
                'c3': result['c3'],
                'c4': result['c4'],
                'c5': result['c5'],
                'c6': result['c6'],
                'c7': result['c7'],
                'c8': result['c8'],
                'c9': result['c9'],
                'c10': result['c10'],
                'c11': result['c11'],
                'c12': result['c12'],
                'c13': result['c13'],
                'c14': result['c14'],
                'c15': result['c15'],
                'c16': result['c16'],
                'c17': result['c17'],
            }
            f = self.env['iwel.fournisseur'].create(vals)

    def maj_tarifdirect(self):
        # Mise a jour des tarifs
        fichiert = "/home/odoo/iwel/entree/wp-direct.txt"
        fic_csvt = open(fichiert, "r", encoding='cp437')
        self.env.cr.execute("delete from tarifdirecttemp")
        self.env.cr.copy_from(fic_csvt, 'tarifdirecttemp', sep=';')
        self.env.cr.commit()
        fic_csvt.close()
        # self.env.cr.execute("delete from tariftemp where c1 in (select c1 from iwel_wtarif where c1 is not null)")
        self.env.cr.execute("update product_template p set c51=t.c5, c48=t.c4 from tarifdirecttemp t where p.c3=t.c2")

    # results = self.env.cr.dictfetchall()
    def maj_cout(self):
        produits = self.env['product.template'].search(
            [('prixbase_dj', '!=', None), ('prixbase_dj', '!=', 0), ('categ_id', '=', 12), ('c51', '!=', 'aj'),
             ('active', '=', False)], limit=500)
        for produit in produits:
            produit.standard_price = produit.prixbase_dj * 1.2705
            produit.coeff = 1.7
            produit.list_price = produit.prixbase_dj * 1.2705 * 1.7
            produit.c51 = 'aj'
        # raise UserError(len(produits))

    def maj_taxe(self):
        products = self.env['product.template'].search([('categ_id', '=', 12), ('description', '!=', 'taj')], limit=500)
        # raise UserError(len(products))
        for product in products:
            product.taxes_id = (6,)
            product.description = 'taj'

    c1 = fields.Char('c1')
    c2 = fields.Char('c2')
    c3 = fields.Char('c3')
    c4 = fields.Char('c4')
    c5 = fields.Char('c5')
    c6 = fields.Char('c6')
    c7 = fields.Char('c7')
    c8 = fields.Char('c8')
    c9 = fields.Char('c9')
    c10 = fields.Char('c10')
    c11 = fields.Char('c11')
    c12 = fields.Char('c12')
    c13 = fields.Char('c13')
    c14 = fields.Char('c14')
    c15 = fields.Char('c15')
    c16 = fields.Char('c16')
    c17 = fields.Char('c17')
    c18 = fields.Char('c18')
    c19 = fields.Char('c19')
    c20 = fields.Char('c20')
    c21 = fields.Char('c21')
    c22 = fields.Char('c22')
    c23 = fields.Char('c23')
    c24 = fields.Char('c24')
    c25 = fields.Char('c25')
    c26 = fields.Char('c26')
    c27 = fields.Char('c27')
    c28 = fields.Char('c28')
    c29 = fields.Char('c29')
    c30 = fields.Char('c30')
    c31 = fields.Char('c31')
    c32 = fields.Char('c32')
    c33 = fields.Char('c33')
    c34 = fields.Char('c34')
    c35 = fields.Char('c35')
    c36 = fields.Char('c36')
    c37 = fields.Char('c37')
    c38 = fields.Char('c38')
    c39 = fields.Char('c39')
    c40 = fields.Char('c40')
    c41 = fields.Char('c41')
    c42 = fields.Char('c42')
    c43 = fields.Char('c43')
    c44 = fields.Char('c44')
    c45 = fields.Char('c45')
    c46 = fields.Char('c46')
    # c47 = fields.Char('c477')
