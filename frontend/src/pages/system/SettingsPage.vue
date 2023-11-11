<template>
  <q-page padding>
    <q-table
      title="Settings"
      :rows="settings"
      :columns="settings_columns"
      selection="single"
      row-key="name"
      v-model:selected="selected_setting"
      :pagination="table_pagination"
      hide-pagination
      :loading="settings_loading"
      hide-bottom
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          flat
          round
          icon="mdi-pencil"
          :disable="selected_setting.length == 0"
          @click="editSettingDialogShow = true"
        >
          <q-tooltip :offset="[5, 5]"> Edit Setting </q-tooltip>
        </q-btn>
      </template>
      <template v-slot:loading>
        <q-inner-loading showing />
      </template>
    </q-table>
    <q-separator color="transparent" spaced="xl" />
    <q-table
      title="OVMF Paths"
      :rows="ovmf_paths"
      :columns="ovmf_paths_columns"
      selection="single"
      row-key="name"
      v-model:selected="selected_ovmf_path"
      :pagination="table_pagination"
      hide-pagination
      :loading="ovmf_paths_loading"
      hide-bottom
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          round
          flat
          icon="mdi-pencil"
          :disable="selected_ovmf_path.length == 0"
          @click="editOvmfPathDialogShow = true"
        >
          <q-tooltip :offset="[5, 5]"> Edit OVMF Path </q-tooltip>
        </q-btn>
        <q-btn
          color="primary"
          round
          flat
          icon="mdi-delete"
          :disable="selected_ovmf_path.length == 0"
          @click="$refs.confirmDialog.show(
            'Are you sure?',
            ['Are you sure you want to remove this OVMF path?'],
            () => { removeOvmfPath() }
          )"
        >
          <q-tooltip :offset="[5, 5]"> Remove OVMF Path </q-tooltip>
        </q-btn>
        <q-btn
          color="primary"
          round
          flat
          icon="mdi-plus"
          @click="addOvmfPathDialogShow = true"
        >
          <q-tooltip :offset="[5, 5]"> Add OVMF Path </q-tooltip>
        </q-btn>
      </template>
      <template v-slot:loading>
        <q-inner-loading showing />
      </template>
    </q-table>
  </q-page>
  <q-dialog v-model="editSettingDialogShow">
    <q-card style="min-width: 50vw">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Edit Setting</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-card-section>
        <q-form @submit="editSetting" class="q-gutter-md">
          <div v-if="selected_setting[0].verifyDir || selected_setting[0].verifyFile">
            <DirectoryList
              v-model="selected_setting[0].value"
              :label="selected_setting[0].name"
              :selectiontype="selected_setting[0].verifyDir ? 'dir' : 'file'"
              :startpath="selected_setting[0].value"
            />
            <div v-if="selected_setting[0].value == null" class="q-mt-sm row items-center">
              <q-icon name="mdi-alert" color="red" />
              <span class="text-red q-ml-xs ">Path is required</span>
            </div>
            <div class="row justify-end">
              <q-btn label="Submit" type="submit" flat :disable="selected_setting[0].value == null"/>
            </div>
          </div>
          <div v-else>
            <q-input
              v-model="selected_setting[0].value"
              type="text"
              :label="selected_setting[0].name"
              :rules="selected_setting[0].rules"
            >
              <template v-slot:counter>
                  {{ selected_setting[0].description }}
              </template>
            </q-input>
            <div class="row justify-end">
              <q-btn label="Submit" type="submit" flat />
            </div>
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
  <q-dialog v-model="editOvmfPathDialogShow">
    <q-card style="min-width: 50vw">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Edit OVMF Path</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-card-section class="q-pt-sm">
        <q-input
          v-model="selected_ovmf_path[0].path"
          type="text"
          :label="selected_ovmf_path[0].name"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
          flat
          label="Edit"
          @click="editOvmfPath"
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
      <q-card-section>
        <q-form
          @submit="addOvmfPath"
          class="q-gutter-md"
        >
          <q-input
            v-model="addOvmfPathDialogName"
            type="text"
            label="Name"
            :rules="[
              (val) => val.length > 0 || 'Name is required',
              (val) => !val.includes(' ') || 'No spaces allowed',
            ]"
          />
          <DirectoryList
            v-model="addOvmfPathDialogPath"
            label="Path"
            selectiontype="file"
            startpath="/usr/share/OVMF"
          />
          <div v-if="addOvmfPathDialogPath == null" class="q-mt-sm row items-center">
          <q-icon name="mdi-alert" color="red" />
          <span class="text-red q-ml-xs ">Path is required</span>
        </div>
          <div class="row justify-end">
            <q-btn label="Submit" type="submit" flat :disable="addOvmfPathDialogPath == null"/>
          </div>
        </q-form>
      </q-card-section>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
  <ConfirmDialog ref="confirmDialog" />
</template>
<script>
import { isReactive, ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";
import DirectoryList from "src/components/DirectoryList.vue";

export default {
  data() {
    return {
      ovmf_paths: [],
      ovmf_paths_columns:  [
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "path",
          label: "Path",
          field: "path",
          align: "left",
          sortable: true,
        },
      ],
      settings: [],
      settings_columns: [
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "value",
          label: "Value",
          field: "value",
          align: "left",
          sortable: true,
        },
        {
          name: "description",
          label: "Description",
          field: "description",
          align: "left",
          sortable: true,
        }
      ],
      selected_setting: [],
      selected_ovmf_path: [],
      editSettingDialogShow: false,
      editOvmfPathDialogShow: false,
      addOvmfPathDialogShow: false,
      addOvmfPathDialogName: "OVMF_name",
      addOvmfPathDialogPath: "/path/to/ovmf",
      table_pagination: {
        sortBy: "name",
        rowsPerPage: 0,
      },
      settings_loading: true,
      ovmf_paths_loading: true,
    };
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
    DirectoryList,
  },
  methods: {
    getData() {
      this.$api
        .get("/settings")
        .then((response) => {
          this.settings = response.data;
          this.settings.forEach((item) => {
            this.generateRegexRules(item);
          });
          console.log(this.settings);
          this.settings_loading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting settings", [
            error.response.data.detail,
          ]);
        });
      this.$api
        .get("/settings/ovmf-paths")
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
      this.$api
        .put("/setting/" + this.selected_setting[0].name, {
          value: this.selected_setting[0].value,
        })
        .then((response) => {
          this.getData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing setting", [
            error.response.data.detail,
          ]);
        });
    },

    editOvmfPath() {
      this.$api
        .put("/settings/ovmf-paths/" + this.selected_ovmf_path[0].name, {
          path: this.selected_ovmf_path[0].path,
        })
        .then((response) => {
          this.getData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing OVMF path", [
            error.response.data.detail,
          ]);
        });
    },

    removeOvmfPath() {
      this.$api
        .delete("/settings/ovmf-paths/" + this.selected_ovmf_path[0].name)
        .then((response) => {
          this.getData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error removing OVMF path", [
            error.response.data.detail,
          ]);
        });
    },

    addOvmfPath() {
      this.$api
        .post("/settings/ovmf-paths/" + this.addOvmfPathDialogName, {
          path: this.addOvmfPathDialogPath,
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
    generateRegexRules(item) {
      if (item.regexrules == []){
        item.rules = [
          (val) => val.length > 0 || 'Value is required',
        ]
      }
      else {
        item.rules = item.regexrules.map((rule) => {
          rule.regex = new RegExp(rule.regex);
          return (val) => rule.regex.test(val) || rule.description;
        });
      }
    },
  },
  mounted() {
    this.getData();
  },
};
</script>
