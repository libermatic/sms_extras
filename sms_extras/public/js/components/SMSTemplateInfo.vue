<template>
  <div class="root">
    <dl>
      <dt>Est char count</dt>
      <dd>{{ get_formatted(messageLength) }}</dd>
    </dl>
    <dl>
      <dt>No of Messages</dt>
      <dd>{{ get_formatted(noOfMessages) }}</dd>
    </dl>
  </div>
</template>

<script>
import trim from 'lodash/trim';
import flatten from 'lodash/flatten';

export default {
  props: {
    content: { type: String, default: '' },
  },
  computed: {
    messageLength: function() {
      return this.content.length;
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
.root {
  margin-top: 1em;
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
