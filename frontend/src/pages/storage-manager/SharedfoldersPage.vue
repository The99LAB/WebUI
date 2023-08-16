<template>
  <q-page padding>
    <q-table
      title="Shared Folders"
      :rows="sharedFolders"
      :columns="SharedFoldersColumns"
      v-model:selected="sharedFoldersSelected"
      selection="single"
      hide-selected-banner
      :pagination="sharedFoldersPagination"
      :loading="sharedFoldersLoading"
      row-key="name"
    >
      <template v-slot:loading>
        <q-inner-loading showing />
      </template>
      <template v-slot:top-right>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-plus"
          @click="sharedFolderCreateDialogOpen"
        >
          <q-tooltip :offset="[5, 5]"> Add a new shared folder </q-tooltip>
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-minus"
          :disable="sharedFoldersSelected.length == 0"
          @click="
            $refs.confirmDialog.show(
              'Delete shared folder',
              [
                'Are you sure you want to delete the selected shared folder?',
                'This action cannot be undone.',
              ],
              sharedFolderDelete,
            )
          "
        >
          <q-tooltip :offset="[5, 5]">
            Remove the selected shared folder
          </q-tooltip>
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-pencil"
          :disable="sharedFoldersSelected.length == 0"
          @click="sharedFolderShowEdit"
        >
          <q-tooltip :offset="[5, 5]">
            Edit the selected shared folder
          </q-tooltip>
        </q-btn>
      </template>
      <template v-slot:body-cell-name="props">
        <q-td key="name" :props="props">
          <q-chip class="q-mx-none" :label="props.row.name" color="primary" />
        </q-td>
      </template>
      <template v-slot:body-cell-status="props">
        <q-td key="status" :props="props">
          <q-chip
            class="q-mx-none"
            :label="props.row.active ? 'Online' : 'Offline'"
            :color="props.row.active ? 'positive' : 'negative'"
          >
            <q-tooltip :offset="[5, 5]">
              {{ props.row.active ? "Active" : "Inactive" }}
            </q-tooltip>
          </q-chip>
          <q-icon
            name="mdi-alert"
            color="orange"
            size="sm"
            v-if="props.row.active == false"
          >
            <q-tooltip :offset="[5, 5]">
              This shared folder is offline. <br />
              The RAID array or the disk where this shared folder is located is
              offline.
            </q-tooltip>
          </q-icon>
        </q-td>
      </template>
      <template v-slot:body-cell-capacity="props">
        <q-td key="capacity" :props="props">
          {{ props.row.free }}
          <q-tooltip :offset="[5, 5]">
            Used space: {{ props.row.used }} / {{ props.row.capacity }}
          </q-tooltip>
        </q-td>
      </template>
      <template v-slot:body-cell-storage="props">
        <q-td key="storage" :props="props">
          <div class="row items-center justify-center">
            <q-icon
              :name="
                props.row.linked_storage.type == 'raid'
                  ? 'mdi-database-outline'
                  : 'bi-hdd'
              "
              size="sm"
            />
            <span class="text-weight-bold text-subtitle1 q-ml-xs">
              {{
                props.row.linked_storage.name
                  ? props.row.linked_storage.name
                  : "Unknown"
              }}
            </span>
            <q-tooltip
              :offset="[5, 5]"
              v-if="props.row.linked_storage.type == 'raid'"
            >
              This shared folder is located on the RAID array
              {{ props.row.linked_storage.name }}
            </q-tooltip>
            <q-tooltip
              :offset="[5, 5]"
              v-else-if="props.row.linked_storage.type == 'disk'"
            >
              This shared folder is located on the disk
              {{ props.row.linked_storage.name }}
            </q-tooltip>
            <q-tooltip :offset="[5, 5]" v-else>
              This shared folder is located on a device that is not managed by
              the WebUI
            </q-tooltip>
          </div>
        </q-td>
      </template>
      <template v-slot:body-cell-path="props">
        <q-td key="path" :props="props">
          <q-chip
            class="q-mx-none"
            style="cursor: pointer"
            :label="props.row.path"
            color="primary"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-smb="props">
        <q-td key="smb" :props="props">
          <q-chip
            class="q-mx-none"
            :label="props.row.smb_share.name ? 'Enabled' : 'Disabled'"
            :color="props.row.smb_share.name ? 'positive' : 'primary'"
          >
            <q-tooltip :offset="[5, 5]"> SMB share status </q-tooltip>
          </q-chip>
        </q-td>
      </template>
    </q-table>
    <q-dialog v-model="sharedFolderCreateDialog" persistent>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Create Shared Folder</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="sm" inset />
        <q-card-section>
          <q-form
            @submit="sharedFolderCreate"
            class="q-gutter-md"
            style="width: 25em"
          >
            <q-input
              filled
              v-model="sharedFolderCreateName"
              label="Name"
              :rules="[
                (val) => !!val || 'Name is required',
                (val) => !val.includes(' ') || 'Name cannot contain spaces',
              ]"
            />
            <q-toggle v-model="sharedFolderCreateCustom" label="Custom Path" class="q-mt-none" />
            <DirectoryList
              v-if="sharedFolderCreateCustom"
              v-model="sharedFolderCreateCustomPath"
              selectiontype="dir"
            />
            <q-select
              v-else
              filled
              v-model="sharedFolderCreateTarget"
              :options="sharedFolderCreateTargetOptions"
              label="Target"
              option-label="name"
              :rules="[(val) => !!val || 'Target is required']"
            >
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section>
                    <q-item-label>{{ scope.opt.name }}</q-item-label>
                    <q-item-label caption>
                      <span class="row justify-between">
                        <span>
                          {{
                            scope.opt.type == "raid"
                              ? "RAID Array"
                              : scope.opt.type == "disk"
                              ? "Individual Disk"
                              : ""
                          }}
                        </span>
                        <span>
                          {{ scope.opt.mountpoint }}
                        </span>
                      </span>
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </template>
              <template v-slot:selected-item="scope">
                <q-item v-bind="scope.itemProps" class="q-pl-none">
                  <q-item-section>
                    <q-item-label>{{ scope.opt.name }}</q-item-label>
                    <q-item-label caption>
                      <span class="row justify-between">
                        <span>
                          {{
                            scope.opt.type == "raid"
                              ? "RAID Array"
                              : scope.opt.type == "disk"
                              ? "Individual Disk"
                              : ""
                          }}
                        </span>
                        <span>
                          {{ scope.opt.mountpoint }}
                        </span>
                      </span>
                    </q-item-label>
                  </q-item-section>
                </q-item>
              </template>
            </q-select>
            <div class="row justify-end">
              <q-btn flat label="Create" type="submit" />
            </div>
          </q-form>
        </q-card-section>
        <q-inner-loading :showing="sharedFolderCreateLoading" />
      </q-card>
    </q-dialog>
    <q-dialog
      full-width
      full-height
      v-model="sharedFolderEditDialog"
      persistent
    >
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Edit Shared Folder</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="sm" inset />
        <q-card-section>
          <q-form @submit="sharedFolderEdit" class="q-gutter-md">
            <p class="text-h6 q-mb-none">
              <q-icon class="q-mr-sm" name="mdi-share-variant-outline" />General
            </p>
            <q-input
              filled
              v-model="sharedFolderEditDialogData.name"
              label="Name"
              readonly
            />
            <q-input
              filled
              v-model="sharedFolderEditDialogData.path"
              label="Path"
              readonly
            />
            <p class="text-h6 q-mb-none q-mt-xl">
              <q-icon class="q-mr-sm" name="bi-hdd-network" />SMB Settings
            </p>
            <q-checkbox
              class="q-mt-none"
              v-model="sharedFolderEditDialogData.smb_share_status"
              label="Enabled"
            />
            <q-select
              v-if="sharedFolderEditDialogData.smb_share_status"
              filled
              v-model="sharedFolderEditDialogData.smb_share_guest"
              label="Guest Access"
              :options="sharedFolderEditDialogGuestOptions"
              @update:model-value="
                (val) => sharedFolderEditUsersChange(val.value)
              "
            >
              <template v-slot:after>
                <q-icon
                  name="mdi-help-circle-outline"
                  @click="
                    $refs.errorDialog.show('Guest Access', [
                      'Guest Access determines the level of access guests have to this shared folder. Guests are users who are not logged in.',
                      'Read/Write: All users including guests have full read/write access',
                      'Read Only: All users including guests have read only access. You chose which users have read/write access.',
                      'No Access: Guests have no access. You chose which users have read or read/write access.',
                    ])
                  "
                  style="cursor: pointer"
                />
              </template>
            </q-select>
            <div
              v-if="
                sharedFolderEditDialogData.smb_share_status &&
                sharedFolderEditDialogSmbUsers.length != 0
              "
            >
              <p>SMB User Access</p>
              <q-table
                :rows="sharedFolderEditDialogSmbUsers"
                :columns="[
                  { name: 'name', label: 'Name', field: 'name', align: 'left' },
                  {
                    name: 'access',
                    label: 'Access',
                    field: 'access',
                    align: 'center',
                  },
                ]"
                row-key="name"
                hide-header
                hide-bottom
                :pagination="{
                  rowsPerPage: 0,
                }"
              >
                <template v-slot:body-cell-access="props">
                  <q-td key="access" :props="props">
                    <q-select
                      filled
                      v-model="props.row.access"
                      :options="sharedFolderEditDialogSmbUsersOptions"
                    />
                  </q-td>
                </template>
              </q-table>
            </div>
            <div class="row justify-end">
              <q-btn label="Save" type="submit" color="primary" />
            </div>
          </q-form>
        </q-card-section>
        <q-inner-loading :showing="sharedFolderEditLoading" />
      </q-card>
    </q-dialog>
    <ErrorDialog ref="errorDialog" />
    <ConfirmDialog ref="confirmDialog" />
  </q-page>
</template>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";
import DirectoryList from "src/components/DirectoryList.vue";

export default {
  data() {
    return {
      sharedFolders: [],
      sharedFoldersLoading: false,
      SharedFoldersColumns: [
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
        },
        {
          name: "status",
          label: "Status",
          field: "status",
          align: "center",
        },
        {
          name: "smb",
          label: "SMB",
          field: "smb",
          align: "center",
        },
        {
          name: "capacity",
          label: "Free Space",
          field: "capacity",
          align: "center",
        },
        {
          name: "storage",
          label: "Storage",
          field: "storage",
          align: "center",
        },
        {
          name: "path",
          label: "Path",
          field: "path",
          align: "center",
        },
      ],
      sharedFoldersSelected: [],
      sharedFoldersPagination: {
        sortBy: "name",
        descending: false,
        page: 1,
        rowsPerPage: 10,
      },
      sharedFolderCreateDialog: false,
      sharedFolderCreateName: "",
      sharedFolderCreateTarget: "",
      sharedFolderCreateTargetOptions: [],
      sharedFolderCreateLoading: false,
      sharedFolderCreateCustom: false,
      sharedFolderCreateCustomPath: null,
      sharedFolderEditDialog: false,
      sharedFolderEditDialogData: {},
      sharedFolderEditLoading: false,
      sharedFolderEditDialogGuestOptions: [
        {
          label: "Read/Write",
          value: "rw",
        },
        {
          label: "Read Only",
          value: "ro",
        },
        {
          label: "No Access",
          value: "none",
        },
      ],
      sharedFolderEditDialogRoOptions: [
        {
          label: "Read/Write",
          value: "rw",
        },
        {
          label: "Read Only",
          value: "ro",
        },
      ],
      sharedFolderEditDialogNoneOptions: [
        {
          label: "Read/Write",
          value: "rw",
        },
        {
          label: "Read Only",
          value: "ro",
        },
        {
          label: "No Access",
          value: "none",
        },
      ],
      sharedFolderEditDialogSmbUsers: [],
      sharedFolderEditDialogSmbUsersOptions: [],
    };
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
    DirectoryList,
  },
  methods: {
    fetchData() {
      this.sharedFoldersLoading = true;
      this.$api
        .get("storage/sharedfolders")
        .then((response) => {
          this.sharedFolders = response.data;
          this.sharedFoldersLoading = false;
          this.sharedFoldersSelected = [];
        })
        .catch((error) => {
          this.sharedFoldersLoading = false;
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error fetching shared folders", [
            errormsg,
          ]);
        });
    },
    sharedFolderCreate() {
      this.sharedFolderCreateLoading = true;
      let target;
      if(this.sharedFolderCreateCustom){
        target = this.sharedFolderCreateCustomPath;
        if (target == null){
          this.sharedFolderCreateLoading = false;
          this.$refs.errorDialog.show("Error creating shared folder", [
            "Path is required",
          ]);
          return;
        }
      } else {
        target = this.sharedFolderCreateTarget.mountpoint;
      }

      this.$api
        .post("storage/sharedfolders/create", {
          name: this.sharedFolderCreateName,
          target: target,
        })
        .then((response) => {
          this.fetchData();
          this.sharedFolderCreateLoading = false;
          this.sharedFolderCreateDialog = false;
        })
        .catch((error) => {
          this.sharedFolderCreateLoading = false;
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error creating shared folder", [
            errormsg,
          ]);
        });
    },
    sharedFolderDelete() {
      this.$api
        .post("storage/sharedfolders/delete", {
          name: this.sharedFoldersSelected[0].name,
        })
        .then((response) => {
          this.fetchData();
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error deleting shared folder", [
            errormsg,
          ]);
        });
    },
    sharedFolderEdit() {
      const status = this.sharedFolderEditDialogData.smb_share_status;
      const name = this.sharedFolderEditDialogData.name;
      const path = this.sharedFolderEditDialogData.path;
      if (status) {
        const mode = this.sharedFolderEditDialogData.smb_share_guest.value;
        if (mode == "rw") {
          this.sharedFolderEditLoading = true;
          this.$api
            .post("storage/sharedfolders/smb-edit", {
              name: name,
              status: true,
              path: path,
              mode: "PUBLIC",
            })
            .then((response) => {
              this.fetchData();
              this.sharedFolderEditLoading = false;
              this.sharedFolderEditDialog = false;
            })
            .catch((error) => {
              const errormsg = error.response
                ? error.response.data.detail
                : error;
              this.$refs.errorDialog.show("Error editing shared folder", [
                errormsg,
              ]);
            });
        } else {
          const users = this.sharedFolderEditDialogSmbUsers.map((user) => {
            return {
              name: user.name,
              mode: user.access.value,
            };
          });
          this.sharedFolderEditLoading = true;
          this.$api
            .post("storage/sharedfolders/smb-edit", {
              name: name,
              status: true,
              path: path,
              mode: mode == "ro" ? "SECURE" : "PRIVATE",
              users: users,
            })
            .then((response) => {
              this.fetchData();
              this.sharedFolderEditLoading = false;
              this.sharedFolderEditDialog = false;
            })
            .catch((error) => {
              const errormsg = error.response
                ? error.response.data.detail
                : error;
              this.$refs.errorDialog.show("Error editing shared folder", [
                errormsg,
              ]);
            });
        }
      } else {
        this.sharedFolderEditLoading = true;
        this.$api
          .post("storage/sharedfolders/smb-edit", {
            name: name,
            status: false,
          })
          .then((response) => {
            this.fetchData();
            this.sharedFolderEditLoading = false;
            this.sharedFolderEditDialog = false;
          })
          .catch((error) => {
            const errormsg = error.response
              ? error.response.data.detail
              : error;
            this.$refs.errorDialog.show("Error editing shared folder", [
              errormsg,
            ]);
          });
      }
    },
    sharedFolderShowEdit() {
      this.sharedFolderEditDialogData = this.sharedFoldersSelected[0];

      // add smbsharestatus  to sharedFolderEditDialogData
      this.sharedFolderEditDialogData.smb_share_status = this
        .sharedFolderEditDialogData.smb_share.name
        ? true
        : false;

      if (!this.sharedFolderEditDialogData.smb_share_status) {
        this.sharedFolderEditDialogData.smb_share_guest =
          this.sharedFolderEditDialogGuestOptions.find(
            (option) => option.value == "rw",
          );
        this.sharedFolderEditUsersChange("rw");
      } else {
        // smb_share_guest, depends on mode.
        // mode = PUBLIC, smb_share_guest = 'rw'
        // mode = SECURE, smb_share_guest = 'ro'
        // mode = PRIVATE, smb_share_guest = 'none'
        const smb_share_guest =
          this.sharedFolderEditDialogData.smb_share.mode == "PUBLIC"
            ? "rw"
            : this.sharedFolderEditDialogData.smb_share.mode == "SECURE"
            ? "ro"
            : "none";
        this.sharedFolderEditDialogData.smb_share_guest =
          this.sharedFolderEditDialogGuestOptions.find(
            (option) => option.value == smb_share_guest,
          );
        this.sharedFolderEditUsersChange(smb_share_guest, true);
      }
      console.log(
        "sharedFolderEditDialogData",
        this.sharedFolderEditDialogData,
      );
      this.sharedFolderEditDialog = true;
    },
    sharedFolderEditUsersChange(mode, init = false) {
      if (mode == "none") {
        this.sharedFolderEditDialogSmbUsers =
          this.sharedFolderEditDialogData.smb_share.users.map((user) => {
            const accessval = init ? user.mode : "none";
            return {
              name: user.name,
              access: this.sharedFolderEditDialogGuestOptions.find(
                (option) => option.value == accessval,
              ),
            };
          });
        this.sharedFolderEditDialogSmbUsersOptions =
          this.sharedFolderEditDialogNoneOptions;
      } else if (mode == "ro") {
        this.sharedFolderEditDialogSmbUsers =
          this.sharedFolderEditDialogData.smb_share.users.map((user) => {
            const accessval = init ? user.mode : "ro";
            return {
              name: user.name,
              access: this.sharedFolderEditDialogGuestOptions.find(
                (option) => option.value == accessval,
              ),
            };
          });
        this.sharedFolderEditDialogSmbUsersOptions =
          this.sharedFolderEditDialogRoOptions;
      } else if (mode == "rw") {
        this.sharedFolderEditDialogSmbUsers = [];
        this.sharedFolderEditDialogSmbUsersOptions =
          this.sharedFolderEditDialogGuestOptions;
      }
    },
    sharedFolderCreateDialogOpen() {
      this.sharedFolderCreateDialog = true;
      this.sharedFolderCreateLoading = true;
      this.$api
        .get("storage/sharedfolders/availabledevices")
        .then((response) => {
          this.sharedFolderCreateTargetOptions = response.data;
          this.sharedFolderCreateLoading = false;
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error getting available devices", [
            errormsg,
          ]);
          this.sharedFolderCreateLoading = false;
        });
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>
