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

Usage
=====

To use this module, you need to:

1. Create payment order and payment lines

* The module gives an ability to the end user to choose which invoice is unpaid yet. At the Payment line, once can easily choose to set a flag to indicate whether
the payment has failed or through.
* Set the 'failed' flag on payment line, the corresponding Journal Entries and Invoices will show that the invoice is still under payment.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/96/8.0

Known issues / Roadmap
======================

 * No known issues.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/account-payment/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------
* Serpent Consulting Services Pvt. Ltd.
* Agile Business Group

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
