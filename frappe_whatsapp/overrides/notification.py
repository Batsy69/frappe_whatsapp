# File: frappe_whatsapp/overrides/notification.py

from frappe.email.doctype.notification.notification import Notification
import frappe

class WhatsAppNotificationChannel(Notification):
    def send(self, doc):
        # `self` is the Notification record
        if self.channel == "Whatsapp Message":
            numbers = []

            # 1) Loop over Notification Recipient rows
            for row in self.recipients:
                # a) Skip by condition if present
                if row.condition:
                    if not frappe.safe_eval(row.condition, None, {"doc": doc}):
                        continue

                # b) Only handle role-based rows
                if row.receiver_by_role:
                    # 2) Get all User names with that role
                    has_role = frappe.get_all(
                        "Has Role",
                        filters={"role": row.receiver_by_role},
                        fields=["parent"]
                    )
                    user_names = [r.parent for r in has_role]

                    if user_names:
                        # 3) Now fetch only enabled Users from that list
                        users = frappe.get_all(
                            "User",
                            filters={
                                "name": ["in", user_names],
                                "enabled": 1
                            },
                            fields=["mobile_no"]
                        )
                        for u in users:
                            if u.mobile_no:
                                numbers.append(u.mobile_no)

            # 4) Guard against sending to nobody
            if not numbers:
                frappe.throw("No WhatsApp recipients found for the selected role(s).")

            # 5) Hand off to Bulk WhatsApp Message
            bulk = frappe.new_doc("Bulk WhatsApp Message")
            bulk.recipients = numbers
            bulk.message = self.message
            bulk.insert(ignore_permissions=True)
            bulk.submit()

        else:
            # fallback for Email/SMS/other channels
            super(WhatsAppNotificationChannel, self).send(doc)

