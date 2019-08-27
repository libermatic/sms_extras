async function request_sms(frm) {
  await frappe.call({
    method: 'request_sms',
    doc: frm.doc,
  });
  frm.refresh();
}

export default {
  refresh: function(frm) {
    frm.disable_save();
    frm.page.clear_icons();
    frm.page.set_primary_action(__('Send SMS'), request_sms(frm));
  },
};
