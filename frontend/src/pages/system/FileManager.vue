<template>
  <q-page padding>
    <q-table
      :rows="paths"
      :columns="columns"
      row-key="name"
      :pagination="tablePagination"
      selection="multiple"
      v-model:selected="selected"
      :loading="tableLoading"
      hide-pagination
      hide-selected-banner
    >
      <template v-slot:top-right>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-form-textbox"
          :disable="selected.length == 0 || selected.length > 1"
          @click="
            renameDialogItem = JSON.parse(JSON.stringify(selected[0]));
            renameDialog = true;
          "
        >
          <q-tooltip :offset="[0, 5]"> Rename </q-tooltip>
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-folder-plus-outline"
          @click="folderDialog = true"
        >
          <q-tooltip :offset="[0, 5]"> Add Folder </q-tooltip>
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-delete-outline"
          :disable="selected.length == 0"
          @click="
            this.$refs.confirmDialog.show(
              'Are you sure?',
              [
                'Do you really want to remove this?',
                'This action is not reversable!',
              ],
              removePath,
            )
          "
        >
          <q-tooltip :offset="[0, 5]"> Remove </q-tooltip>
        </q-btn>
      </template>
      <template v-slot:top-left>
        <div v-for="(item, index) in currentPath.split('/')" :key="index">
          <div
            v-if="index == 0"
            class="row items-center"
            style="cursor: pointer"
            @click="getPath('/')"
          >
            root
          </div>
          <div
            v-else-if="item != ''"
            class="row items-center"
            style="cursor: pointer"
            @click="
              getPath(
                currentPath
                  .split('/')
                  .slice(0, index + 1)
                  .join('/'),
              )
            "
          >
            <q-icon name="mdi-chevron-right" size="sm" />
            {{ item }}
          </div>
        </div>
      </template>
      <template v-slot:loading>
        <q-inner-loading showing />
      </template>
      <template v-slot:body="props">
        <q-tr
          :props="props"
          @click="clickRow(props.row)"
          style="cursor: pointer; user-select: none"
          v-if="props.row.name != '..'"
        >
          <q-td>
            <q-checkbox v-model="props.selected" color="primary" />
          </q-td>
          <q-td key="type" :props="props" style="width: 1em">
            <q-icon :name="icons[props.row.type]" size="lg" />
          </q-td>
          <q-td key="name" :props="props">
            <q-item-label>{{ props.row.name }}</q-item-label>
          </q-td>
          <q-td key="permissions" :props="props">
            <q-item-label>{{ props.row.permissions }}</q-item-label>
          </q-td>
          <q-td key="size" :props="props">
            <q-item-label>{{ props.row.size }}</q-item-label>
          </q-td>
          <q-td key="modified" :props="props">
            <q-item-label>{{ props.row.modified }}</q-item-label>
          </q-td>
        </q-tr>
      </template>
      <template v-slot:top-row v-if="currentPath != '/'">
        <q-tr
          style="cursor: pointer; user-select: none"
          @click="getPath(paths[0].parentdir)"
        >
          <q-td />
          <q-td>
            <q-icon :name="icons.dirparent" size="lg" />
          </q-td>
          <q-td>
            <q-item-label>Previous Directory</q-item-label>
          </q-td>
          <q-td colspan="100%" />
        </q-tr>
      </template>
      <template v-slot:bottom-row>
        <q-tr no-hover>
          <q-td />
          <q-td colspan="100%">
            <q-item-label
              >{{
                paths.filter(
                  (path) => path.type.startsWith("dir") && path.name != "..",
                ).length
              }}
              directories,
              {{ paths.filter((path) => path.type.startsWith("file")).length }}
              files</q-item-label
            >
          </q-td>
        </q-tr>
      </template>
      <template v-slot:no-data>
        <p>This folder is empty</p>
      </template>
    </q-table>
    <ErrorDialog ref="errorDialog" />
    <ConfirmDialog ref="confirmDialog" />
    <q-dialog v-model="folderDialog" persistent>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Create folder</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <q-form @submit="folderDialogSubmit" class="q-gutter-xs">
            <q-input
              v-model="folderDialogName"
              label="Folder name"
              autofocus
              style="width: 25em"
              :rules="[val => !!val || 'Cannot be empty']"
            />
            <p class="q-mb-none q-mt-sm">Folder will be created at: {{ currentPath }}</p>
            <div class="row justify-end">
              <q-btn flat label="Create" type="submit" />
            </div>
          </q-form>
        </q-card-section>
        <q-inner-loading :showing="folderDialogLoading" />
      </q-card>
    </q-dialog>
    <q-dialog v-model="renameDialog" persistent>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Rename folder</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <q-form @submit="renameDialogSubmit" class="q-gutter-xs">
            <q-input
              v-model="renameDialogItem.name"
              label="Rename to"
              autofocus
              style="width: 25em"
            />
            <div class="row justify-end">
              <q-btn flat label="Rename" type="submit" />
            </div>
          </q-form>
        </q-card-section>
        <q-inner-loading :showing="renameDialogLoading" />
      </q-card>
    </q-dialog>
  </q-page>
</template>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";
export default {
  data() {
    return {
      currentPath: "/",
      tableLoading: false,
      paths: [],
      columns: [
        {
          name: "type",
          label: "Type",
          field: "type",
          align: "left",
          sortable: true,
        },
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "permissions",
          label: "Permissions",
          field: "permissions",
          align: "left",
          sortable: false,
        },
        {
          name: "size",
          label: "Size",
          field: "size",
          align: "left",
          sortable: false,
        },
        {
          name: "modified",
          label: "Modified",
          field: "modified",
          align: "left",
          sortable: true,
        },
      ],
      tablePagination: {
        rowsPerPage: 0,
        sortBy: "name",
        descending: false,
      },
      selected: [],
      icons: {
        dir: "mdi-folder",
        dirparent: "mdi-folder-upload-outline",
        file: "mdi-file",
        unknown: "mdi-file-question",
      },
      folderDialog: false,
      folderDialogName: "newfolder",
      folderDialogLoading: false,
      renameDialog: false,
      renameDialogItem: {},
      renameDialogLoading: false,
    };
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
  },
  methods: {
    clickRow(name) {
      if (name.type.startsWith("dir")) {
        this.getPath(name.path);
      }
    },
    getPath(path) {
      this.selected = [];
      this.tableLoading = true;
      this.currentPath = path;
      this.$api
        .post("system/file-manager", { path: path })
        .then((response) => {
          this.paths = response.data.list;
          this.tableLoading = false;
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error getting path", [errormsg]);
          this.tableLoading = false;
        });
    },
    removePath() {
      for (let i = 0; i < this.selected.length; i++) {
        let path = this.selected[i].path;
        this.$api
          .post("system/file-manager/remove", { path: path })
          .then((response) => {
            if (i == this.selected.length - 1) {
              this.getPath(this.currentPath);
            }
          })
          .catch((error) => {
            let errormsg = error.response ? error.response.data.detail : error;
            this.$refs.errorDialog.show("Error removing path", [errormsg]);
          });
      }
    },
    folderDialogSubmit() {
      const path = this.currentPath;
      const name = this.folderDialogName;
      this.folderDialogLoading = true;
      this.$api
        .post("system/file-manager/create-folder", { path: path, name: name })
        .then((response) => {
          this.getPath(this.currentPath);
          this.folderDialogLoading = false;
          this.folderDialog = false;
        })
        .catch((error) => {
          this.folderDialogLoading = false;
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error creating folder", [errormsg]);
        });
    },
    renameDialogSubmit() {
      const path = this.renameDialogItem.path;
      const name = this.renameDialogItem.name;
      this.renameDialogLoading = true;
      this.$api
        .post("system/file-manager/rename", { path: path, name: name })
        .then((response) => {
          this.getPath(this.currentPath);
          this.renameDialogLoading = false;
          this.renameDialog = false;
        })
        .catch((error) => {
          this.renameDialogLoading = false;
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error renaming folder", [errormsg]);
        });
    },
  },
  mounted() {
    this.getPath(this.currentPath);
  },
};
</script>
