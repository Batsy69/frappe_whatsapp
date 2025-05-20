# File: apps/frappe_whatsapp/frappe_whatsapp/overrides/notification.py

import re
import frappe
from frappe_whatsapp.frappe_whatsapp.doctype.whatsapp_notification.whatsapp_notification import (
    WhatsAppNotification, _post_and_log
)

class WhatsAppNotificationOverride(WhatsAppNotification):
    @property
    def disabled(self):
        """
        Map the standard Notification.doctype `enabled` field to WhatsAppNotification's `disabled` logic.
        """
        # Notification.doctype uses 'enabled' boolean; invert it for 'disabled'
        return not getattr(self, 'enabled', False)

    def send(self, doc):
        """
        Intercept only our custom WhatsApp channel, then delegate to core send.
        """
        if self.channel != "frappe_whatsapp":
            return super().send(doc)

        if not getattr(self, 'custom_whatsapp_template', None):
            frappe.throw("Please select a WhatsApp Template")

        # Provide the core class with the template
        self.template = self.custom_whatsapp_template

        # Let the core class build, send, and log the WhatsApp message
        return self.send_template_message(doc)

    def get_contact_list(self, doc):
        """
        Return normalized phone numbers for each Role in Recipients.
        """
        numbers = set()
        for recipient in (self.recipients or []):
            role_name = recipient.receiver_by_role
            if not role_name:
                continue

            assignments = frappe.get_all(
                "Has Role",
                filters={"role": role_name, "parenttype": "User"},
                fields=["parent"]
            )
            for a in assignments:
                user_name = a.parent
                if not frappe.db.exists("User", user_name):
                    frappe.log_error(f"User {user_name} not found", "WhatsApp Notification Override")
                    continue

                mobile = frappe.get_value("User", user_name, "mobile_no")
                if mobile:
                    num = re.sub(r'^(?:\+|00|0)+', '', str(mobile))
                    numbers.add(num if num.startswith("91") else "91" + num)

        return list(numbers)
