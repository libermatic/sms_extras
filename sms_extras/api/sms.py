# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import today, get_first_day, get_last_day
from frappe.core.doctype.sms_settings.sms_settings import send_sms
import requests
from toolz import merge, compose


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


@frappe.whitelist()
def get_usage():
    query = frappe.db.sql(
        """
            SELECT SUM(no_of_sent_sms) FROM `tabSMS Log`
            WHERE sent_on BETWEEN '{first_day}' AND '{last_day}'
        """.format(
            first_day=compose(get_first_day, today)(),
            last_day=compose(get_last_day, today)(),
        )
    )
    sms_balance = 'N/A'
    settings = frappe.get_single('SMS Extras Settings')
    if settings.sms_balance_url:
        response = requests.get(settings.sms_balance_url)
        if settings.response_content_type == 'JSON':
            sms_balance = response.json().get(settings.response_field)
        else:
            sms_balance = response.text
    return {'sms_sent': query[0][0], 'sms_balance': sms_balance}
