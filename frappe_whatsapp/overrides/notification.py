# File: frappe_whatsapp/overrides/notification.py

from frappe.email.doctype.notification.notification import Notification
import frappe

class WhatsAppNotificationChannel(Notification):
    def send(self, doc):
        if self.channel == "Whatsapp Message":
            numbers = []

            # 1) Gather mobile numbers from the Recipients child‐table
            for row in self.recipients:
                if row.condition and not frappe.safe_eval(row.condition, None, {"doc": doc}):
                    continue

                if row.receiver_by_role:
                    # Fetch all users in that role
                    has_role = frappe.get_all(
                        "Has Role",
                        filters={"role": row.receiver_by_role},
                        fields=["parent"]
                    )
                    user_names = [r.parent for r in has_role]
                    if user_names:
                        users = frappe.get_all(
                            "User",
                            filters={"name": ["in", user_names], "enabled": 1},
                            fields=["mobile_no"]
                        )
                        for u in users:
                            if u.mobile_no:
                                numbers.append(u.mobile_no)

            if not numbers:
                frappe.throw("No WhatsApp recipients found for the selected role(s).")

            # 2) Build the Bulk WhatsApp Message doc
            bulk = frappe.new_doc("Bulk WhatsApp Message")

            # **Use the Notification’s subject as the title**
            bulk.title = self.subject or f"WA via Notification {self.name}"

            # (Optional) If your Bulk doctype requires a reference, uncomment:
            # bulk.reference_doctype = self.reference_doctype
            # bulk.reference_name = self.reference_name

            # 3) Append each number as its own child row
            for num in numbers:
                bulk.append("recipients", {
                    "mobile_number": num
                })

            # 4) Copy the Notification’s message body
            bulk.message = self.message

            # 5) Insert & submit to trigger your existing bulk‐send logic
            bulk.insert(ignore_permissions=True)
            bulk.submit()
        else:
            super(WhatsAppNotificationChannel, self).send(doc)
