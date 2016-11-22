.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :alt: License: AGPL-3

=============================
Account Invoice Under Payment
=============================

When user confirms a payment order (payment.order), the invoices contained in it should be set as 'under payment'.
This would make more easy to control the invoices that have already been put in payment.
This is also useful while creating a new payment order, allowing the user to only see the open credits (account.move.line), avoiding to see the "under payments" ones.
Also, it should be possible to set a payment line as failed (to indicate if something went wrong with the bank or other)

Installation
============

This module depends on:

* account_payment

Configuration
=============

There is nothing to configure.

Known issues / Roadmap
======================

 * No known issues.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-payment/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/account-payment/issues/new?body=module:%20account_invoice_under_payment_mode%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Contributors
------------
- Serpent Consulting Services Pvt. Ltd.
- Agile Business Group

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
