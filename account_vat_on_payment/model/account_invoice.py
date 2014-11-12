# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2011-2012 Domsense s.r.l. (<http://www.domsense.com>).
#    Copyright (C) 2014 Agile Business Group sagl (<http://www.agilebg.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp import models, fields, api, _
from openerp.exceptions import Warning


class AccountInvoice(models.Model):

    def _get_vat_on_payment(self):
        return self.env.user.company_id.vat_on_payment

    def _set_vat_on_payment_account(self, line_tuple):
        account = self.env['account.account'].browse(
            line_tuple[2]['account_id'])
        if account.type not in ['receivable', 'payable']:
            if not account.vat_on_payment_related_account_id:
                raise Warning(
                    _('Error'),
                    _("The invoice is 'VAT on payment' but "
                      "account %s does not have a related shadow "
                      "account")
                    % account.name)
            line_tuple[2]['real_account_id'] = line_tuple[
                2]['account_id']
            line_tuple[2]['account_id'] = (
                account.vat_on_payment_related_account_id.id)
        return line_tuple

    def _set_vat_on_payment_tax_code(self, line_tuple):
        tax_code = self.env['account.tax.code'].browse(
            line_tuple[2]['tax_code_id'])
        if not tax_code.vat_on_payment_related_tax_code_id:
            raise Warning(
                _('Error'),
                _("The invoice is 'VAT on payment' but "
                  "tax code %s does not have a related shadow "
                  "tax code")
                % tax_code.name)
        line_tuple[2]['real_tax_code_id'] = line_tuple[
            2]['tax_code_id']
        line_tuple[2]['tax_code_id'] = (
            tax_code.vat_on_payment_related_tax_code_id.id)
        return line_tuple

    @api.multi
    def finalize_invoice_move_lines(self, move_lines):
        """
        Use shadow accounts for journal entry to be generated, according to
        account and tax code related records
        """
        invoices = self.with_context(self.env['res.users'].context_get())
        move_lines = super(invoices, self).finalize_invoice_move_lines(
            move_lines)
        new_move_lines = []
        for line_tuple in move_lines:
            if self.vat_on_payment:
                if line_tuple[2].get('account_id', False):
                    line_tuple = self._set_vat_on_payment_account(line_tuple)
                if line_tuple[2].get('tax_code_id', False):
                    line_tuple = self._set_vat_on_payment_tax_code(line_tuple)
            new_move_lines.append(line_tuple)
        return new_move_lines

    @api.multi
    def onchange_partner_id(
            self, type, partner_id, date_invoice=False,
            payment_term=False, partner_bank_id=False, company_id=False
    ):
        res = super(AccountInvoice, self).onchange_partner_id(
            type, partner_id, date_invoice, payment_term, partner_bank_id,
            company_id)
        # default value for VAT on Payment is changed every time the
        # customer/supplier is changed
        if partner_id:
            p = self.env['res.partner'].browse(partner_id)
            p.with_context(self.env['res.users'].context_get())
            if p.property_account_position:
                res['value'][
                    'vat_on_payment'
                ] = p.property_account_position.default_has_vat_on_payment
        return res

    _inherit = "account.invoice"

    vat_on_payment = fields.Boolean(
        string='Vat on payment', default=_get_vat_on_payment),
