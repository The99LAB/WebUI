<template>
  <q-page padding>
    <div class="row">
      <q-space />
      <q-btn
        class="q-ma-sm"
        color="primary"
        icon="mdi-plus"
        label="Create config"
        @click="openCreateConfigDialog"
      />
    </div>
    <q-table
      :loading="backupConfigTableLoading"
      :rows="backupConfigRows"
      :columns="backupConfigColumns"
      row-key="config"
      separator="none"
      no-data-label="Failed to get data from backend or no configs defined"
      hide-pagination
    >
      <template #body="props">
        <q-tr :props="props">
          <q-td key="config" :props="props">
            <q-btn
              flat
              round
              :icon="props.row.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              @click="props.row.expand = !props.row.expand"
              no-caps
              :label="props.row.config"
              class="text-weight-regular text-body2"
            />
          </q-td>
          <q-td
            key="lastResult"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.lastResult }}
          </q-td>
          <q-td
            key="backups"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.backupCount }}
          </q-td>
        </q-tr>

        <q-tr v-show="props.row.expand" :props="props">
          <q-td colspan="100%">
            <div class="row">
              <q-tabs v-model="props.row.tab">
                <q-tab name="overview" label="Overview" />
                <q-tab name="backups" label="Backups" />
              </q-tabs>
            </div>
            <q-tab-panels v-model="props.row.tab">
              <q-tab-panel name="overview">
                <div class="row q-ma-sm">
                  <q-btn
                    class="q-mr-sm"
                    color="primary"
                    icon="mdi-delete"
                    label="Delete config"
                    @click="deleteConfig(props.row.config)"
                  />
                  <q-btn
                    class="q-mr-sm"
                    color="primary"
                    icon="mdi-backup-restore"
                    label="Create backup"
                    @click="createBackup(props.row.config)"
                  />
                </div>

                <div class="row q-ma-sm">
                  <p class="text-body2 text-weight-bold q-mr-sm">
                    Destination:
                  </p>
                  <p class="text-body2">{{ props.row.destination }}</p>
                </div>
                <div class="row q-ma-sm">
                  <p class="text-body2 text-weight-bold q-mr-sm">
                    Auto shutdown:
                  </p>
                  <p class="text-body2">
                    {{ props.row.autoShutdown ? "Yes" : "No" }}
                  </p>
                </div>
                <div class="row q-ma-sm">
                  <p class="text-body2 text-weight-bold q-mr-sm">Disks:</p>
                  <p class="text-body2">
                    {{ props.row.disks.join(", ") }}
                  </p>
                </div>
              </q-tab-panel>
              <q-tab-panel name="backups">
                <div
                  class="row"
                  v-if="
                    props.row.selectedBackup !== undefined &&
                    props.row.selectedBackup.length
                  "
                >
                  <q-space />
                  <q-btn
                    class="q-ma-sm"
                    color="primary"
                    icon="mdi-restore"
                    label="Restore backup"
                    @click="
                      restoreBackup(props.row.config, props.row.selectedBackup)
                    "
                  />
                  <q-btn
                    class="q-ma-sm"
                    color="primary"
                    icon="mdi-delete"
                    label="Delete backup"
                    @click="
                      deleteBackup(props.row.config, props.row.selectedBackup)
                    "
                  />
                  <!-- show log -->
                  <q-btn
                    class="q-ma-sm"
                    color="primary"
                    icon="mdi-file"
                    label="Show log"
                    @click="
                      showBackupLog(props.row.config, props.row.selectedBackup)
                    "
                  />
                </div>
                <div class="q-pa-md">
                  <q-table
                    :rows="props.row.backups"
                    :columns="backupColumns"
                    row-key="name"
                    selection="single"
                    v-model:selected="props.row.selectedBackup"
                    hide-no-data
                    hide-bottom
                    hide-pagination
                  />
                </div>
              </q-tab-panel>
            </q-tab-panels>
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <q-dialog v-model="backupLogDialogShow">
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Backup log</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="lg" inset />
        <q-card-section class="q-pt-none" v-for="item in backupLog" :key="item">
          {{ item }}
        </q-card-section>
      </q-card>
    </q-dialog>
    <q-dialog v-model="createConfigDialogShow">
      <q-card style="min-width: 50vw">
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Create config</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="lg" inset />
        <q-card-section class="q-pt-none">
          <q-input v-model="createConfigName" type="text" label="Name" />
          <VmListAll
            ref="createConfigDialogVmList"
            @vm-selected="(selectedVm) => getDomainDisks(selectedVm['uuid'])"
          />
          <q-input
            v-model="createConfigDestination"
            type="text"
            label="Destination"
          />
          <!-- autoShutdown toggle -->
          <q-toggle v-model="createConfigAutoShutdown" label="Auto shutdown" />
          <!-- createConfigDisks q-select, can select multiple -->
          <q-select
            v-model="createConfigDisks"
            :options="createConfigDisksOptions"
            label="Disks"
            multiple
            filled
          />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Create" @click="createConfig()" />
        </q-card-actions>
      </q-card>
    </q-dialog>
    <ErrorDialog ref="errorDialog"></ErrorDialog>
  </q-page>
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import VmListAll from "src/components/VmListAll.vue";
import _ from "lodash";

const backupConfigRows = [];

const backupConfigColumns = [
  { label: "Config", field: "config", name: "config", align: "left" },
  {
    label: "Last result",
    field: "lastResult",
    name: "lastResult",
    align: "left",
  },
  { label: "Backups", field: "backups", name: "backups", align: "left" },
];

const backupColumns = [
  { label: "Name", field: "name", name: "name", align: "left" },
  { label: "Status", field: "status", name: "status", align: "left" },
  { label: "Size", field: "size", name: "size", align: "left" },
];

export default {
  data() {
    return {
      backupConfigRows,
      backupConfigColumns,
      backupColumns,
      backupConfigTableLoading: ref(true),
      backupLogDialogShow: ref(false),
      backupLog: ref(""),
      createConfigDialogShow: ref(false),
      createConfigName: ref("NewConfig"),
      createConfigDestination: ref("/path/to/backup/dir"),
      createConfigAutoShutdown: ref(false),
      createConfigDisksOptions: ref([]),
      createConfigDisks: ref([]),
    };
  },
  components: {
    ErrorDialog,
    VmListAll,
  },
  methods: {
    getData() {
      var array1 = this.backupConfigRows;
      var backupConfigNames1 = [];
      for (let i = 0; i < array1.length; i++) {
        backupConfigNames1.push(array1[i].config);
      }
      var array1SpecialData = [];
      for (let i = 0; i < array1.length; i++) {
        var expand = array1[i].expand;
        const config = array1[i].config;
        const lastResult = array1[i].lastResult;
        const backupCount = array1[i].backupCount;
        const destination = array1[i].destination;
        const autoShutdown = array1[i].autoShutdown;
        const disks = array1[i].disks;
        const backups = array1[i].backups;
        const tab = array1[i].tab;
        if (expand === undefined) {
          expand = false;
        }

        array1SpecialData.push({
          expand: expand,
          config: config,
          lastResult: lastResult,
          backupCount: backupCount,
          destination: destination,
          autoShutdown: autoShutdown,
          disks: disks,
          backups: backups,
          tab: tab,
        });
      }
      this.$api
        .get("/backup-manager/configs")
        .then((response) => {
          var array2 = response.data;
          if (array2.length === 0) {
            this.backupConfigRows = [];
            this.backupConfigTableLoading = false;
            return;
          }
          var backupConfigNames2 = [];
          for (let i = 0; i < array2.length; i++) {
            backupConfigNames2.push(array2[i].config);
          }
          // if array1 is empty, just use array2
          if (array1.length === 0) {
            for (let i = 0; i < array2.length; i++) {
              array2[i].tab = "overview";
            }
            this.backupConfigRows = array2;
            this.backupConfigTableLoading = false;
            return;
          }
          // merge arrays
          var combinedArray = _.merge(array1, array2);
          // remove deleted by comparing backupConfigNames1 and backupConfigNames2
          for (let i = 0; i < backupConfigNames1.length; i++) {
            if (!backupConfigNames2.includes(backupConfigNames1[i])) {
              combinedArray.splice(i, 1);
            }
          }

          // add expand and uuid to combined array
          for (let i = 0; i < combinedArray.length; i++) {
            // put expand and tab and expand varibles from array1SpecialData (client) into combinedArray (server)
            for (let j = 0; j < array1SpecialData.length; j++) {
              if (combinedArray[i].config === array1SpecialData[j].config) {
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
              if (combinedArray[i].config === array2[j].config) {
                combinedArray[i].backups = array2[j].backups;
              }
            }
          }
          // set rows
          this.backupConfigRows = combinedArray;
          this.backupConfigTableLoading = false;
        })
        .catch((error) => {
          if (error.response == undefined) {
            this.$refs.errorDialog.show("Error getting backup configs", [
              "Could not get backup configs.",
            ]);
          } else {
            this.$refs.errorDialog.show("Error getting backup configs", [
              "Could not get backup configs.",
              error.response.data.detail,
            ]);
          }
        });
    },
    createBackup(config) {
      this.$api
        .post("/backup-manager/config/" + config + "/create-backup")
        .catch((error) => {
          this.$refs.errorDialog.show("Error creating backup", [
            "Could not create backup.",
            error.response.data.detail,
          ]);
        });
    },
    deleteBackup(config, backup) {
      const backupname = backup[0]["name"];
      this.$api
        .post("/backup-manager/" + config + "/" + backupname + "/delete")
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting backup", [
            "Could not delete backup.",
            error.response.data.detail,
          ]);
        });
    },
    restoreBackup(config, backup) {
      const backupname = backup[0]["name"];
      this.$api
        .post("/backup-manager/" + config + "/" + backupname + "/restore")
        .catch((error) => {
          this.$refs.errorDialog.show("Error restoring backup", [
            "Could not restore backup.",
            error.response.data.detail,
          ]);
        });
    },
    deleteConfig(config) {
      this.$api
        .post("/backup-manager/config/" + config + "/delete")
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting config", [
            "Could not delete config.",
            error.response.data.detail,
          ]);
        });
    },
    showBackupLog(config, backup) {
      const backupname = backup[0]["name"];
      this.$api
        .post("/backup-manager/" + config + "/" + backupname + "/log")
        .then((response) => {
          this.backupLog = response.data;
          this.backupLogDialogShow = true;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting backup log", [
            "Could not get backup log.",
            error.response.data.detail,
          ]);
        });
    },
    createConfig() {
      const vm = this.$refs.createConfigDialogVmList.getSelectedVm()["name"];
      const destination = this.createConfigDestination;
      const autoShutdown = this.createConfigAutoShutdown;
      const disks = this.createConfigDisks.map((disk) => disk.value);
      console.log(destination);
      this.$api
        .post("/backup-manager/configs", {
          configName: this.createConfigName,
          vmName: vm,
          destination: destination,
          autoShutdown: autoShutdown,
          disks: disks,
        })
        .then((response) => {
          console.log(response.data);
          this.createConfigDialogShow = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error creating config", [
            "Could not create config.",
            error.response.data.detail,
          ]);
        });
    },
    openCreateConfigDialog() {
      this.createConfigDialogShow = true;
    },
    getDomainDisks(vmuuid) {
      this.$api
        .get("/vm-manager/" + vmuuid + "/disk-data")
        .then((response) => {
          if (response.data.length > 0) {
            this.createConfigDisks = [];
            this.createConfigDisksOptions = [];
            for (let i = 0; i < response.data.length; i++) {
              const disk = response.data[i];
              this.createConfigDisksOptions.push({
                label: disk["sourcefile"],
                value: disk["targetdev"],
              });
            }
          }
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting disks", [
            "Could not get disks.",
            error.response.data.detail,
          ]);
        });
    },
  },
  mounted() {
    this.getData();
    this.getDataInterval = setInterval(this.getData, 1000);
  },
  unmounted() {
    clearInterval(this.getDataInterval);
  },
};
</script>
