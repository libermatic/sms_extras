# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import today, get_first_day, get_last_day, cint
from frappe.core.doctype.sms_settings.sms_settings import send_sms
import requests
from toolz import merge, compose, get


def process(doc, method):
    sms_template = frappe.db.exists(
        "SMS Template",
        {"disabled": 0, "ref_doctype": doc.doctype, "event": method, "auto_trigger": 1},
    )
    if not sms_template:
        return

    template = frappe.get_doc("SMS Template", sms_template)

    if not _allowed(template.condition, doc):
        return

    try:
        number = _get_number(template.num_field, doc)
        text = _get_content(template.content, doc)

        # fix for json.loads casting to int during number validation
        send_sms('"{}"'.format(number), text)

        if template.save_com:
            _make_communication(
                {
                    "subject": "SMS: {} to {}".format(template.template_name, number),
                    "reference_doctype": doc.doctype,
                    "reference_name": doc.name,
                    "phone_no": number,
                    "content": text,
                }
            )
    except Exception:
        frappe.log_error(frappe.get_traceback())


def _allowed(condition, doc):
    if not condition:
        return True
    return frappe.safe_eval(
        condition,
        eval_globals=dict(
            frappe=frappe._dict(
                db=frappe._dict(
                    get_value=frappe.db.get_value, get_list=frappe.db.get_list
                ),
                session=frappe.session,
            )
        ),
        eval_locals=doc.as_dict(),
    )


def _get_number(field, doc):
    if "." not in field:
        return get(field, doc.as_dict())

    link_field, source_fieldname = field.split(".", 1)
    meta = frappe.get_meta(doc.doctype)
    link_df = meta.get_field(link_field)
    return frappe.db.get_value(
        link_df.options, get(link_field, doc.as_dict()), source_fieldname
    )


def _get_content(template, doc):
    return frappe.render_template(template, doc.as_dict())


def _make_communication(args):
    return frappe.get_doc(
        merge(
            {
                "doctype": "Communication",
                "communication_type": "Communication",
                "communication_medium": "SMS",
            },
            args,
        )
    ).insert()


def get_sms_text(template_name, doc):
    template = frappe.db.get_value("SMS Template", template_name, "content")
    if not template:
        return None
    return frappe.render_template(template, {"doc": doc})


def request_sms(number, content, communication=None):
    try:
        # fix for json.loads casting to int during number validation
        send_sms('"{}"'.format(number), content)
        if communication:
            frappe.get_doc(
                merge(
                    {
                        "doctype": "Communication",
                        "communication_type": "Communication",
                        "communication_medium": "SMS",
                        "subject": "SMS: {}".format(number),
                    },
                    communication,
                    {"phone_no": number, "content": content},
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
    sms_balance = 0
    settings = frappe.get_single("SMS Extras Settings")
    if settings.sms_balance_url:
        response = requests.get(settings.sms_balance_url)
        if settings.response_content_type == "JSON":
            sms_balance = response.json().get(settings.response_field)
        else:
            sms_balance = cint(response.text)
    return {"sms_sent": query[0][0] or 0, "sms_balance": sms_balance}
