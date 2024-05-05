<template>
  <q-dialog v-model="layout">
    <q-card>
      <q-card-section>
        <div class="row">
          <div class="text-h6">Edit Host Name</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        <q-form>
          <div class="row">
            <div class="col">
              <q-input label="Name" v-model="hostName" />
            </div>
          </div>
        </q-form>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Finish" @click="editHostName()" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <errorDialog ref="errorDialog" />
</template>

<script>
import { ref } from "vue";
import errorDialog from "src/components/ErrorDialog.vue";
import { useHostnameStore } from "stores/hostname";
import { storeToRefs } from "pinia";

export default {
  data() {
    return {
      hostName: "",
      layout: ref(false),
    };
  },
  setup() {
    const hostname_store = useHostnameStore();
    return { hostname_store };
  },
  components: {
    errorDialog,
  },
  emits: ["hostname-edit-finished"],
  methods: {
    show() {
      this.layout = true;
      this.getHostName();
    },
    getHostName() {
      this.hostName = this.hostname_store.hostname;
    },
    editHostName() {
      this.$api
        .post("/host/system-info/hostname", { hostname: this.hostName })
        .then((response) => {
          this.hostname_store.getHostnameApi();
          this.layout = false;
          this.$emit("hostname-edit-finished");
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing hostname", [
            error.response.data.detail,
          ]);
        });
    },
  },
  mounted() {},
};
</script>
