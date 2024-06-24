<template>
  <q-dialog v-model="layout">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add video</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none">
        <q-select
          v-model="videoType"
          :options="videoTypeOptions"
          label="Video model"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Add" @click="addVideo" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "/src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      layout: ref(false),
      videoTypeOptions: ["QXL", "VGA", "Virtio"],
      videoType: "Virtio",
      vmuuid: "",
    };
  },
  components: {
    ErrorDialog,
  },
  emits: ["video-add-finished"],
  methods: {
    show(vmuuid) {
      this.vmuuid = vmuuid;
      this.layout = true;
    },
    addVideo() {
      this.$api
        .post("/vm-manager/" + this.vmuuid + "/edit-video-add", {
          type: this.videoType,
        })
        .then((response) => {
          this.$emit("video-add-finished");
          this.layout = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error adding video", [
            error.response.data.detail,
          ]);
        });
    },
  },
};
</script>
