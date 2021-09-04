import Vue from 'vue/dist/vue.js';

import SMSPortalDashboard from '../components/SMSPortalDashboard.vue';

async function request_sms(frm) {
  try {
    await frappe.call({ method: 'request_sms', doc: frm.doc });
  } finally {
    frm.refresh();
  }
}

function render_dashboard(frm) {
  frm.dashboard.show();
  const $wrapper = $('<div />');
  frm.dashboard.add_section($wrapper);

  const { recipients, message } = frm.doc;
  return new Vue({
    data: { recipients, message },
    el: $wrapper[0],
    render: function (h) {
      return h(SMSPortalDashboard, {
        props: { recipients: this.recipients, message: this.message },
      });
    },
  });
}

export default {
  onload: function (frm) {
    frm.set_query('template', () => ({
      filters: { type: 'Manual', disabled: 0 },
    }));
  },
  refresh: function (frm) {
    console.log('refresh');
    frm.disable_save();
    frm.page.clear_icons();
    frm.page.set_primary_action(__('Send SMS'), () => request_sms(frm));
    frm.vue_sms_portal_dashboard = render_dashboard(frm);
  },
  recipient_list: async function (frm) {
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
  recipients: function (frm) {
    frm.vue_sms_portal_dashboard.recipients = frm.doc.recipients;
  },
  message: function (frm) {
    frm.vue_sms_portal_dashboard.message = frm.doc.message;
  },
};
