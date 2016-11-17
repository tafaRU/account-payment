# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2016-Today Serpent Consulting Services PVT. LTD.
#    (<http://www.serpentcs.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>
#
# ---------------------------------------------------------------------------

from openerp.osv import osv
from openerp.tools.translate import _


class PaymentOrdercreate(osv.osv_memory):

    _inherit = 'payment.order.create'

    def search_entries(self, cr, uid, ids, context=None):
        line_obj = self.pool.get('account.move.line')
        mod_obj = self.pool.get('ir.model.data')
        if context is None:
            context = {}
        data = self.browse(cr, uid, ids, context=context)[0]
        search_due_date = data.duedate
        domain = [('under_payment', '=', False),
                  ('reconcile_id', '=', False),
                  ('account_id.type', '=', 'payable'),
                  ('credit', '>', 0),
                  ('account_id.reconcile', '=', True)]
        domain = domain + \
            ['|', ('date_maturity', '<=', search_due_date),
             ('date_maturity', '=', False)]
        line_ids = line_obj.search(cr, uid, domain, context=context)
        context = dict(context, line_ids=line_ids)
        dom = [('model', '=', 'ir.ui.view'),
               ('name', '=', 'view_create_payment_order_lines')]
        model_data_ids = mod_obj.search(cr, uid, dom, context=context)
        resource_id = mod_obj.read(cr, uid, model_data_ids, fields=[
                                   'res_id'], context=context)[0]['res_id']
        return {'name': _('Entry Lines'),
                'context': context,
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'payment.order.create',
                'views': [(resource_id, 'form')],
                'type': 'ir.actions.act_window',
                'target': 'new',
                }
