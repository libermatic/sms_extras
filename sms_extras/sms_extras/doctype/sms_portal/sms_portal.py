# -*- coding: utf-8 -*-
# Copyright (c) 2019, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe.utils import cint
from frappe.model.document import Document
from frappe.utils.background_jobs import enqueue

from sms_extras.api.sms import send_multiple_sms, send_sms


class SMSPortal(Document):
    def validate_balance(self):
        pass

    @frappe.whitelist()
    def request_sms(self):
        self.validate_balance()
        enqueue(
            method=_enqueue_sms,
            queue="short",
            event="send_multiple_sms" if cint(self.batch_send) else send_sms,
            recipients=self.recipients,
            message=self.message,
            in_batch=cint(self.batch_send),
        )


def _enqueue_sms(recipients=[], message="", in_batch=False):
    if not in_batch:
        send_sms(recipients, message)
    else:
        send_multiple_sms(recipients, message)
