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


class AccountVoucher(models.Model):
    _inherit = "account.voucher"

    shadow_move_id = fields.Many2one(
        'account.move', string='Shadow Entry', readonly=True),

    def is_vat_on_payment(self, voucher):
        vat_on_p = 0
        valid_lines = 0
        if voucher.type in ('payment', 'receipt'):
            for line in voucher.line_ids:
                if line.amount:
                    valid_lines += 1
                    if (
                        line.move_line_id and line.move_line_id.invoice
                        and line.move_line_id.invoice.vat_on_payment
                    ):
                        vat_on_p += 1
            if vat_on_p and vat_on_p != valid_lines:
                raise Warning(
                    _('Error'),
                    _("Can't handle VAT on payment if not every invoice "
                      "is on a VAT on payment treatment"))
        return vat_on_p

    def _compute_allocated_amount(self, voucher, allocated=0, write_off=0):
        # compute the VAT or base line proportionally to
        # the paid amount
        allocated_amount = allocated + write_off
        if (
            voucher.exclude_write_off
            and voucher.payment_option == 'with_writeoff'
        ):
            # avoid including write-off if set in voucher.
            # That means: use the invoice's total
            # (as we are in 'full reconcile' case)
            allocated_amount = allocated
        return allocated_amount

    def _compute_new_line_amount(
            self, voucher, inv_move_line, amounts_by_invoice, invoice
    ):
        currency_obj = self.pool.get('res.currency')
        allocated_amount = self._compute_allocated_amount(
            voucher,
            allocated=amounts_by_invoice[invoice.id]['allocated'],
            write_off=amounts_by_invoice[invoice.id]['write-off'],
        )
        new_line_amount = currency_obj.round(
            voucher.company_id.currency_id,
            (allocated_amount / amounts_by_invoice[invoice.id]['total'])
            *
            (inv_move_line.credit or inv_move_line.debit)
        )
        return new_line_amount

    def _compute_new_line_currency_amount(
            self, voucher, inv_move_line, amounts_by_invoice, invoice
    ):
        currency = self.env['res.currency']
        new_line_amount_curr = False
        if (
            amounts_by_invoice[invoice.id].get('allocated_currency')
            and amounts_by_invoice[invoice.id].get('foreign_currency_id')
        ):
            for_curr = currency.browse(
                amounts_by_invoice[invoice.id]['foreign_currency_id']
            )
            allocated_amount = self._compute_allocated_amount(
                voucher,
                allocated=amounts_by_invoice[invoice.id]['allocated_currency'],
                write_off=amounts_by_invoice[invoice.id]['currency-write-off'],
            )
            new_line_amount_curr = currency.round(
                for_curr,
                (
                    allocated_amount /
                    amounts_by_invoice[invoice.id]['total_currency']
                )
                *
                (inv_move_line.amount_currency)
            )
        return new_line_amount_curr

    def _prepare_real_move_line(
            self, inv_move_line, new_line_amount,
            new_line_amount_curr, foreign_curr_id
    ):
        if not inv_move_line.real_account_id:
            raise Warning(
                _('Error'),
                _("We are on a VAT on payment treatment "
                  "but move line %s does not have a related "
                  "real account")
                % inv_move_line.name)
        vals = {
            'name': inv_move_line.name,
            'account_id': inv_move_line.real_account_id.id,
            'credit': (inv_move_line.credit and new_line_amount or 0.0),
            'debit': (inv_move_line.debit and new_line_amount or 0.0),
            'type': 'real',
            'partner_id': (
                inv_move_line.partner_id
                and inv_move_line.partner_id.id or False)
        }
        if new_line_amount_curr:
            vals['amount_currency'] = new_line_amount_curr
            vals['currency_id'] = foreign_curr_id
        if inv_move_line.tax_code_id:
            if not inv_move_line.real_tax_code_id:
                raise Warning(
                    _('Error'),
                    _("We are on a VAT on payment "
                      "treatment but move line %s does not "
                      "have a related real tax code")
                    % inv_move_line.name
                )
            vals['tax_code_id'] = inv_move_line.real_tax_code_id.id
            if inv_move_line.tax_amount < 0:
                vals['tax_amount'] = -new_line_amount
            else:
                vals['tax_amount'] = new_line_amount
        return vals

    def _prepare_shadow_move_line(self, inv_move_line, new_line_amount):
        vals = {
            'name': inv_move_line.name,
            'account_id': inv_move_line.account_id.id,
            'credit': (
                inv_move_line.debit
                and new_line_amount or 0.0),
            'debit': (
                inv_move_line.credit
                and new_line_amount or 0.0),
            'type': 'shadow',
            'partner_id': (
                inv_move_line.partner_id
                and inv_move_line.partner_id.id or False)
        }
        if inv_move_line.tax_code_id:
            vals[
                'tax_code_id'
            ] = inv_move_line.tax_code_id.id
            if inv_move_line.tax_amount < 0:
                vals['tax_amount'] = new_line_amount
            else:
                vals['tax_amount'] = -new_line_amount
        return vals

    def _prepare_shadow_move(self, voucher):
        return {
            'journal_id': (
                voucher.journal_id.vat_on_payment_related_journal_id.id
            ),
            'period_id': voucher.move_id.period_id.id,
            'date': voucher.move_id.date,
        }

    def _move_payment_lines_to_shadow_entry(self, voucher, shadow_move_id):
        for line in voucher.move_ids:
            if line.account_id.type != 'liquidity':
                # If the line is related to write-off and user doesn't
                # want to compute the tax including write-off,
                # write-off move line must stay on the real move
                if not (
                    voucher.exclude_write_off
                    and voucher.payment_option == 'with_writeoff'
                    and line.account_id.id
                        == voucher.writeoff_acc_id.id
                ):
                    line.write({
                        'move_id': shadow_move_id,
                    }, update_check=False)
                # this will allow user to see the real entry from
                # invoice payment tab
                if (
                    line.account_id.type == 'receivable'
                    or line.account_id.type == 'payable'
                ):
                    line.write({
                        'real_payment_move_id': voucher.move_id.id,
                    })
        return True

    def _create_vat_on_payment_move(self, voucher):
        move_line = self.env['account.move.line']
        move = self.env['account.move']
        if not voucher.journal_id.vat_on_payment_related_journal_id:
            raise Warning(
                _('Error'),
                _("We are on a VAT on payment treatment "
                  "but journal %s does not have a related shadow "
                  "journal")
                % voucher.journal_id.name)
        lines_to_create = []
        amounts_by_invoice = super(
            AccountVoucher, self
        ).allocated_amounts_grouped_by_invoice(voucher)
        for inv_id in amounts_by_invoice:
            invoice = self.env['account.invoice'].browse(inv_id)
            for inv_move_line in invoice.move_id.line_id:
                if (
                    inv_move_line.account_id.type != 'receivable'
                    and inv_move_line.account_id.type != 'payable'
                ):
                    new_line_amount = self._compute_new_line_amount(
                        voucher, inv_move_line,
                        amounts_by_invoice, invoice
                    )
                    new_line_amount_curr = (
                        self._compute_new_line_currency_amount(
                            voucher, inv_move_line,
                            amounts_by_invoice, invoice,
                        )
                    )
                    foreign_currency_id = amounts_by_invoice[
                        invoice.id]['foreign_currency_id']
                    real_vals = self._prepare_real_move_line(
                        inv_move_line, new_line_amount,
                        new_line_amount_curr, foreign_currency_id,
                    )
                    lines_to_create.append(real_vals)

                    shadow_vals = self._prepare_shadow_move_line(
                        inv_move_line, new_line_amount,
                    )
                    lines_to_create.append(shadow_vals)

        journal_id = (
            voucher.journal_id.vat_on_payment_related_journal_id.id)
        period_id = voucher.move_id.period_id.id
        shadow_move_id = move.with_context(
            journal_id=journal_id, period_id=period_id).create(
                self._prepare_shadow_move(voucher))

        self._move_payment_lines_to_shadow_entry(voucher, shadow_move_id)

        for line_to_create in lines_to_create:
            if line_to_create['type'] == 'real':
                line_to_create['move_id'] = voucher.move_id.id
            elif line_to_create['type'] == 'shadow':
                line_to_create['move_id'] = shadow_move_id
            del line_to_create['type']

            move_line.create(line_to_create)

        voucher.write({'shadow_move_id': shadow_move_id})

        super(AccountVoucher, self).balance_move(shadow_move_id)
        super(AccountVoucher, self).balance_move(voucher.move_id.id)
        return True

    @api.multi
    def action_move_line_create(self):
        journal = self.env['account.journal']
        res = False
        for voucher in self:
            entry_posted = voucher.journal_id.entry_posted
            # disable the 'skip draft state' option because "mixed" entry
            # (shadow + real) won't pass validation. Anyway every entry will be
            # posted later (if 'entry_posted' is enabled)
            if entry_posted:
                journal.write(
                    voucher.journal_id.id, {'entry_posted': False})
            res = super(AccountVoucher, self).action_move_line_create(
                [voucher.id])
            # because 'move_id' has been updated by 'action_move_line_create'
            voucher.refresh()
            if entry_posted:
                journal.write(
                    voucher.journal_id.id, {'entry_posted': True})
            if self.is_vat_on_payment(voucher):
                self._create_vat_on_payment_move(voucher)

        return res

    @api.multi
    def cancel_voucher(self):
        res = super(AccountVoucher, self).cancel_voucher()
        reconcile = self.env['account.move.reconcile']
        move = self.env['account.move']
        for voucher in self:
            recs = []
            if voucher.shadow_move_id:
                for line in voucher.shadow_move_id.line_id:
                    if line.reconcile_id:
                        recs += [line.reconcile_id.id]
                    if line.reconcile_partial_id:
                        recs += [line.reconcile_partial_id.id]

                reconcile.unlink(recs)

                if voucher.shadow_move_id:
                    move.button_cancel(
                        [voucher.shadow_move_id.id])
                    move.unlink([voucher.shadow_move_id.id])
        return res
