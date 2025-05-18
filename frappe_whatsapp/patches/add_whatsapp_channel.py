import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
    """
    Inject 'frappe_whatsapp' into the Notification.channel select options
    every time bench migrate runs.
    """
    meta = frappe.get_meta("Notification")
    opts = (meta.get_field("channel").options or "").split("\n")

    if "frappe_whatsapp" not in opts:
        opts.append("frappe_whatsapp")
        make_property_setter(
            "Notification",      # DocType
            "channel",           # fieldname
            "options",           # property to override
            "\n".join(opts),     # new newline-delimited options
            "Text"               # property type
        )
        # Clear cache so the dropdown updates immediately in the UI
        frappe.clear_cache(doctype="Notification")
