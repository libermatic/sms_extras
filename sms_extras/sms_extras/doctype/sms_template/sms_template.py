# -*- coding: utf-8 -*-
# Copyright (c) 2018, Libermatic and contributors
# For license information, please see license.txt

from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.utils import cint
from frappe.model.document import Document


class SMSTemplate(Document):
    def validate(self):
        if self.type != "Transactional" and cint(self.auto_trigger):
            frappe.throw(_("Only Transactional template can be auto-triggered"))
        if cint(self.auto_trigger) and not self.ref_doctype:
            frappe.throw(_("Reference DocType required for auto-triggered templates"))
        if cint(self.auto_trigger) and not self.num_field:
            frappe.throw(_("Recipient No Field required for auto-triggered templates"))
        if cint(self.save_com) and not cint(self.auto_trigger):
            frappe.throw(
                _("Communications can only be saved for auto-triggered templates")
            )
