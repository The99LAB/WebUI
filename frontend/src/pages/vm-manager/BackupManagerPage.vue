<template>
  <q-page padding>
    <q-table
      title="Backups"
      :loading="backupConfigTableLoading"
      :rows="backupConfigRows"
      :columns="backupConfigColumns"
      row-key="config"
      separator="none"
      no-data-label="No configs defined"
      :pagination="backupConfigTablePagination"
    >
      <template v-slot:top-right>
        <q-btn flat color="primary" round icon="mdi-refresh" @click="getData">
          <q-tooltip :offset="[5, 5]"> Refresh Backups </q-tooltip>
        </q-btn>
        <q-btn
          flat
          color="primary"
          round
          icon="mdi-plus"
          @click="openCreateConfigDialog"
        >
          <q-tooltip :offset="[5, 5]"> Create new backup config </q-tooltip>
        </q-btn>
      </template>
      <template v-slot:loading>
        <q-inner-loading showing />
      </template>
      <template v-slot:body="props">
        <q-tr :props="props">
          <q-td
            key="config"
            :props="props"
            @click="props.row.expand = !props.row.expand"
            class="text-weight-regular text-body2"
            style="cursor: pointer; user-select: none"
          >
            <q-icon
              :name="props.row.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              size="sm"
            />
            {{ props.row.config }}
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

        <q-tr v-show="props.row.expand" :props="props" no-hover>
          <q-td colspan="100%">
            <div class="row">
              <q-tabs v-model="props.row.tab">
                <q-tab name="overview" label="Overview" />
                <q-tab name="backups" label="Backups" />
              </q-tabs>
            </div>
            <q-tab-panels v-model="props.row.tab">
              <q-tab-panel name="overview">
                <div class="row q-mt-sm">
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
                <div class="row q-my-xs">
                  <span class="text-body2 text-weight-bold q-mr-sm">
                    Destination:
                  </span>
                  <span class="text-body2">{{ props.row.destination }}</span>
                </div>
                <div class="row q-my-xs">
                  <span class="text-body2 text-weight-bold q-mr-sm">
                    Auto shutdown:
                  </span>
                  <span class="text-body2">
                    {{ props.row.autoShutdown ? "Yes" : "No" }}
                  </span>
                </div>
                <div class="row q-mt-xs">
                  <span class="text-body2 text-weight-bold q-mr-sm"
                    >Disks:</span
                  >
                  <span class="text-body2">{{
                    props.row.disks.join(", ")
                  }}</span>
                </div>
              </q-tab-panel>
              <q-tab-panel name="backups">
                <q-table
                  :rows="props.row.backups"
                  :columns="backupColumns"
                  row-key="name"
                  selection="single"
                  v-model:selected="props.row.selectedBackup"
                  hide-no-data
                  hide-bottom
                  hide-pagination
                >
                  <template v-slot:top-right>
                    <q-btn
                      color="primary"
                      icon="mdi-backup-restore"
                      round
                      flat
                      :disable="props.row.selectedBackup.length == 0"
                      @click="
                        restoreBackup(
                          props.row.config,
                          props.row.selectedBackup,
                        )
                      "
                    >
                      <q-tooltip :offset="[5, 5]"> Restore backup </q-tooltip>
                    </q-btn>
                    <q-btn
                      color="primary"
                      icon="mdi-delete"
                      round
                      flat
                      :disable="props.row.selectedBackup.length == 0"
                      @click="
                        deleteBackup(props.row.config, props.row.selectedBackup)
                      "
                    >
                      <q-tooltip :offset="[5, 5]"> Delete backup </q-tooltip>
                    </q-btn>
                    <q-btn
                      color="primary"
                      icon="mdi-file-document-outline"
                      round
                      flat
                      :disable="props.row.selectedBackup.length == 0"
                      @click="
                        showBackupLog(
                          props.row.config,
                          props.row.selectedBackup,
                        )
                      "
                    >
                      <q-tooltip :offset="[5, 5]"> Show backup log </q-tooltip>
                    </q-btn>
                  </template>
                </q-table>
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
        <q-card-section v-for="item in backupLog" :key="item">
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
        <q-card-section>
          <q-form @submit="createConfig">
            <q-input
              v-model="createConfigName"
              type="text"
              label="Config Name"
              :rules="[
                (val) => !!val || 'Cannot be empty',
                (val) => !val.includes(' ') || 'Cannot contain spaces',
              ]"
            />
            <VmListAll
              ref="createConfigDialogVmList"
              @vm-selected="(selectedVm) => getDomainDisks(selectedVm['uuid'])"
            />
            <DirectoryList
              v-model="createConfigDestination"
              selectiontype="dir"
              label="Destination"
            >
              <template v-slot:append>
                <q-icon name="mdi-help-circle-outline">
                  <q-tooltip :offset="[5, 5]">
                    The directory where the backups will be stored.
                    <br />
                    Every Virtual Machine needs its own directory.
                  </q-tooltip>
                </q-icon>
              </template>
            </DirectoryList>
            <q-select
              class="q-my-md"
              v-model="createConfigDisks"
              :options="createConfigDisksOptions"
              label="Disks"
              multiple
              filled
              :rules="[(val) => !!val || 'Cannot be empty']"
            >
              <template v-slot:append>
                <q-icon name="mdi-help-circle-outline">
                  <q-tooltip :offset="[5, 5]">
                    The VM Disks that you want to backup.
                  </q-tooltip>
                </q-icon>
              </template>
            </q-select>
            <div class="row">
              <q-toggle
                v-model="createConfigAutoShutdown"
                label="Auto shutdown"
              >
                <q-tooltip :offset="[5, 5]">
                  If the vm is running, it will be shutdown before the backup
                  starts.
                </q-tooltip>
              </q-toggle>
              <q-space />
              <q-btn flat label="Create" type="submit" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
      <q-inner-loading :visible="createConfigLoading" />
    </q-dialog>
    <ErrorDialog ref="errorDialog" />
  </q-page>
</template>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";
import VmListAll from "src/components/VmListAll.vue";
import DirectoryList from "src/components/DirectoryList.vue";

export default {
  data() {
    return {
      backupConfigRows: [],
      backupConfigColumns: [
        { label: "Config", field: "config", name: "config", align: "left" },
        {
          label: "Last result",
          field: "lastResult",
          name: "lastResult",
          align: "left",
        },
        { label: "Backups", field: "backups", name: "backups", align: "left" },
      ],
      backupColumns: [
        { label: "Name", field: "name", name: "name", align: "left" },
        { label: "Status", field: "status", name: "status", align: "left" },
        { label: "Size", field: "size", name: "size", align: "left" },
      ],
      backupConfigTableLoading: true,
      backupConfigTablePagination: {
        rowsPerPage: 15,
        sortBy: "config",
        descending: false,
      },
      backupLogDialogShow: false,
      backupLog: "",
      createConfigDialogShow: false,
      createConfigLoading: false,
      createConfigName: "NewConfig",
      createConfigDestination: null,
      createConfigAutoShutdown: false,
      createConfigDisksOptions: [],
      createConfigDisks: [],
    };
  },
  components: {
    ErrorDialog,
    VmListAll,
    DirectoryList,
  },
  methods: {
    getData() {
      this.backupConfigTableLoading = true;
      this.$api
        .get("/backup-manager/configs")
        .then((response) => {
          this.backupConfigRows = response.data;
          for (let i = 0; i < this.backupConfigRows.length; i++) {
            this.backupConfigRows[i]["expand"] = false;
            this.backupConfigRows[i]["tab"] = "overview";
            this.backupConfigRows[i]["selectedBackup"] = [];
          }
          this.backupConfigTableLoading = false;
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error getting backup configs", [
            errormsg,
          ]);
        });
    },
    createBackup(config) {
      this.$api
        .post("/backup-manager/config/" + config + "/create-backup")
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error creating backup", [errormsg]);
        });
    },
    deleteBackup(config, backup) {
      const backupname = backup[0]["name"];
      this.$api
        .post("/backup-manager/" + config + "/" + backupname + "/delete")
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error deleting backup", [errormsg]);
        });
    },
    restoreBackup(config, backup) {
      const backupname = backup[0]["name"];
      this.$api
        .post("/backup-manager/" + config + "/" + backupname + "/restore")
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error restoring backup", [errormsg]);
        });
    },
    deleteConfig(config) {
      this.$api
        .post("/backup-manager/config/" + config + "/delete")
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error deleting config", [errormsg]);
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
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error getting backup log", [errormsg]);
        });
    },
    createConfig() {
      this.createConfigLoading = true;
      const vm = this.$refs.createConfigDialogVmList.getSelectedVm()["name"];
      const destination = this.createConfigDestination;
      const autoShutdown = this.createConfigAutoShutdown;
      const disks = this.createConfigDisks.map((disk) => disk.value);
      this.$api
        .post("/backup-manager/configs", {
          configName: this.createConfigName,
          vmName: vm,
          destination: destination,
          autoShutdown: autoShutdown,
          disks: disks,
        })
        .then((response) => {
          this.createConfigDialogShow = false;
          this.createConfigLoading = false;
          this.getData();
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error creating config", [errormsg]);
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
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error getting disks", [errormsg]);
        });
    },
  },
  mounted() {
    this.getData();
  },
  unmounted() {
    clearInterval(this.getDataInterval);
  },
};
</script>
