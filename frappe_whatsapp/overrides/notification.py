# frappe_whatsapp/overrides/notification.py

from frappe.email.doctype.notification.notification import Notification
import frappe

class WhatsAppNotificationChannel(Notification):
    def send(self, doc):
        if doc.channel == "Whatsapp Message":
            numbers = []

            for row in doc.recipients:
                # 1) Skip any row with a false condition
                if row.condition:
                    if not frappe.safe_eval(row.condition, None, {"doc": doc}):
                        continue

                # 2) Role‐based recipients
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

                # (We skip receiver_by_document_field here since it’s blank)

            if not numbers:
                frappe.throw("No WhatsApp recipients found for the selected role(s).")

            # 3) Hand off to your existing Bulk doctype
            bulk = frappe.new_doc("Bulk WhatsApp Message")
            bulk.recipients = numbers
            bulk.message = doc.message
            bulk.insert(ignore_permissions=True)
            bulk.submit()

        else:
            super(WhatsAppNotificationChannel, self).send(doc)
