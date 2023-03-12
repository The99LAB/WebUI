<template>
  <q-page padding>
    <!-- <div class="row">
      <q-space />
      <q-btn
        class="q-ma-sm"
        color="primary"
        icon="mdi-plus"
        label="Create config"
      />
    </div> -->
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
              </q-tab-panel>
              <q-tab-panel name="backups">
                <div class="row" v-if="
                      props.row.selectedBackup !== undefined &&
                      props.row.selectedBackup.length
                    ">
                  <q-space />
                    <q-btn
                        class="q-ma-sm"
                        color="primary"
                        icon="mdi-restore"
                        label="Restore backup"
                        @click="restoreBackup(props.row.config, props.row.selectedBackup)"
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
                  <q-btn class="q-ma-sm" color="primary" icon="mdi-file" label="Show log" @click="showBackupLog(props.row.config, props.row.selectedBackup)"/>
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
            <q-separator spaced="lg" inset />
            <q-card-section class="q-pt-none" v-for="item in backupLog" :key="item">
                {{ item }}
            </q-card-section>
        </q-card>
    </q-dialog>
    <ErrorDialog ref="errorDialog"></ErrorDialog>
  </q-page>
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

const backupConfigRows = [];

const backupConfigColumns = [
  { label: "Config", field: "config", name: "config", align: "left" },
  { label: "Backups", field: "backups", name: "backups", align: "left" },
];

const backupColumns = [
  { label: "Name", field: "name", name: "name", align: "left" },
  { label: "Size", field: "size", name: "size", align: "left" }
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
    };
  },
  components: {
    ErrorDialog,
  },
  methods: {
    getData(){
        this.$api
            .get("/backup-manager/configs")
            .then((response) => {
                this.backupConfigRows = response.data;
                console.log(response.data)
                this.backupConfigTableLoading = false;
            })
            .catch((error) => {
                this.$refs.errorDialog.show("Error getting backup configs", [
                    "Could not get backup configs.",
                    error.response.data,
                ]);
            });

    },
    createBackup(config){
        this.$api.post("/backup-manager/config/" + config + "/create-backup")
            .then((response) => {
                console.log(response.data)
            })
            .catch((error) => {
                this.$refs.errorDialog.show("Error creating backup", [
                    "Could not create backup.",
                    error.response.data,
                ]);
            }
        );
    },
    deleteBackup(config, backup){
        const backupname = backup[0]['name']
        this.$api.post("/backup-manager/" + config + "/" + backupname + "/delete")
            .then((response) => {
                console.log(response.data)
            })
            .catch((error) => {
                this.$refs.errorDialog.show("Error deleting backup", [
                    "Could not delete backup.",
                    error.response.data,
                ]);
            }
        );
    },
    restoreBackup(config, backup){
        const backupname = backup[0]['name']
        this.$api.post("/backup-manager/" + config + "/" + backupname + "/restore")
            .then((response) => {
                console.log(response.data)
            })
            .catch((error) => {
                this.$refs.errorDialog.show("Error restoring backup", [
                    "Could not restore backup.",
                    error.response.data,
                ]);
            }
        );
    },
    deleteConfig(config){
        this.$api.post("/backup-manager/config/" + config + "/delete")
            .then((response) => {
                console.log("response", response.data)
            })
            .catch((error) => {
                this.$refs.errorDialog.show("Error deleting config", [
                    "Could not delete config.",
                    error.response.data,
                ]);
            }
        );
    },
    showBackupLog(config, backup){
        const backupname = backup[0]['name']

        this.$api.post("/backup-manager/" + config + "/" + backupname + "/log")
            .then((response) => {
                this.backupLog = response.data
                this.backupLogDialogShow = true
            })
            .catch((error) => {
                this.$refs.errorDialog.show("Error getting backup log", [
                    "Could not get backup log.",
                    error.response.data,
                ]);
            }
        );
    },
  },
  mounted() {
    this.getData();
  },
};
</script>
