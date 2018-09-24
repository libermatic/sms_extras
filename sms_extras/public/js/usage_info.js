frappe.pages['usage-info'].on_page_show = async function(wrapper) {
  const { message: sms_usage } = await frappe.call({
    method: 'sms_extras.api.sms.get_usage',
  });
  if (sms_usage) {
    const ht = frappe.render_template('usage_info_add', sms_usage);
    $(wrapper)
      .find('.usage-info-section')
      .last()
      .after(ht);
  }
};
