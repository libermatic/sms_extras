frappe.pages['usage-info'].on_page_show = async function(wrapper) {
  const section = $(wrapper).find('.layout-main-section');
  $(wrapper)
    .find('.sms_extra-sms-section')
    .remove();
  const { message: sms_usage } = await frappe.call({
    method: 'sms_extras.api.sms.get_usage',
    freeze: true,
  });
  if (sms_usage) {
    $(frappe.render_template('usage_info_add', sms_usage)).appendTo(section);
  }
};
