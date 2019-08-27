async function request_sms(frm) {
  try {
    await frappe.call({ method: 'request_sms', doc: frm.doc });
  } finally {
    frm.refresh();
  }
}

export default {
  onload: function(frm) {
    frm.set_query('template', () => ({
      filters: { type: 'Promotional', disabled: 0 },
    }));
  },
  refresh: function(frm) {
    frm.disable_save();
    frm.page.clear_icons();
    frm.page.set_primary_action(__('Send SMS'), () => request_sms(frm));
  },
  recipient_list: async function(frm) {
    const { recipient_list } = frm.doc;
    if (recipient_list) {
      const { message: recipients } = await frappe.call({
        method: 'sms_extras.api.sms.get_numbers_from_list',
        args: { recipient_list },
      });
      frm.set_value('recipients', recipients.join('\n'));
    } else {
      frm.set_value('recipients', null);
    }
  },
};
