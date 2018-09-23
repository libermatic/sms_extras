# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe


def get_sms_text(template_name, doc):
    template = frappe.db.get_value(
        'SMS Template', template_name, 'content'
    )
    if not template:
        return None
    return frappe.render_template(template, {'doc': doc})
