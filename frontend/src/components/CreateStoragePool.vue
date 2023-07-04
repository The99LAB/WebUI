<template>
  <q-dialog v-model="layout">
    <q-card>
      <q-card-section>
        <div class="row">
          <div class="text-h6">Create storage pool</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        <q-form>
          <div class="row">
            <div class="col">
              <q-input label="Name" v-model="poolName" />
            </div>
          </div>
          <div class="row">
            <div class="col">
              <q-select
                label="Type"
                v-model="poolType"
                :options="poolTypeOptions"
              />
            </div>
          </div>
          <div class="row">
            <div class="col">
              <q-input label="Path" v-model="poolPath" />
            </div>
          </div>
        </q-form>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Create" @click="createPool()" />
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
      poolName: ref("default"),
      poolType: ref("dir"),
      poolTypeOptions: ref(["dir"]),
      poolPath: ref("/var/lib/libvirt/images"),
      layout: ref(false),
    };
  },
  emits: ["storagepool-created"],
  components: {
    ErrorDialog,
  },
  methods: {
    show() {
      this.layout = true;
    },
    createPool() {
      console.log("Creating pool...");
      this.$api
        .post("/storage-pools", {
          name: this.poolName,
          type: this.poolType,
          path: this.poolPath,
        })
        .then((this.layout = false), this.$emit("storagepool-created"))
        .catch((error) => {
          this.$refs.errorDialog.show("Error creating pool", [
            error.response.data.detail,
          ]);
        });
    },
  },
};
</script>
