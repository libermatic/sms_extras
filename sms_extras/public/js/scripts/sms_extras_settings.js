export default {
  show_balance: function(frm) {
    if (!frm.doc.show_balance) {
      [
        'sms_balance_url',
        'sms_balance_method',
        'sms_balance_payload',
        'response_content_type',
        'response_field',
      ].forEach(field => frm.set_value(field, null));
    }
  },
};
