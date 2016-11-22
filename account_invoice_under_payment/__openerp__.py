# -*- coding: utf-8 -*-
# © 2016 Serpent Consulting Services Pvt. Ltd
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "Payment Order Under Payment",
    "summary": "Payment Order Under Payment",
    "version": "8.0.1.0.0",
    "category": "Accounting",
    "description": "Payment Order Under Payment",
    'website': 'http://www.serpentcs.com',
    "author": """Serpent Consulting Services Pvt. Ltd.,
                Agile Business Group,
                Odoo Community Association (OCA)""",
    "license": "AGPL-3",
    "depends": [
        "account_payment",
    ],
    "data": [
        "views/payment_line_views.xml",
        "views/move_line_views.xml",
        "views/invoice_view.xml",
    ],
    "installable": True,
}
