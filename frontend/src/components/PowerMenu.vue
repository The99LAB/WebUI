<template>
  <q-dialog v-model="visible">
    <q-card>
      <q-card-section class="row items-center">
        <div class="text-h6">Power menu</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-card-section class="row">
        <q-space />
        <q-btn color="primary" label="Shutdown" icon="mdi-power" @click="shutdown()" />
        <q-space />
      </q-card-section>
      <q-card-section class="row">
        <q-space />
        <q-btn color="primary" icon="mdi-refresh" label="Reboot" @click="reboot()" />
        <q-space />
      </q-card-section>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      visible: ref(false),
    };
  },
  components: {
    ErrorDialog,
  },
  methods: {
    show() {
      this.visible = true;
    },
    shutdown() {
      this.$api.post("host/power/shutdown").catch((error) => {
        this.$refs.errorDialog.show("Shutdown error", [
          error,
          error.response.data.detail,
        ]);
      });
    },
    reboot() {
      this.$api.post("host/power/reboot").catch((error) => {
        this.$refs.errorDialog.show("Reboot error", [
          error,
          error.response.data.detail,
        ]);
      });
    },
  },
};
</script>
