<template>
  <q-dialog v-model="layout">
    <q-card>
      <q-card-section>
        <div class="row">
          <div class="text-h6">Create volume</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </div>
      </q-card-section>

      <q-card-section class="q-pt-none">
        <q-form>
          <div class="row">
            <div class="col">
              <q-input label="Name" v-model="volumeName" />
            </div>
          </div>
          <div class="row">
            <div class="col">
              <q-select
                label="Pool"
                v-if="showPoolSelection"
                v-model="selectedPool"
                :options="poolOptions"
              />
            </div>
          </div>
          <div class="row">
            <div class="col">
              <q-input
                label="Size"
                v-model="volumeSize"
                type="number"
                min="1"
              />
            </div>
            <div class="col-md-auto">
              <q-select
                v-model="volumeSizeUnit"
                :options="volumeSizeUnitOptions"
              />
            </div>
          </div>
          <div class="row">
            <div class="col">
              <q-select
                label="Format"
                v-model="volumeFormat"
                :options="volumeFormatOptions"
              />
            </div>
          </div>
        </q-form>
      </q-card-section>

      <q-card-actions align="right">
        <q-btn flat label="Create" @click="createVolume()" />
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
      pooluuid: ref(null),
      volumeName: ref("Volume"),
      volumeFormat: ref("raw"),
      volumeFormatOptions: ref(["raw", "qcow2"]),
      volumeSize: ref(1),
      volumeSizeUnit: ref("GB"),
      volumeSizeUnitOptions: ref(["MB", "GB", "TB"]),
      layout: ref(false),
    };
  },
  emits: ["volume-created"],
  components: {
    ErrorDialog,
  },
  methods: {
    show(pooluuid = null) {
      if (pooluuid == null) {
        this.showPoolSelection = true;
      } else {
        this.showPoolSelection = false;
        this.pooluuid = pooluuid;
      }
      this.layout = true;
    },
    createVolume() {
      this.$api
        .post("/storage-pools/" + this.pooluuid + "/create-volume", {
          name: this.volumeName,
          format: this.volumeFormat,
          size: this.volumeSize,
          size_unit: this.volumeSizeUnit,
        })
        .then((response) => {
          this.layout = false;
          this.$emit("volume-created");
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error creating volume", [
            error.response.data.detail,
          ]);
        });
    },
  },
};
</script>
