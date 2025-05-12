# File: frappe_whatsapp/overrides/notification.py

from frappe.email.doctype.notification.notification import Notification
import frappe

class WhatsAppNotificationChannel(Notification):
    def send(self, doc):
        # `self` is the Notification record; `doc` is the referenced document
        if self.channel == "Whatsapp Message":
            numbers = []

            # 1) Collect all mobile numbers from the Recipients child‐table by role
            for row in self.recipients:
                # a) Skip by condition if provided
                if row.condition:
                    if not frappe.safe_eval(row.condition, None, {"doc": doc}):
                        continue

                # b) Only handle role-based recipients
                if row.receiver_by_role:
                    # fetch all User names with that role
                    has_role = frappe.get_all(
                        "Has Role",
                        filters={"role": row.receiver_by_role},
                        fields=["parent"]
                    )
                    user_names = [r.parent for r in has_role]

                    if user_names:
                        # fetch only enabled Users from that list
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

            # 2) Guard against an empty recipient list
            if not numbers:
                frappe.throw("No WhatsApp recipients found for the selected role(s).")

            # 3) Build the Bulk WhatsApp Message doc
            bulk = frappe.new_doc("Bulk WhatsApp Message")

            # Use the Notification’s own name (prompt‐entered) as the Bulk title
            bulk.title = self.name

            # (Optional) If Bulk requires reference fields, uncomment:
            # bulk.reference_doctype = self.reference_doctype
            # bulk.reference_name = self.reference_name

            # 4) Append each number as its own child row
            for num in numbers:
                bulk.append("recipients", {
                    "mobile_number": num
                })

            # 5) Copy the Notification’s message body
            bulk.message = self.message

            # 6) Insert & submit to fire your existing bulk‐send logic
            bulk.insert(ignore_permissions=True)
            bulk.submit()

        else:
            # Fallback to the standard Notification behavior for other channels
            super(WhatsAppNotificationChannel, self).send(doc)
