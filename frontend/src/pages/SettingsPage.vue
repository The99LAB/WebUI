<template>
  <q-page padding>
    <p class="text-h6">Settings</p>
    <p class="text-subtitle2">General settings</p>
    <div class="row">
      <q-space />
      <q-btn
        color="primary"
        label="Edit"
        icon="mdi-pencil"
        :disable="selected_setting.length == 0"
        @click="editSetting"
      />
    </div>
    <div class="q-pa-md">
      <q-table
        :rows="settings"
        :columns="settings_columns"
        selection="single"
        row-key="name"
        v-model:selected="selected_setting"
        :pagination="table_pagination"
        hide-pagination
        :loading="settings_loading"
      />
    </div>
    <q-separator color="transparent" spaced="xl" />
    <p class="text-subtitle2">OVMF Paths</p>
    <div class="row">
      <q-space />
      <q-btn
        color="primary"
        label="Edit"
        icon="mdi-pencil"
        :disable="selected_ovmf_path.length == 0"
        @click="editOvmfPath"
      />
      <q-separator color="transparent" spaced vertical dark />
      <q-btn
        color="primary"
        label="Remove"
        icon="mdi-delete"
        :disable="selected_ovmf_path.length == 0"
        @click="removeOvmfPath(selected_ovmf_path[0].name)"
      />
      <q-separator color="transparent" spaced vertical dark />
      <q-btn
        color="primary"
        label="Add"
        icon="mdi-plus"
        @click="addOvmfPathDialogShow = true"
      />
    </div>
    <div class="q-pa-md">
      <q-table
        :rows="ovmf_paths"
        :columns="ovmf_paths_columns"
        selection="single"
        row-key="name"
        v-model:selected="selected_ovmf_path"
        :pagination="table_pagination"
        hide-pagination
        :loading="ovmf_paths_loading"
      />
    </div>
  </q-page>
  <q-dialog v-model="editSettingDialogShow">
    <q-card style="min-width: 50vw">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Edit setting</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none">
        <p>Target: {{ this.editSettingDialogTarget }}</p>
        <q-input
          v-model="editSettingDialogValue"
          type="text"
          :label="this.editSettingDialogName"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          flat
          label="Edit"
          @click="
            editSettingDialogSave(
              this.editSettingDialogTarget,
              this.editSettingDialogName,
              this.editSettingDialogValue,
            )
          "
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <q-dialog v-model="addOvmfPathDialogShow">
    <q-card style="min-width: 50vw">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add OVMF path</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none">
        <q-input
          v-model="addOvmfPathDialogName"
          type="text"
          label="Name"
          :rules="[(val) => val.length > 0 || 'Name is required']"
        />
        <q-input
          v-model="addOvmfPathDialogPath"
          type="text"
          label="Path"
          :rules="[(val) => val.length > 0 || 'Path is required']"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          flat
          label="Add"
          @click="
            addOvmfPath(this.addOvmfPathDialogName, this.addOvmfPathDialogPath);
            addOvmfPathDialogShow = false;
          "
        />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
</template>
<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
const ovmf_paths_columns = [
  {
    name: "name",
    label: "name",
    field: "name",
    align: "left",
    sortable: true,
  },
  {
    name: "path",
    label: "path",
    field: "path",
    align: "left",
    sortable: true,
  },
];

const settings_columns = [
  {
    name: "name",
    label: "name",
    field: "name",
    align: "left",
    sortable: true,
  },
  {
    name: "value",
    label: "value",
    field: "value",
    align: "left",
    sortable: true,
  },
];

export default {
  data() {
    return {
      novnc_path: ref(null),
      novnc_port: ref(null),
      novnc_protocool: ref(null),
      qemu_path: ref(null),
      protocool_options: ["http", "https"],
      ovmf_paths: ref([]),
      ovmf_paths_columns,
      settings: ref([]),
      settings_columns,
      selected_setting: ref([]),
      selected_ovmf_path: ref([]),
      editSettingDialogShow: ref(false),
      editSettingDialogValue: ref(null),
      editSettingDialogName: ref(null),
      editSettingDialogTarget: ref(null),
      addOvmfPathDialogShow: ref(false),
      addOvmfPathDialogName: ref("OVMF name"),
      addOvmfPathDialogPath: ref("/path/to/ovmf"),
      table_pagination: {
        sortBy: "name",
        rowsPerPage: 0,
      },
      settings_loading: ref(true),
      ovmf_paths_loading: ref(true),
    };
  },
  components: {
    ErrorDialog,
  },
  methods: {
    getData() {
      this.$api
        .get("/host/settings/all")
        .then((response) => {
          this.settings = response.data;
          this.settings_loading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting settings", [
            error.response.data.detail,
          ]);
        });
      this.$api
        .get("/vm-manager/settings/ovmf-paths/all")
        .then((response) => {
          this.ovmf_paths = response.data;
          this.ovmf_paths_loading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting OVMF paths", [
            error.response.data.detail,
          ]);
        });
    },
    editSetting() {
      const name = this.selected_setting[0].name;
      const value = this.selected_setting[0].value;
      this.showEditSettingDialog("general", name, value);
    },

    editOvmfPath() {
      const name = this.selected_ovmf_path[0].name;
      const value = this.selected_ovmf_path[0].path;
      this.showEditSettingDialog("ovmf paths", name, value);
    },

    showEditSettingDialog(target, name, value) {
      this.editSettingDialogTarget = target;
      this.editSettingDialogName = name;
      this.editSettingDialogValue = value;
      this.editSettingDialogShow = true;
    },

    changeSetting(setting, value) {
      this.$api
        .post("/host/settings/edit", {
          setting: setting,
          value: value,
        })
        .then((response) => {
          this.getData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error changing setting", [
            error.response.data.detail,
          ]);
        });
    },

    changeOvmfPath(name, value) {
      this.$api
        .post("/vm-manager/settings/ovmf-paths/edit", {
          name: name,
          path: value,
        })
        .then((response) => {
          this.getData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error changing OVMF path", [
            error.response.data.detail,
          ]);
        });
    },

    removeOvmfPath(name) {
      this.$api
        .post("/vm-manager/settings/ovmf-paths/delete", {
          name: name,
        })
        .then((response) => {
          this.getData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting OVMF path", [
            error.response.data.detail,
          ]);
        });
    },

    addOvmfPath(name, path) {
      this.$api
        .post("/vm-manager/settings/ovmf-paths/add", {
          name: name,
          path: path,
        })
        .then((response) => {
          this.getData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error adding OVMF path", [
            error.response.data.detail,
          ]);
        });
    },

    editSettingDialogSave(target, name, value) {
      if (target == "general") {
        this.changeSetting(name, value);
      } else if (target == "ovmf paths") {
        this.changeOvmfPath(name, value);
      }
      this.editSettingDialogShow = false;
    },
  },
  mounted() {
    this.getData();
  },
};
</script>
