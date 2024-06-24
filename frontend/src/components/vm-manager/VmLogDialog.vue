<template>
  <q-dialog v-model="visible" full-width full-height :maximized="$q.screen.lt.md">
    <q-layout
      view="hHh lpR fFf"
      container
      :class="{ 'bg-dark': $q.dark.isActive, 'bg-white': !$q.dark.isActive }"
    >
      <q-header bordered>
        <q-toolbar>
          <q-toolbar-title>VM Logs</q-toolbar-title>
          <q-btn icon="close" flat round dense v-close-popup />
        </q-toolbar>
      </q-header>
      <q-page-container>
        <q-page class="fit row items-center justify-center">
          <q-card class="q-pa-md" style="width: 100%">
            <q-card-section>
              <q-input filled v-model="content" type="textarea" autogrow readonly />
            </q-card-section>
          </q-card>
        </q-page>
      </q-page-container>
    </q-layout>
    <q-inner-loading :showing="loading" />
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
</template>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      visible: false,
      loading: false,
      vm_uuid: "",
      content: "",
    };
  },
  components: {
    ErrorDialog,
  },
  methods: {
    show(vm_uuid) {
      this.visible = true;
      this.loading = true;
      this.vm_uuid = vm_uuid;
      this.$api.get("/vm-manager/" + this.vm_uuid + "/log")
        .then((response) => {
          this.content = response.data;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error while loading vm log", error);
        })
        .finally(() => {
          this.loading = false;
        });
    },
  },
};
</script>
