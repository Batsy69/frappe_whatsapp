# File: frappe_whatsapp/overrides/notification.py

from frappe.email.doctype.notification.notification import Notification
import frappe

class WhatsAppNotificationChannel(Notification):
    def send(self, doc):
        # `self` is the Notification record, `doc` is the referenced document
        if self.channel == "Whatsapp Message":
            numbers = []

            # 1) Pull mobile numbers from each Recipients child‐row by role
            for row in self.recipients:
                # Optional condition filter
                if row.condition:
                    if not frappe.safe_eval(row.condition, None, {"doc": doc}):
                        continue

                if row.receiver_by_role:
                    # Find all users who have this role
                    has_role = frappe.get_all(
                        "Has Role",
                        filters={"role": row.receiver_by_role},
                        fields=["parent"]
                    )
                    user_names = [r.parent for r in has_role]
                    if user_names:
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

            if not numbers:
                frappe.throw("No WhatsApp recipients found for the selected role(s).")

            # 2) Build the Bulk WhatsApp Message doc correctly
            bulk = frappe.new_doc("Bulk WhatsApp Message")
            # Clear any default rows, then append one child record per number
            for num in numbers:
                bulk.append("recipients", {
                    "mobile_number": num,
                    # You can also set recipient_name or recipient_data here if needed
                    # "recipient_name": "",
                    # "recipient_data": "{}",
                })

            # 3) Copy the message from the Notification
            bulk.message = self.message

            # 4) Insert & submit to fire your existing bulk‐send logic
            bulk.insert(ignore_permissions=True)
            bulk.submit()
        else:
            # All other channels (Email, SMS, Slack, etc.)
            super(WhatsAppNotificationChannel, self).send(doc)
