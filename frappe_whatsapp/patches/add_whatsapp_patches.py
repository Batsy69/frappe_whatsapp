import frappe
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def execute():
    doctype, field, prop = "Notification", "channel", "options"
    meta = frappe.get_meta(doctype)
    opts = (meta.get_field(field).options or "").split("\n")
    if "frappe_whatsapp" not in opts:
        opts.append("frappe_whatsapp")
        make_property_setter(
            doctype, field, prop, "\n".join(opts), "Text"
        )
