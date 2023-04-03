<template>
  <q-dialog v-model="layout">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add graphics</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none">
        <q-select
          v-model="graphicsType"
          :options="graphicsTypeOptions"
          label="Graphics type"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Add" @click="addGraphics" />
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
      graphicsTypeOptions: ["vnc", "spice"],
      graphicsType: "vnc",
      vmuuid: "",
    };
  },
  components: {
    ErrorDialog,
  },
  emits: ["graphics-add-finished"],
  methods: {
    show(vmuuid) {
      this.vmuuid = vmuuid;
      this.layout = true;
    },
    addGraphics() {
      this.$api
        .post("/vm-manager/" + this.vmuuid + "/edit-graphics-add", {
          type: this.graphicsType,
        })
        .then((response) => {
          this.$emit("graphics-add-finished");
          this.layout = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error adding graphics", [
            error.response.data,
          ]);
        });
    },
  },
};
</script>
