<template>
  <q-dialog v-model="alert" full-width full-height>
    <q-card full-height>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">VM Logs</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-card-section class="q-pt-sm">
        <q-input filled v-model="content" type="textarea" autogrow />
      </q-card-section>
    </q-card>
  </q-dialog>
</template>

<script>
export default {
  data() {
    return {
      alert: false,
      content: "",
    };
  },
  methods: {
    show(content) {
      this.content = content;
      this.alert = true;
    },
  },
};
</script>
