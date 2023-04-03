<template>
  <q-dialog v-model="visible">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add Sound Device</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none q-px-xl">
        <q-select
          v-model="selectedSoundDeviceModel"
          :options="soundDevicesModel"
          label="Sound Device"
          filled
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Finish" @click="addSoundDevice()" />
      </q-card-actions>
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
      uuid: null,
      selectedSoundDeviceModel: { label: "AC97", value: "ac97" },
      soundDevicesModel: [
        { label: "AC97", value: "ac97" },
        { label: "ICH6", value: "ich6" },
        { label: "ICH9", value: "ich9" },
      ],
    };
  },
  emits: ["sound-add-finished"],
  components: {
    ErrorDialog,
  },
  methods: {
    show(uuid) {
      this.uuid = uuid;
      if (this.selectedSoundDeviceModel == null) {
        this.selectedSoundDeviceModel = this.soundDevicesModel[0].value;
      }
      this.visible = true;
    },
    addSoundDevice() {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-sound-add", {
          model: this.selectedSoundDeviceModel.value,
        })
        .then((response) => {
          this.$emit("sound-add-finished");
          this.visible = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error", [
            "Failed to add sound device.",
            error.response.data,
          ]);
        });
    },
  },
};
</script>
