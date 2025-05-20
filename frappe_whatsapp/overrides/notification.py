# File: apps/frappe_whatsapp/frappe_whatsapp/overrides/notification.py

import re
import frappe
from frappe_whatsapp.frappe_whatsapp.doctype.whatsapp_notification.whatsapp_notification import WhatsAppNotification, _post_and_log

class WhatsAppNotificationOverride(WhatsAppNotification):
    def send(self, doc):
        """
        Override Notification.send to hook into the frappe_whatsapp channel.
        """
        # 1) If not our channel, defer to base Notification
        if self.channel != "frappe_whatsapp":
            return super().send(doc)

        # 2) Ensure a template is selected
        if not getattr(self, 'custom_whatsapp_template', None):
            frappe.throw("Please select a WhatsApp Template")

        # 3) Make the core logic aware of our custom-template field
        self.template = self.custom_whatsapp_template

        # 4) Delegate to the core WhatsAppNotification push method
        return self.send_template_message(doc)

    def get_contact_list(self, doc):
        """
        Return a list of normalized phone numbers for each Role in self.recipients.
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
