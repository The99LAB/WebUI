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
        <StoragePoolAndVolumeList ref="storagePoolVolumeList" />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Select" @click="addDisk()" />
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
      path: null,
      disknumber: null,
      uuid: null,
    };
  },
  emits: ["sourcefile-add-finished"],
  components: {
    StoragePoolAndVolumeList,
    ErrorDialog,
  },
  methods: {
    show(disknumber, uuid) {
      this.disknumber = disknumber;
      this.uuid = uuid;
      this.alert = true;
    },
    addDisk() {
      this.path = this.$refs.storagePoolVolumeList.getSelectedVolumePath();
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-source-file", {
          number: this.disknumber,
          value: this.path,
        })
        .then((response) => {
          this.$emit("sourcefile-add-finished");
          this.alert = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error changing source file", [
            error.response.data.detail,
          ]);
        });
    },
  },
};
</script>
