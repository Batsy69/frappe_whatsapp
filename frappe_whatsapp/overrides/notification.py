import re
import frappe
from frappe.core.doctype.notification.notification import Notification
from frappe_whatsapp.doctype.whatsapp_notification.whatsapp_notification import (
    build_whatsapp_payload, _post_and_log
)

class WhatsAppNotificationOverride(Notification):
    def send(self, doc):
        # 1) only handle our channel
        if self.channel != "frappe_whatsapp":
            return super().send(doc)

        # 2) load & validate template link
        if not self.whatsapp_template:
            frappe.throw("Please select a WhatsApp Template")

        tpl = frappe.get_doc("WhatsApp Template", self.whatsapp_template)

        # 3) gather & normalize numbers from Recipients by role
        numbers = set()
        for row in (self.recipients or []):
            if row.receiver_by_role:
                users = frappe.get_all(
                    "Has Role",
                    filters={"role": row.receiver_by_role},
                    fields=["parent"]
                )
                for u in users:
                    user = frappe.get_doc("User", u.parent)
                    if user.phone:
                        numbers.add(self._normalize_number(user.phone))

        if not numbers:
            return

        # 4) optional condition
        ctx = doc.as_dict()
        if self.condition and not frappe.safe_eval(self.condition, None, ctx):
            return

        # 5) build payload (template + components + optional PDF)
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

        # 6) enqueue one API call per number
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
        # enforce country code if needed, e.g. "91"
        return num if num.startswith("91") else "91" + num
