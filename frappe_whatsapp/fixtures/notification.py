from frappe.core.doctype.notification.notification import Notification
import frappe

class WhatsAppNotificationChannel(Notification):
    def send(self, doc):
        if doc.channel == "Whatsapp Message":
            # Hand off to existing Bulk WhatsApp Message doctype
            bulk = frappe.new_doc("Bulk WhatsApp Message")
            bulk.recipients = [r.strip() for r in doc.recipients.split(",")]
            bulk.message = doc.message
            bulk.insert(ignore_permissions=True)
            bulk.submit()
        else:
            super(WhatsAppNotificationChannel, self).send(doc)
