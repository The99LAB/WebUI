<template>
  <q-dialog v-model="visible">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add PCIe Device</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-card-section style="width: 30em">
        <HostPcieDevicesList ref="hostPcieDevicesList" />
        <q-toggle v-model="customRomFile" label="Custom ROM file" left-label />
        <!-- TODO: Use DirectoryList component here -->
        <q-input
          v-if="customRomFile"
          v-model="romFile"
          label="ROM file"
          :rules="[(val) => !!val || 'ROM file is required']"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Finish" @click="addPcieDevice()" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
</template>

<script>
import { ref } from "vue";
import HostPcieDevicesList from "src/components/HostPcieDevicesList.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      visible: ref(false),
      uuid: null,
      customRomFile: false,
      romFile: "",
    };
  },
  emits: ["pcie-device-add-finished"],
  components: {
    HostPcieDevicesList,
    ErrorDialog,
  },
  methods: {
    show(uuid) {
      this.uuid = uuid;
      this.visible = true;
    },
    addPcieDevice() {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-pcie-add", {
          domain:
            this.$refs.hostPcieDevicesList.getSelectedPciDevice()["domain"],
          bus: this.$refs.hostPcieDevicesList.getSelectedPciDevice()["bus"],
          slot: this.$refs.hostPcieDevicesList.getSelectedPciDevice()["slot"],
          function:
            this.$refs.hostPcieDevicesList.getSelectedPciDevice()["function"],
          customRomFile: this.customRomFile,
          romFile: this.romFile,
        })
        .then((response) => {
          this.$emit("pcie-device-add-finished");
          this.visible = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error", [
            "Failed to add PCIe device.",
            error.response.data.detail,
          ]);
        });
    },
  },
};
</script>
