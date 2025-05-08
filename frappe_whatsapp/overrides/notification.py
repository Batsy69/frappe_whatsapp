# File: frappe_whatsapp/overrides/notification.py

from frappe.email.doctype.notification.notification import Notification
import frappe

class WhatsAppNotificationChannel(Notification):
    def send(self, doc):
        # `self` is the Notification record, `doc` is the Sales Order (or whatever ref. doctype)
        if self.channel == "Whatsapp Message":
            numbers = []

            # Loop through the Notification Recipient child‐table on *this* Notification
            for row in self.recipients:
                # 1) Skip by condition if provided
                if row.condition:
                    if not frappe.safe_eval(row.condition, None, {"doc": doc}):
                        continue

                # 2) Role‐based lookup only
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

            if not numbers:
                frappe.throw("No WhatsApp recipients found for the selected role(s).")

            # Hand off to your existing Bulk WhatsApp Message
            bulk = frappe.new_doc("Bulk WhatsApp Message")
            bulk.recipients = numbers
            # Use the Notification’s message, not the reference document’s
            bulk.message = self.message
            bulk.insert(ignore_permissions=True)
            bulk.submit()
        else:
            # Fallback to all other channels (Email, SMS, Slack…)
            super(WhatsAppNotificationChannel, self).send(doc)
