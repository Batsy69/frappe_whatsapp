from . import __version__ as app_version

app_name = "frappe_whatsapp"
app_title = "Frappe Whatsapp"
app_publisher = "Shridhar Patil"
app_description = "WhatsApp integration for frappe"
app_email = "shridhar.p@zerodha.com"
app_license = "MIT"

# Includes in <head>
# ------------------
app_include_js = "/assets/frappe_whatsapp/js/frappe_whatsapp.js"

# Scheduler Events
# ----------------
scheduler_events = {
    "all": [
        "frappe_whatsapp.utils.trigger_whatsapp_notifications_all"
    ],
    "hourly": [
        "frappe_whatsapp.utils.trigger_whatsapp_notifications_hourly"
    ],
    "hourly_long": [
        "frappe_whatsapp.utils.trigger_whatsapp_notifications_hourly_long"
    ],
    "daily": [
        "frappe_whatsapp.utils.trigger_whatsapp_notifications_daily",
        "frappe_whatsapp.frappe_whatsapp.doctype.whatsapp_notification.whatsapp_notification.trigger_notifications",
    ],
    "daily_long": [
        "frappe_whatsapp.utils.trigger_whatsapp_notifications_daily_long",
    ],
    "weekly": [
        "frappe_whatsapp.utils.trigger_whatsapp_notifications_weekly",
    ],
    "weekly_long": [
        "frappe_whatsapp.utils.trigger_whatsapp_notifications_weekly_long",
    ],
    "monthly": [
        "frappe_whatsapp.utils.trigger_whatsapp_notifications_monthly",
    ],
    "monthly_long": [
        "frappe_whatsapp.utils.trigger_whatsapp_notifications_monthly_long",
    ],
}

# Document Events
# ---------------
doc_events = {
    "*": {
        "before_insert": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "after_insert": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "before_validate": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "validate": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "on_update": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "before_submit": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "on_submit": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "before_cancel": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "on_cancel": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "on_trash": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "after_delete": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "before_update_after_submit": "frappe_whatsapp.utils.run_server_script_for_doc_event",
        "on_update_after_submit": "frappe_whatsapp.utils.run_server_script_for_doc_event"
    }
}

# -------------------------------------------------------------------
# Override the core Notification DocType to hook in our WhatsApp logic
# -------------------------------------------------------------------
override_doctype_class = {
    "Notification": "frappe_whatsapp.overrides.notification.WhatsAppNotificationOverride"
}

# -------------------------------------------------------------------
# When uninstalling this app, run our cleanup to remove customizations
# -------------------------------------------------------------------
before_uninstall = "frappe_whatsapp.utils.clean_whatsapp_channel"
