# -*- coding: utf-8 -*-
# Copyright (c) 2019, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
from frappe.model.document import Document
from frappe.core.doctype.sms_settings.sms_settings import validate_receiver_nos
from toolz import compose

from sms_extras.api.sms import send_sms


_get_recipients = compose(validate_receiver_nos, lambda x: x.replace(",", "\n").split())


class SMSPortal(Document):
    def validate_balance(self):
        pass

    def request_sms(self):
        recipients = _get_recipients(self.recipients)
        self.validate_balance()
        send_sms(recipients, self.message, in_batch=self.batch_send)
