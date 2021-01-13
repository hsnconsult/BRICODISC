# -*- coding: utf-8 -*-

from odoo import models, fields


class StockPickingBatch(models.Model):
    _inherit = 'stock.picking.batch'

    barcode = fields.Char("Barcode")

    def confirm_picking(self):
        res = super(StockPickingBatch, self).confirm_picking()
        if res:
            self.message_subscribe(partner_ids=self.user_id.partner_id.ids)
            self.activity_schedule('brico_base.batch_to_confirm_activity',
                                   user_id=self.user_id.id)
        return res

    def done(self):
        res = super(StockPickingBatch, self).done()
        if res:
            self.activity_feedback(['brico_base.batch_to_confirm_activity', ])
        return res

    def cancel_picking(self):
        res = super(StockPickingBatch, self).cancel_picking()
        if res:
            self.activity_unlink(['brico_base.batch_to_confirm_activity', ])
        return res
