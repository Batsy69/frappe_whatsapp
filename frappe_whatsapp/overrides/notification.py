# File: frappe_whatsapp/overrides/notification.py

from frappe.email.doctype.notification.notification import Notification
import frappe

class WhatsAppNotificationChannel(Notification):
    def send(self, doc):
        if doc.channel == "Whatsapp Message":
            numbers = []

            # Gather numbers from the Recipients child table, by role only
            for row in doc.recipients:
                # Skip rows with a false condition (if provided)
                if row.condition:
                    if not frappe.safe_eval(row.condition, None, {"doc": doc}):
                        continue

                # Only role-based recipients for your internal alerts
                if row.receiver_by_role:
                    users = frappe.get_all(
                        "User",
                        filters={
                            "enabled": 1,
                            "roles.role": row.receiver_by_role
                        },
                        fields=["mobile_no"]
                    )
                    for u in users:
                        if u.mobile_no:
                            numbers.append(u.mobile_no)

            # Guard against an empty list
            if not numbers:
                frappe.throw("No WhatsApp recipients found for the selected role(s).")

            # Hand off to your existing Bulk WhatsApp Message doctype
            bulk = frappe.new_doc("Bulk WhatsApp Message")
            bulk.recipients = numbers
            bulk.message = doc.message
            bulk.insert(ignore_permissions=True)
            bulk.submit()

        else:
            # Default to the standard Notification behavior for all other channels
            super(WhatsAppNotificationChannel, self).send(doc)
