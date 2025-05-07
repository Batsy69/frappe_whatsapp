frappe.ui.form.on("Notification", {
  refresh(frm) {
    const isWA = frm.doc.channel === "Whatsapp Message";
    frm.toggle_reqd("recipients", isWA);
    if (isWA) {
      frm.set_intro(
        "Enter comma-separated WhatsApp numbers (with country code), e.g. 919812345678."
      );
    } else {
      frm.clear_intro();
    }
  }
});
