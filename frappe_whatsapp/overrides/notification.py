import re
import frappe
from frappe.email.doctype.notification.notification import Notification
from frappe_whatsapp.frappe_whatsapp.doctype.whatsapp_notification.whatsapp_notification import (
    build_whatsapp_payload, _post_and_log
)

class WhatsAppNotificationOverride(Notification):
    def send(self, doc):
        # Only intercept our channel
        if self.channel != "frappe_whatsapp":
            return super().send(doc)

        if not self.custom_whatsapp_template:
            frappe.throw("Please select a WhatsApp Template")

        tpl = frappe.get_doc("WhatsApp Templates", self.custom_whatsapp_template)

        # Collect phone numbers based on Roles in Recipients
        numbers = set()
        for recipient in (self.recipients or []):
            role_name = recipient.receiver_by_role
            if not role_name:
                continue

            assignments = frappe.get_all(
                "Has Role",
                filters={
                    "role": role_name,
                    "parenttype": "User"
                },
                fields=["parent"]
            )
            for a in assignments:
                user_name = a.parent
                if not frappe.db.exists("User", user_name):
                    frappe.log_error(f"User {user_name} not found", "WhatsApp Notification Override")
                    continue

                user = frappe.get_doc("User", user_name)
                if user.mobile_no:
                    numbers.add(self._normalize_number(user.mobile_no))

        if not numbers:
            return

        # Evaluate condition if any
        ctx = doc.as_dict()
        if self.condition and not frappe.safe_eval(self.condition, None, ctx):
            return

        # Build payload
        components = tpl.build_components(doc, getattr(self, "whatsapp_message_fields", []))
        payload = {
            "template": {
                "name": tpl.whatsapp_name,
                "language": {"code": tpl.language},
                "components": components
            }
        }
        if self.attach_print:
            payload["pdf"] = frappe.utils.get_url_to_form(doc.doctype, doc.name)

        # Enqueue send for each number
        for to in numbers:
            payload["to"] = to
            frappe.enqueue(
                _post_and_log,
                queue="short",
                timeout=120,
                kwargs=dict(
                    url=frappe.get_conf().whatsapp_api_url,
                    data=payload,
                    doc=doc,
                    notification=self.name
                )
            )

    def _normalize_number(self, raw):
        num = re.sub(r'^(?:\+|00|0)+', '', str(raw))
        return num if num.startswith("91") else "91" + num
