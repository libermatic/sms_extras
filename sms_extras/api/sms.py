# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import today, get_first_day, get_last_day, cint
from frappe.core.doctype.sms_settings.sms_settings import (
    validate_receiver_nos,
    get_headers,
    send_request,
    create_sms_log,
)
import json
import requests
from functools import partial, reduce
from toolz import merge, compose, get, valmap, dissoc, unique


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

        send_sms(number, text)

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
    if settings.show_balance and settings.sms_balance_url:
        response = (
            requests.post(
                settings.sms_balance_url, data=json.loads(settings.sms_balance_payload)
            )
            if settings.sms_balance_method == "POST"
            else requests.get(settings.sms_balance_url)
        )
        sms_balance = (
            response.json().get(settings.response_field)
            if settings.response_content_type == "JSON"
            else cint(response.text)
        )
    return {"sms_sent": query[0][0] or 0, "sms_balance": sms_balance}


_get_receiver_list = compose(
    list,
    unique,
    validate_receiver_nos,
    lambda x: x.replace(",", "\n").split(),
    frappe.utils.cstr,
)


_eval_dynamic_params = partial(
    valmap,
    lambda x: frappe.safe_eval(
        x, eval_globals=frappe._dict(frappe=frappe._dict(utils=frappe.utils))
    ),
)


def _make_headers(ss, sx):
    get_dynamic_headers = compose(
        _eval_dynamic_params, lambda x: dissoc(x, "Accept"), get_headers
    )
    return merge(get_headers(ss), get_dynamic_headers(sx))


def _make_params(ss, sx):
    get_param_payload = compose(
        lambda params: reduce(
            lambda a, x: merge(a, {x.parameter: x.value}), params, {}
        ),
        partial(filter, lambda x: not x.header),
    )
    return merge(
        get_param_payload(ss.parameters),
        _eval_dynamic_params(get_param_payload(sx.parameters)),
    )


def send_sms(recipients, message):
    ss = frappe.get_single("SMS Settings")
    sx = frappe.get_single("SMS Extras Settings")
    headers = _make_headers(ss, sx)
    params = _make_params(ss, sx)

    receiver_list = _get_receiver_list(recipients)
    success_list = []
    for receiver in receiver_list:
        payload = merge(
            {
                ss.message_parameter: frappe.safe_decode(message).encode("utf-8"),
                ss.receiver_parameter: receiver,
            },
            params,
        )
        status = send_request(ss.sms_gateway_url, payload, headers, ss.use_post)
        if 200 <= status < 300:
            success_list.append(receiver)

    if success_list:
        create_sms_log(
            {
                "message": frappe.safe_decode(message).encode("utf-8"),
                "receiver_list": receiver_list,
            },
            sent_to=success_list,
        )


def send_multiple_sms(recipients, message):
    ss = frappe.get_single("SMS Settings")
    sx = frappe.get_single("SMS Extras Settings")
    headers = _make_headers(ss, sx)

    receiver_list = _get_receiver_list(recipients)
    payload = merge(
        {
            ss.message_parameter: frappe.safe_decode(message).encode("utf-8"),
            ss.receiver_parameter: ",".join(receiver_list),
        },
        _make_params(ss, sx),
    )
    status = send_request(ss.sms_gateway_url, payload, headers, ss.use_post)
    if 200 <= status < 300:
        create_sms_log(
            {
                "message": frappe.safe_decode(message).encode("utf-8"),
                "receiver_list": receiver_list,
            },
            sent_to=receiver_list,
        )


@frappe.whitelist()
def get_numbers_from_list(recipient_list):
    doc = frappe.get_doc("SMS Recipient List", recipient_list)
    if not doc:
        return None
    return [x.recipient_number for x in doc.recipients if not x.disabled]
