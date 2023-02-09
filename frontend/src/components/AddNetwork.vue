<template>
  <q-dialog v-model="alert">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add Network</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator spaced="lg" inset />
      <q-card-section class="q-pt-none q-px-xl">
        <NetworkList ref="networkList" />
        <q-select
          v-model="networkModel"
          :options="networkModelOptions"
          label="Model"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Finish" @click="addNetwork()" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
</template>

<script>
import { ref } from "vue";
import NetworkList from "src/components/NetworkList.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      alert: ref(false),
      sourceNetwork: null,
      networkModelOptions: ["virtio", "e1000", "rtl8139"],
      networkModel: ref("virtio"),
      uuid: null,
    };
  },
  emits: ["network-add-finished"],
  components: {
    ErrorDialog,
    NetworkList,
  },
  methods: {
    show(uuid) {
      (this.alert = true), (this.uuid = uuid);
      console.log("UUID: " + this.uuid);
    },
    addNetwork() {
      this.sourceNetwork = this.$refs.networkList.getSelectedNetwork();
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-network-add", {
          sourceNetwork: this.sourceNetwork,
          networkModel: this.networkModel,
        })
        .then((response) => {
          this.$emit("network-add-finished");
          this.alert = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error adding disk", [
            error.response.data,
          ]);
        });
    },
  },
};
</script>
