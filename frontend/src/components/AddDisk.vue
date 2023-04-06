<template>
  <q-dialog v-model="alert">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add Disk</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none q-px-xl">
        <q-select
          v-model="diskType"
          :options="diskTypeOptions"
          label="Disk Type"
        />
        <StoragePoolAndVolumeList
          ref="storagePoolVolumeList"
          v-if="diskType == 'file'"
        />
        <q-select
          v-model="deviceType"
          :options="deviceTypeOptions"
          label="Device Type"
        />
        <q-select
          v-model="diskDriverType"
          :options="diskDriverTypeOptions"
          label="Driver Type"
        />
        <q-input
          v-model="sourceDevice"
          label="Source Device"
          v-if="diskType == 'block'"
        />
        <q-select
          v-model="diskBus"
          :options="diskBusOptions"
          label="Bus Format"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Finish" @click="addDisk()" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
</template>

<script>
import { ref } from "vue";
import StoragePoolAndVolumeList from "src/components/StoragePoolAndVolumeList.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      alert: ref(false),
      diskTypeOptions: ["file", "block"],
      diskType: "file",
      sourceDevice: "/dev/sda",
      pool: null,
      volumePath: null,
      deviceTypeOptions: ["disk", "cdrom"],
      deviceType: "disk",
      diskDriverTypeOptions: ["raw", "qcow2"],
      diskDriverType: "raw",
      diskBusOptions: ["sata", "scsi", "virtio", "usb"],
      diskBus: "sata",
      uuid: null,
    };
  },
  emits: ["disk-add-finished"],
  components: {
    StoragePoolAndVolumeList,
    ErrorDialog,
  },
  methods: {
    show(uuid) {
      (this.alert = true), (this.uuid = uuid);
      console.log("UUID: " + this.uuid);
    },
    addDisk() {
      this.volumePath = null;
      if (this.diskType == "file") {
        this.volumePath =
          this.$refs.storagePoolVolumeList.getSelectedVolumePath();
      }

      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-add", {
          volumePath: this.volumePath,
          deviceType: this.deviceType,
          diskDriverType: this.diskDriverType,
          diskBus: this.diskBus,
          sourceDevice: this.sourceDevice,
          diskType: this.diskType,
        })
        .then((response) => {
          this.$emit("disk-add-finished");
          this.alert = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error adding disk", [
            error.response.data.detail,
          ]);
        });
    },
  },
};
</script>
