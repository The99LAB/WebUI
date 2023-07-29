<template>
  <q-page padding>
    <div class="row q-mb-sm">
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
      no-data-label="No pools defined"
      :pagination="storageTablePagination"
    >
      <template v-slot:loading>
        <q-inner-loading showing color="primary" />
      </template>
      <template #body="props">
        <q-tr :props="props">
          <q-td
            key="name"
            :props="props"
            class="text-weight-regular text-body2"
          >
            <q-btn
              flat
              round
              :icon="props.row.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              @click="props.row.expand = !props.row.expand"
              size="md"
              padding="none"
            />
            {{ props.row.name }}
          </q-td>
          <q-td
            key="state"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.state }}
          </q-td>
          <q-td
            key="actions"
            :props="props"
            class="text-weight-regular text-body2"
          >
            <q-btn
              size="sm"
              flat
              round
              padding="xs"
              icon="mdi-delete"
              @click="deleteStoragePool(props.row.uuid)"
            >
              <q-tooltip :offset="[0, 5]"> Delete pool </q-tooltip>
            </q-btn>
            <q-btn
              size="sm"
              flat
              round
              padding="xs"
              icon="mdi-play"
              v-if="props.row.state != 'active'"
              @click="activateStoragePool(props.row.uuid)"
              ><q-tooltip :offset="[0, 5]"> Start pool </q-tooltip>
            </q-btn>
            <q-btn
              size="sm"
              flat
              round
              padding="xs"
              icon="mdi-stop"
              v-if="props.row.state == 'active'"
              @click="deactivateStoragePool(props.row.uuid)"
            >
              <q-tooltip :offset="[0, 5]"> Stop pool </q-tooltip>
            </q-btn>
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
          <q-td
            key="autostart"
            :props="props"
            class="text-weight-regular text-body2"
          >
            <q-toggle
              v-model="props.row.autostart"
              @update:model-value="toggleAutostartStoragePool(props.row.uuid)"
            />
          </q-td>
        </q-tr>
        <q-tr v-show="props.row.expand" :props="props">
          <q-td colspan="100%" no-hover>
            <div class="row">
              <q-tabs v-model="props.row.tab">
                <q-tab name="overview" label="Overview" />
                <q-tab name="volumes" label="Volumes" />
              </q-tabs>
            </div>
            <q-tab-panels v-model="props.row.tab">
              <q-tab-panel name="overview">
                <div class="row q-mb-sm">
                  <p class="text-body2 text-weight-bold q-mr-sm q-my-none">
                    Path:
                  </p>
                  <p class="text-body2 q-my-none">{{ props.row.path }}</p>
                </div>
                <div class="row q-mt-none">
                  <p
                    class="text-body2 text-weight-bold q-mr-sm q-my-none q-py-none"
                  >
                    Type:
                  </p>
                  <p class="text-body2 q-my-none q-py-none">
                    {{ props.row.type }}
                  </p>
                </div>
              </q-tab-panel>
              <q-tab-panel name="volumes" class="q-pb-none">
                <div class="row">
                  <q-space />
                  <q-btn
                    class="q-ma-sm"
                    color="primary"
                    icon="mdi-delete"
                    label="Remove"
                    :disable="
                      props.row.selectedVolume === undefined ||
                      props.row.selectedVolume.length == 0
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
                    selection="multiple"
                    v-model:selected="props.row.selectedVolume"
                    :pagination="volumeTablePagination"
                    hide-no-data
                    :loading="props.row.volumesLoading"
                  >
                    <template v-slot:loading>
                      <q-inner-loading showing color="primary" />
                    </template>
                  </q-table>
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
  { label: "Actions", field: "actions", name: "actions", align: "left" },
  { label: "Capacity", field: "capacity", name: "capacity", align: "left" },
  {
    label: "Allocation",
    field: "allocation",
    name: "allocation",
    align: "left",
  },
  { label: "Available", field: "available", name: "available", align: "left" },
  { label: "Autostart", field: "autostart", name: "autostart", align: "left" },
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
        descending: false,
      },
      storageTablePagination: {
        sortBy: "name",
        descending: false,
        rowsPerPage: 10,
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
      this.storageTableLoading = true;
      this.$api
        .get("/storage-pools")
        .then((response) => {
          let dataApi = response.data;
          let dataCurrent = this.rows;
          for (let i = 0; i < dataApi.length; i++) {
            // If the uuid is the same, then copy the expand property from the current data, and copy the tab property from the current data
            let index = _.findIndex(dataCurrent, { uuid: dataApi[i]["uuid"] });
            if (index != -1) {
              dataApi[i]["expand"] = dataCurrent[index]["expand"];
              dataApi[i]["tab"] = dataCurrent[index]["tab"];
            }
            // If the uuid is not the same, then insert the expand property to the data
            else {
              dataApi[i]["expand"] = false;
              dataApi[i]["tab"] = "overview";
            }
            dataApi[i]["selectedVolume"] = [];
            dataApi[i]["volumesLoading"] = false;
          }
          this.rows = dataApi;
          this.storageTableLoading = false;
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error getting storage pools.", [
            errormsg,
          ]);
        });
    },
    removeVolume(pooluuid, volume) {
      // Set volumesLoading to true for that pool
      let index = _.findIndex(this.rows, { uuid: pooluuid });
      this.rows[index]["volumesLoading"] = true;

      var volumeNames = [];
      for (let i = 0; i < volume.length; i++) {
        volumeNames.push(volume[i]["name"]);
      }

      this.$api
        .post("/storage-pools/" + pooluuid + "/delete-volumes", volumeNames)
        .then((response) => {
          this.getStoragePools();
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error removing volume.", [errormsg]);
        });
    },
    createVolume(pooluuid) {
      // Set volumesLoading to true for that pool
      let index = _.findIndex(this.rows, { uuid: pooluuid });
      this.rows[index]["volumesLoading"] = true;
      this.$refs.createVolumeDialog.show((pooluuid = pooluuid));
    },
    createStoragePool() {
      this.$refs.createStoragePoolDialog.show();
    },
    activateStoragePool(pooluuid) {
      this.$api
        .post("/storage-pools/" + pooluuid + "/start")
        .then((response) => {
          this.getStoragePools();
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error starting storage pool.", [
            errormsg,
          ]);
        });
    },
    deactivateStoragePool(pooluuid) {
      this.$api
        .post("/storage-pools/" + pooluuid + "/stop")
        .then((response) => {
          this.getStoragePools();
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error stopping storage pool.", [
            errormsg,
          ]);
        });
    },
    deleteStoragePool(pooluuid) {
      this.$api
        .post("/storage-pools/" + pooluuid + "/delete")
        .then((response) => {
          this.getStoragePools();
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error deleting storage pool.", [
            errormsg,
          ]);
        });
    },
    toggleAutostartStoragePool(pooluuid) {
      this.$api
        .post("/storage-pools/" + pooluuid + "/toggle-autostart")
        .then((response) => {
          this.getStoragePools();
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error toggling autostart.", [errormsg]);
        });
    },
  },
  mounted() {
    this.getStoragePools();
  },
  beforeUnmount() {
    clearInterval(this.storagePoolResultInterval);
  },
};
</script>
