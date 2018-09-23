# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.core.doctype.sms_settings.sms_settings import send_sms
from toolz import merge


def get_sms_text(template_name, doc):
    template = frappe.db.get_value(
        'SMS Template', template_name, 'content'
    )
    if not template:
        return None
    return frappe.render_template(template, {'doc': doc})


def request_sms(number, content, communication=None):
    try:
        # fix for json.loads casting to int during number validation
        send_sms('"{}"'.format(number), content)
        if communication:
            frappe.get_doc(
                merge(
                    {
                        'doctype': 'Communication',
                        'communication_type': 'Communication',
                        'communication_medium': 'SMS',
                        'subject': 'SMS: {}'.format(number)
                    },
                    communication,
                    {
                        'phone_no': number,
                        'content': content,
                    }
                )
            ).insert()
    except Exception:
        frappe.log_error(frappe.get_traceback())
