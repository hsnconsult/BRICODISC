# -*- coding: utf-8 -*-

from odoo import http, _
from odoo.addons.stock_barcode.controllers.main import StockBarcodeController
from odoo.http import request


class StockBarcodeControllerInherited(StockBarcodeController):
    @http.route('/stock_barcode/scan_from_main_menu', type='json', auth='user')
    def main_menu(self, barcode, **kw):
        ret_open_picking_b = self.try_open_picking_batch(barcode)
        print("=====> menuuu")
        if ret_open_picking_b:
            return ret_open_picking_b
        super(StockBarcodeControllerInherited, self).main_menu(barcode)

    def try_open_picking_batch(self, barcode):
        """ If barcode represents a picking, open it
        """
        print("=====> picking bacthh")
        corresponding_pb = request.env['stock.picking.batch'].search([
            ('name', '=', barcode),
        ], limit=1)
        if corresponding_pb:
            return self.get_action_batch(corresponding_pb.id)
        return False

    def get_action_batch(self, bpicking_id):
        """
        return the action to display the picking. We choose between the traditionnal
        form view and the new client action
        """
        use_form_handler = request.env['ir.config_parameter'].sudo().get_param('stock_barcode.use_form_handler')
        print("1")
        if use_form_handler:
            view_id = request.env.ref('stock_picking_batch.stock_picking_batch_form').id
            print("1====")
            return {
                'action': {
                    'name': _('Open batch picking form'),
                    'res_model': 'stock.picking.batch',
                    'view_mode': 'form',
                    'view_id': view_id,
                    'views': [(view_id, 'form')],
                    'type': 'ir.actions.act_window',
                    'res_id': bpicking_id,
                }
            }
        else:
            print(bpicking_id)
            action = request.env.ref('stock_barcode_picking_batch.stock_barcode_picking_batch_client_action').read()[0]
            params = {
                'model': 'stock.picking.batch',
                'picking_batch_id': bpicking_id,
            }
            action = dict(action, target='fullscreen', params=params)
            action['context'] = {'active_id': bpicking_id}
            action = {'action': action}
            print("1---")
            return action
