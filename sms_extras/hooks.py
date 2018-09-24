# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from . import __version__

app_name = "sms_extras"
app_version = __version__
app_title = "SMS Extras"
app_publisher = "Libermatic"
app_description = "Enhancements to ERPNext SMS module"
app_icon = "fa fa-comment"
app_color = "#FFEB3B"
app_email = "info@libermatic.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
app_include_css = [
    '/assets/sms_extras/css/usage_info.css',
]
app_include_js = [
    '/assets/js/sms_extras.min.js',
]

# include js, css files in header of web template
# web_include_css = "/assets/sms_extras/css/sms_extras.css"
# web_include_js = "/assets/sms_extras/js/sms_extras.js"

# include js in page
page_js = {
    'usage-info': 'public/js/usage_info.js',
}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = { #    "Role": "home_page" # }

# Website user home page (by function)
# get_website_user_home_page = "sms_extras.utils.get_home_page"

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Installation
# ------------

# before_install = "sms_extras.install.before_install"
# after_install = "sms_extras.install.after_install"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sms_extras.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
#     "Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
#     "Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#     "*": {
#         "on_update": "method",
#         "on_cancel": "method",
#         "on_trash": "method" #    }
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
#     "all": [
#         "sms_extras.tasks.all"
#     ],
#     "daily": [
#         "sms_extras.tasks.daily"
#     ],
#     "hourly": [
#         "sms_extras.tasks.hourly"
#     ],
#     "weekly": [
#         "sms_extras.tasks.weekly"
#     ]
#     "monthly": [
#         "sms_extras.tasks.monthly"
#     ]
# }

# Testing
# -------

# before_tests = "sms_extras.install.before_tests"

# Overriding Whitelisted Methods
# ------------------------------
#
# override_whitelisted_methods = {
#     "frappe.desk.doctype.event.event.get_events": "sms_extras.event.get_events"
# }
