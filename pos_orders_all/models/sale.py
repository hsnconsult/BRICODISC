# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

import logging

import psycopg2
from odoo import fields, models, api, _, tools

_logger = logging.getLogger(__name__)


class PosConfiguration(models.Model):
    _inherit = 'pos.config'

    discount_type = fields.Selection([('percentage', "Percentage"), ('fixed', "Fixed")], string='Discount Type',
                                     default='percentage', help='Seller can apply different Discount Type in POS.')


class PosOrderInherit(models.Model):
    _inherit = 'pos.order'

    coupon_id = fields.Many2one('pos.gift.coupon')
    discount_type = fields.Char(string='Discount Type')

    def _prepare_invoice_line(self, order_line):
        res = super(PosOrderInherit, self)._prepare_invoice_line(order_line)
        res.update({
            'pos_order_line_id': order_line.id,
            'pos_order_id': self.id
        })
        return res

    def action_pos_order_invoice(self):
        moves = self.env['account.move']

        for order in self:
            # Force company for all SUPERUSER_ID action
            if order.account_move:
                moves += order.account_move
                continue

            if not order.partner_id:
                raise UserError(_('Please provide a partner for the sale.'))

            move_vals = {
                'pos_order_id': order.id,
                'invoice_payment_ref': order.name,
                'invoice_origin': order.name,
                'journal_id': order.session_id.config_id.invoice_journal_id.id,
                'type': 'out_invoice' if order.amount_total >= 0 else 'out_refund',
                'ref': order.name,
                'partner_id': order.partner_id.id,
                'narration': order.note or '',
                # considering partner's sale pricelist's currency
                'currency_id': order.pricelist_id.currency_id.id,
                'invoice_user_id': order.user_id.id,
                'invoice_date': fields.Date.today(),
                'fiscal_position_id': order.fiscal_position_id.id,
                'invoice_line_ids': [(0, None, order._prepare_invoice_line(line)) for line in order.lines],
            }
            new_move = moves.sudo() \
                .with_context(default_type=move_vals['type'], force_company=order.company_id.id) \
                .create(move_vals)
            message = _(
                "This invoice has been created from the point of sale session: <a href=# data-oe-model=pos.order data-oe-id=%d>%s</a>") % (
                          order.id, order.name)
            new_move.message_post(body=message)
            order.write({'account_move': new_move.id, 'state': 'invoiced'})
            moves += new_move

        if not moves:
            return {}

        return {
            'name': _('Customer Invoice'),
            'view_mode': 'form',
            'view_id': self.env.ref('account.view_move_form').id,
            'res_model': 'account.move',
            'context': "{'type':'out_invoice'}",
            'type': 'ir.actions.act_window',
            'nodestroy': True,
            'target': 'current',
            'res_id': moves and moves.ids[0] or False,
        }

    @api.model
    def _amount_line_tax(self, line, fiscal_position_id):
        taxes = line.tax_ids.filtered(lambda t: t.company_id.id == line.order_id.company_id.id)
        if fiscal_position_id:
            taxes = fiscal_position_id.map_tax(taxes, line.product_id, line.order_id.partner_id)
        if line.discount_line_type == 'Percentage':
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
        else:
            price = line.price_unit - line.discount
        taxes = taxes.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty, product=line.product_id,
                                  partner=line.order_id.partner_id or False)['taxes']
        return sum(tax.get('amount', 0.0) for tax in taxes)

    @api.onchange('payment_ids', 'lines')
    def _onchange_amount_all(self):
        for order in self:
            currency = order.pricelist_id.currency_id
            order.amount_paid = sum(payment.amount for payment in order.payment_ids)
            order.amount_return = sum(payment.amount < 0 and payment.amount or 0 for payment in order.payment_ids)
            order.amount_tax = currency.round(
                sum(self._amount_line_tax(line, order.fiscal_position_id) for line in order.lines))
            amount_untaxed = currency.round(sum(line.price_subtotal for line in order.lines))
            order.amount_total = order.amount_tax + amount_untaxed
        # order.amount_total = order.amount_paid

    @api.model
    def _process_order(self, order, draft, existing_order):
        """Create or update an pos.order from a given dictionary.

        :param pos_order: dictionary representing the order.
        :type pos_order: dict.
        :param draft: Indicate that the pos_order is not validated yet.
        :type draft: bool.
        :param existing_order: order to be updated or False.
        :type existing_order: pos.order.
        :returns number pos_order id
        """
        order = order['data']
        pos_session = self.env['pos.session'].browse(order['pos_session_id'])
        if pos_session.state == 'closing_control' or pos_session.state == 'closed':
            order['pos_session_id'] = self._get_valid_session(order).id

        pos_order = False
        if not existing_order:
            pos_order = self.create(self._order_fields(order))
        else:
            pos_order = existing_order
            pos_order.lines.unlink()
            order['user_id'] = pos_order.user_id.id
            pos_order.write(self._order_fields(order))

        if pos_order.config_id.discount_type == 'percentage':
            pos_order.update({'discount_type': "Percentage"})
            pos_order.lines.update({'discount_line_type': "Percentage"})
        if pos_order.config_id.discount_type == 'fixed':
            pos_order.update({'discount_type': "Fixed"})
            pos_order.lines.update({'discount_line_type': "Fixed"})

        coupon_id = order.get('coupon_id', False)
        coup_max_amount = order.get('coup_maxamount', False)
        pos_order.write({'coupon_id': coupon_id})
        pos_order.coupon_id.update({'coupon_count': pos_order.coupon_id.coupon_count + 1})
        pos_order.coupon_id.update({'max_amount': coup_max_amount})

        self._process_payment_lines(order, pos_order, pos_session, draft)

        if not draft:
            try:
                pos_order.action_pos_order_paid()
            except psycopg2.DatabaseError:
                # do not hide transactional errors, the order(s) won't be saved!
                raise
            except Exception as e:
                _logger.error('Could not fully process the POS Order: %s', tools.ustr(e))

        if pos_order.to_invoice and pos_order.state == 'paid':
            pos_order.action_pos_order_invoice()
            if pos_order.discount_type and pos_order.discount_type == "Fixed":
                invoice = pos_order.account_move
                for line in invoice.invoice_line_ids:
                    pos_line = line.pos_order_line_id
                    if pos_line and pos_line.discount_line_type == "Fixed":
                        line.write({'price_unit': pos_line.price_unit})
            pos_order.account_move.sudo().with_context(force_company=self.env.user.company_id.id).post()

        return pos_order.id


class PosOrderLineInherit(models.Model):
    _inherit = 'pos.order.line'

    discount_line_type = fields.Char(string='Discount Type', readonly=True)

    def _compute_amount_line_all(self):
        for line in self:
            fpos = line.order_id.fiscal_position_id
            tax_ids_after_fiscal_position = fpos.map_tax(line.tax_ids, line.product_id,
                                                         line.order_id.partner_id) if fpos else line.tax_ids

            if line.discount_line_type == "Fixed":
                price = line.price_unit - line.discount

            else:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = tax_ids_after_fiscal_position.compute_all(price, line.order_id.pricelist_id.currency_id, line.qty,
                                                              product=line.product_id, partner=line.order_id.partner_id)

            line.update({
                'price_subtotal_incl': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
