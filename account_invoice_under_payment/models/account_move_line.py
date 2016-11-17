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

from openerp import models, fields, api


class AccountMoveline(models.Model):
    _inherit = "account.move.line"

    @api.multi
    @api.depends('payment_line_ids.failed')
    def _check_payment(self):
        for record in self:
            if any([not x.failed for x in record.payment_line_ids]):
                record.under_payment = True

    payment_line_ids = fields.One2many(
        'payment.line', 'move_line_id', string='Payment Lines', readonly=True)

    under_payment = fields.Boolean(
        'Under Payment', readonly=True, store=True, compute=_check_payment)
