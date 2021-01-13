# -*- coding: utf-8 -*-

from odoo import models, fields, api


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    idreception = fields.Many2one('iwel.reception', string='reception')

    # def unlink(self):
    #     print('========================>>>>')
    #     for pl in self.order_line:
    #         if pl.idreception:
    #             print("Herrreeee")
    #             pl.idreception.is_invoiced = False
    #     return super(PurchaseOrder, self).unlink()


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    idreception = fields.Many2one('iwel.lignereception', string='Ligne de reception')

    def unlink(self):
        if self.idreception:
            print("Herrreeee")
            self.idreception.is_invoiced = False
        return super(PurchaseOrderLine, self).unlink()


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    filler_remplacement = fields.Float("Filler replacement", compute='compute_filler', store=1)

    @api.depends('c51')
    def compute_filler(self):
        for r in self:
            r.filler_remplacement = 0
            if r.c51:
                try:
                    r.filler_remplacement = float(r.c51) / 100
                except Exception:
                    r.filler_remplacement = 0
