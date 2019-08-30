import Vue from 'vue/dist/vue.js';

import SMSTemplateInfo from '../components/SMSTemplateInfo.vue';

function render_info(frm) {
  const { $wrapper } = frm.get_field('info_html');
  $wrapper.empty();
  const { content } = frm.doc;
  return new Vue({
    data: { content },
    el: $wrapper.html('<div />').children()[0],
    render: function(h) {
      return h(SMSTemplateInfo, { props: { content: this.content } });
    },
  });
}

export default {
  onload: function(frm) {
    frm.set_query('ref_doctype', function() {
      return { filters: { istable: 0, issingle: 0 } };
    });
  },
  refresh: function(frm) {
    frm.vue_info = render_info(frm);
  },
  content: function(frm) {
    frm.vue_info.content = frm.doc.content;
  },
};
