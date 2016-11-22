# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models, _


class PaymentOrderCreate(models.TransientModel):

    _inherit = 'payment.order.create'

    @api.multi
    def search_entries(self):
        line_obj = self.env['account.move.line']
        mod_obj = self.env['ir.model.data']
        context = self._context or {}
        search_due_date = self.duedate
        domain = [('under_payment', '=', False),
                  ('reconcile_id', '=', False),
                  ('account_id.type', '=', 'payable'),
                  ('credit', '>', 0),
                  ('account_id.reconcile', '=', True)]
        domain = domain + \
            ['|', ('date_maturity', '<=', search_due_date),
             ('date_maturity', '=', False)]
        line_ids = line_obj.search(domain).ids
        context = dict(context, line_ids=line_ids)
        dom = [('model', '=', 'ir.ui.view'),
               ('name', '=', 'view_create_payment_order_lines')]
        model_data_ids = mod_obj.search(dom)
        return {'name': _('Entry Lines'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.order.create',
                'views': [(model_data_ids.res_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                }
