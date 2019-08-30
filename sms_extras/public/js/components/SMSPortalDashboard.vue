<template>
  <loading-indicator v-if="isLoading" />
  <div v-else>
    <div class="detail-row">
      <dl>
        <dt>Balance</dt>
        <dd>{{ get_formatted(balance) }}</dd>
      </dl>
      <dl>
        <dt>Sent this month</dt>
        <dd>{{ get_formatted(sent) }}</dd>
      </dl>
    </div>
    <div class="detail-row">
      <dl>
        <dt>Est char count</dt>
        <dd>{{ get_formatted(messageLength) }}</dd>
      </dl>
      <dl>
        <dt>No of Messages</dt>
        <dd>{{ get_formatted(noOfMessages) }}</dd>
      </dl>
      <dl>
        <dt>No of Recipients</dt>
        <dd>{{ get_formatted(recipientLength) }}</dd>
      </dl>
      <dl>
        <dt>Est Total SMS</dt>
        <dd>{{ get_formatted(noOfMessages * recipientLength) }}</dd>
      </dl>
    </div>
  </div>
</template>

<script>
import trim from 'lodash/trim';
import flatten from 'lodash/flatten';

import LoadingIndicator from './LoadingIndicator.vue';

export default {
  components: { LoadingIndicator },
  props: {
    recipients: { type: String, default: '' },
    message: { type: String, default: '' },
  },
  data: function() {
    return { isLoading: true, balance: 0, sent: 0 };
  },
  computed: {
    messageLength: function() {
      return this.message.length;
    },
    recipientLength: function() {
      return flatten(this.recipients.split('\n').map(x => x.split(',')))
        .map(trim)
        .filter(x => x).length;
    },
    noOfMessages: function() {
      if (this.messageLength < 161) {
        return 1;
      }
      if (this.messageLength < 307) {
        return 2;
      }
      return Math.ceil(this.messageLength / 153);
    },
  },
  mounted: async function() {
    try {
      const {
        message: { sms_balance = 0, sms_sent = 0 } = {},
      } = await frappe.call({
        method: 'sms_extras.api.sms.get_usage',
      });
      this.balance = sms_balance;
      this.sent = sms_sent;
    } finally {
      this.isLoading = false;
    }
  },
  methods: {
    get_formatted: function(value) {
      if (typeof value === 'number') {
        return value.toLocaleString();
      }
      return value;
    },
  },
};
</script>

<style lang="scss" scoped>
.detail-row {
  display: flex;
  justify-content: space-around;
  dl {
    width: 100%;
    padding: 0.5em 1em;
    text-align: center;
  }
  dt {
    font-weight: normal;
    font-size: 0.8em;
    color: #8d99a6;
    text-transform: uppercase;
  }
  dd {
    font-weight: bold;
    font-size: 1.2em;
  }
}
</style>
