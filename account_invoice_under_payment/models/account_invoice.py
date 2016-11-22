# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields, api


class AccountInvoice(models.Model):
    _inherit = "account.invoice"

    @api.multi
    @api.depends('payment_ids.under_payment')
    def _check_payment(self):
        for record in self:
            for payment_record in record.payment_ids:
                if payment_record.under_payment:
                    self.under_payment = True

    under_payment = fields.Boolean(
        'Under Payment', readonly=True, store=True, compute=_check_payment)
