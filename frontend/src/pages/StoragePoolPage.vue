<template>
  <q-page padding>
    <div class="row">
      <q-space />
      <q-btn
        class="q-ma-sm"
        color="primary"
        icon="mdi-plus"
        label="Create storage pool"
        @click="createStoragePool()"
      />
    </div>
    <q-table
      :loading="storageTableLoading"
      :rows="rows"
      :columns="columns"
      row-key="uuid"
      separator="none"
      no-data-label="Failed to get data from backend or no pools defined"
      hide-pagination
    >
      <template #body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props">
            <q-btn
              flat
              round
              :icon="props.row.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              @click="props.row.expand = !props.row.expand"
              no-caps
              :label="props.row.name"
              class="text-weight-regular text-body2"
            />
          </q-td>
          <q-td
            key="state"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.state }}
          </q-td>
          <q-td
            key="capacity"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.capacity }}
          </q-td>
          <q-td
            key="allocation"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.allocation }}
          </q-td>
          <q-td
            key="available"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.available }}
          </q-td>
        </q-tr>

        <q-tr v-show="props.row.expand" :props="props">
          <q-td colspan="100%">
            <div class="row">
              <q-tabs v-model="props.row.tab">
                <q-tab name="overview" label="Overview" />
                <q-tab name="volumes" label="Volumes" />
              </q-tabs>
            </div>
            <q-tab-panels v-model="props.row.tab">
              <q-tab-panel name="overview">
                <div class="row q-ma-sm">
                  <q-btn
                    class="q-mr-sm"
                    color="primary"
                    icon="mdi-delete"
                    label="Delete"
                    @click="deleteStoragePool(props.row.uuid)"
                  />
                  <q-btn
                    class="q-mr-sm"
                    color="primary"
                    icon="mdi-play"
                    label="Activate"
                    v-if="props.row.state != 'active'"
                    @click="activateStoragePool(props.row.uuid)"
                  />
                  <q-btn
                    class="q-mr-sm"
                    color="primary"
                    icon="mdi-stop"
                    label="Deactivate"
                    v-if="props.row.state == 'active'"
                    @click="deactivateStoragePool(props.row.uuid)"
                  />
                  <q-btn
                    class="q-mr-sm"
                    color="primary"
                    :icon="props.row.autostart ? 'mdi-stop' : 'mdi-play'"
                    :label="
                      props.row.autostart
                        ? 'Disable autostart'
                        : 'Enable autostart'
                    "
                    @click="toggleAutostartStoragePool(props.row.uuid)"
                  />
                </div>
                <div class="row q-ma-sm">
                  <p class="text-body2 text-weight-bold q-mr-sm">Path:</p>
                  <p class="text-body2">{{ props.row.path }}</p>
                </div>
                <div class="row q-ma-sm">
                  <p class="text-body2 text-weight-bold q-mr-sm">Autostart:</p>
                  <p class="text-body2" v-if="props.row.autostart">Yes</p>
                  <p class="text-body2" v-else>No</p>
                </div>
                <div class="row q-ma-sm">
                  <p class="text-body2 text-weight-bold q-mr-sm">Type:</p>
                  <p class="text-body2">{{ props.row.type }}</p>
                </div>
              </q-tab-panel>
              <q-tab-panel name="volumes">
                <div class="row">
                  <q-space />
                  <q-btn
                    class="q-ma-sm"
                    color="primary"
                    icon="mdi-delete"
                    label="Remove"
                    v-if="
                      props.row.selectedVolume !== undefined &&
                      props.row.selectedVolume.length
                    "
                    @click="
                      removeVolume(props.row.uuid, props.row.selectedVolume)
                    "
                  />
                  <q-btn
                    class="q-ma-sm"
                    color="primary"
                    icon="mdi-plus"
                    label="Create volume"
                    @click="createVolume((pooluuid = props.row.uuid))"
                  />
                </div>
                <div class="q-pa-md">
                  <q-table
                    :rows="props.row.volumes"
                    :columns="volumeColums"
                    row-key="name"
                    selection="single"
                    v-model:selected="props.row.selectedVolume"
                    hide-no-data
                    hide-bottom
                    hide-pagination
                    :pagination="volumeTablePagination"
                  />
                </div>
              </q-tab-panel>
            </q-tab-panels>
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <ErrorDialog ref="errorDialog"></ErrorDialog>
    <CreateVolume
      ref="createVolumeDialog"
      @volume-created="getStoragePools"
    ></CreateVolume>
    <createStoragePool
      ref="createStoragePoolDialog"
      @storagepool-created="getStoragePools"
    ></createStoragePool>
  </q-page>
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import CreateVolume from "src/components/CreateVolume.vue";
import createStoragePool from "src/components/CreateStoragePool.vue";
import _ from "lodash";

const selected = ref();

const rows = [];

const columns = [
  { label: "Name", field: "name", name: "name", align: "left" },
  { label: "State", field: "state", name: "state", align: "left" },
  { label: "Capacity", field: "capacity", name: "capacity", align: "left" },
  {
    label: "Allocation",
    field: "allocation",
    name: "allocation",
    align: "left",
  },
  { label: "Available", field: "available", name: "available", align: "left" },
];

const volumeColums = [
  { label: "Name", field: "name", name: "name", align: "left" },
  { label: "Size", field: "size", name: "size", align: "left" },
];

export default {
  data() {
    return {
      rows,
      columns,
      volumeColums,
      selected,
      storageTableLoading: ref(true),
      volumeTablePagination: {
        sortBy: "name",
        rowsPerPage: 0,
      },
    };
  },
  components: {
    ErrorDialog,
    CreateVolume,
    createStoragePool,
  },
  methods: {
    getStoragePools() {
      var array1 = this.rows;
      var storagePoolNames1 = [];
      for (let i = 0; i < array1.length; i++) {
        storagePoolNames1.push(array1[i].name);
      }
      var array1SpecialData = [];
      for (let i = 0; i < array1.length; i++) {
        var expand = array1[i].expand;
        const uuid = array1[i].uuid;
        const tab = array1[i].tab;
        const volumes = array1[i].volumes;
        if (expand === undefined) {
          expand = false;
        }

        array1SpecialData.push({
          uuid: uuid,
          expand: expand,
          tab: tab,
          volumes: volumes,
        });
      }
      // get data from server
      this.$api
        .get("/storage-pools")
        .then((response) => {
          var array2 = response.data;
          if (array2.length === 0) {
            this.rows = [];
            this.storageTableLoading = false;
            return;
          }
          var storagePoolNames2 = [];
          for (let i = 0; i < array2.length; i++) {
            storagePoolNames2.push(array2[i].name);
          }
          // if array1 is empty, just use array2
          if (array1.length === 0) {
            for (let i = 0; i < array2.length; i++) {
              array2[i].tab = "overview";
            }
            this.rows = array2;
            return;
          }
          // merge arrays
          var combinedArray = _.merge(array1, array2);
          // remove deleted by comparing storagePoolNames1 and storagePoolNames2
          for (let i = 0; i < storagePoolNames1.length; i++) {
            if (!storagePoolNames2.includes(storagePoolNames1[i])) {
              combinedArray.splice(i, 1);
            }
          }

          // add expand and uuid to combined array
          for (let i = 0; i < combinedArray.length; i++) {
            // put expand and tab and expand varibles from array1SpecialData (client) into combinedArray (server)
            for (let j = 0; j < array1SpecialData.length; j++) {
              if (combinedArray[i].uuid === array1SpecialData[j].uuid) {
                combinedArray[i].expand = array1SpecialData[j].expand;
                combinedArray[i].tab = array1SpecialData[j].tab;
              }
            }
            // make sure tab isn't undefined
            if (combinedArray[i].tab === undefined) {
              combinedArray[i].tab = "overview";
            }
            // put volumes from array2 (server) into combinedArray (client)
            for (let j = 0; j < array2.length; j++) {
              if (combinedArray[i].uuid === array2[j].uuid) {
                combinedArray[i].volumes = array2[j].volumes;
              }
            }
          }
          // set rows
          this.rows = combinedArray;
          this.storageTableLoading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting storage pools.", [error]);
        });
    },
    removeVolume(pooluuid, volume) {
      //console.log("pooluuid:", pooluuid)
      //console.log("volume:", volume)
      const volumeName = volume[0]["name"];
      //console.log(volume[0]["name"])
      this.$api
        .delete("/storage-pools/" + pooluuid + "/volume/" + volumeName)
        .then((response) => {
          //console.log("storagepools:", response.data)
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error.response.data);
        });
    },
    createVolume(pooluuid) {
      this.$refs.createVolumeDialog.show((pooluuid = pooluuid));
    },
    createStoragePool() {
      this.$refs.createStoragePoolDialog.show();
    },
    activateStoragePool(pooluuid) {
      this.$api
        .post("/storage-pools/" + pooluuid + "/start")
        .then((response) => {})
        .catch((error) => {
          this.$refs.errorDialog.show(error.response.data);
        });
    },
    deactivateStoragePool(pooluuid) {
      this.$api
        .post("/storage-pools/" + pooluuid + "/stop")
        .then((response) => {})
        .catch((error) => {
          this.$refs.errorDialog.show(error.response.data);
        });
    },
    deleteStoragePool(pooluuid) {
      this.$api
        .post("/storage-pools/" + pooluuid + "/delete")
        .then((response) => {})
        .catch((error) => {
          this.$refs.errorDialog.show(error.response.data);
        });
    },
    toggleAutostartStoragePool(pooluuid) {
      this.$api
        .post("/storage-pools/" + pooluuid + "/toggle-autostart")
        .then((response) => {})
        .catch((error) => {
          this.$refs.errorDialog.show(error.response.data);
        });
    },
  },
  mounted() {
    this.getStoragePools();
    this.storagePoolResultInterval = setInterval(() => {
      this.getStoragePools();
    }, 1000);
  },
  beforeUnmount() {
    clearInterval(this.storagePoolResultInterval);
  },
};
</script>
