<template>
  <q-select
    label="Storage pool"
    v-model="selectedStoragePool"
    :options="storagePoolList"
    option-label="name"
    @update:model-value="updateVolumesList()"
  >
    <template v-slot:option="scope">
      <q-item v-bind="scope.itemProps">
        <q-item-section>
          <q-item-label>{{ scope.opt.name }}</q-item-label>
          <q-item-label caption
            >{{ scope.opt.allocation }} / {{ scope.opt.capacity }}</q-item-label
          >
        </q-item-section>
      </q-item>
    </template>
  </q-select>
  <q-select
    label="Volume"
    v-model="selectedVolume"
    :options="volumesList"
    option-label="name"
  >
    <template v-slot:option="scope">
      <q-item v-bind="scope.itemProps">
        <q-item-section>
          <q-item-label>{{ scope.opt.name }}</q-item-label>
          <q-item-label caption
            >{{ scope.opt.allocation }} /
            {{ scope.opt.capacity }} GB</q-item-label
          >
        </q-item-section>
      </q-item>
    </template>
  </q-select>
</template>

<script>
export default {
  data() {
    return {
      storagePoolList: [],
      selectedStoragePool: "default",
      volumesList: [],
      selectedVolume: "default",
    };
  },
  methods: {
    updatePoolList() {
      this.$api
        .get("/storage-pools")
        .then((response) => {
          this.storagePoolList = response.data;
          this.selectedStoragePool = this.storagePoolList[0];
          this.updateVolumesList();
        })
        .catch((error) => {});
    },
    updateVolumesList() {
      this.$api
        .get("/storage-pools/" + this.selectedStoragePool["uuid"] + "/volumes")
        .then((response) => {
          this.volumesList = response.data;
          this.selectedVolume = this.volumesList[0];
        })
        .catch((error) => {});
    },
    getSelectedPool() {
      return this.selectedStoragePool["uuid"];
    },
    getSelectedVolume() {
      return this.selectedVolume["name"];
    },
    getSelectedVolumePath() {
      return this.selectedVolume["path"];
    },
  },
  mounted() {
    this.updatePoolList();
  },
};
</script>
