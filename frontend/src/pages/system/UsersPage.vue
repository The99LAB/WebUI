<template>
  <q-page padding>
    <q-table
      title="Users"
      :rows="formattedUsers"
      :columns="table_culumns"
      :pagination="table_pagination"
      selection="single"
      v-model:selected="table_selected"
      hide-selected-banner
      row-key="name"
      :loading="table_loading"
    >
      <template v-slot:loading>
        <q-inner-loading showing />
      </template>
      <template v-slot:top-right>
        <q-btn
          round
          flat
          color="primary"
          icon="mdi-pencil"
          :disable="
            table_selected.length === 0 || table_selected[0].name === 'root'
          "
          @click="editUserDialogShow"
        >
          <q-tooltip :offset="[5, 5]">Edit User</q-tooltip>
        </q-btn>
        <q-btn
          round
          flat
          color="primary"
          :disable="
            table_selected.length === 0 || table_selected[0].name === 'root'
          "
          icon="mdi-minus"
          @click="
            $refs.confirmDialog.show(
              'Remove User',
              ['Are you sure you want to remove this user?'],
              removeUser,
            )
          "
        >
          <q-tooltip :offset="[5, 5]">Remove User</q-tooltip>
        </q-btn>
      </template>
      <template v-slot:body-cell-smb="props">
        <q-td key="smb" :props="props">
          <q-icon
            :name="props.row.smb_user ? 'mdi-check' : 'mdi-close'"
            :color="props.row.smb_user ? 'green' : 'red'"
            size="sm"
          >
            <q-tooltip>
              {{ props.row.smb_user ? "SMB user" : "Not a SMB user" }}
            </q-tooltip>
          </q-icon>
        </q-td>
      </template>
    </q-table>
    <q-dialog v-model="editUserDialog" persistent>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Edit User</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section style="width: 30em">
          <q-input v-model="table_selected[0].name" label="Name" readonly />
          <q-form class="q-mt-md" @submit="editUserGeneral">
            <q-input
              v-model="editUserDialogPassword"
              label="Password"
              type="password"
              :rules="[
                (val) =>
                  val.length >= 8 || 'Password must be at least 8 characters',
              ]"
              lazy-rules
            />
            <q-input
              v-model="editUserDialogPasswordConfirm"
              label="Confirm Password"
              type="password"
              :rules="[
                (val) =>
                  val === editUserDialogPassword || 'Passwords do not match',
              ]"
              lazy-rules
            />
            <div class="row">
              <q-space />
              <q-btn
                class="q-mt-sm q-mb-md"
                label="Save"
                color="primary"
                outline
                type="submit"
              />
            </div>
          </q-form>
          <q-separator spaced="md" />
          <q-form @submit="editUserSmb">
            <q-checkbox
              v-model="editUserDialogSmb"
              left-label
              label="Enable SMB"
              class="q-mt-md"
            />
            <q-input
              v-model="editUserDialogSmbPassword"
              label="Password"
              type="password"
              v-if="editUserDialogSmb"
              :rules="[
                (val) =>
                  val.length >= 8 || 'Password must be at least 8 characters',
              ]"
            />
            <q-input
              v-model="editUserDialogSmbPasswordConfirm"
              label="Confirm Password"
              type="password"
              v-if="editUserDialogSmb"
              :rules="[
                (val) =>
                  val === editUserDialogSmbPassword || 'Passwords do not match',
              ]"
            />
            <div class="row">
              <q-space />
              <q-btn
                class="q-mt-sm q-mb-md"
                label="Save"
                color="primary"
                outline
                type="submit"
              />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
    </q-dialog>
    <ErrorDialog ref="errorDialog" />
    <ConfirmDialog ref="confirmDialog" />
  </q-page>
</template>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";

export default {
  data() {
    return {
      users: [],
      table_culumns: [
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "groups",
          label: "Groups",
          field: "groups",
          align: "left",
          sortable: false,
        },
        {
          name: "home",
          label: "Home",
          field: "home",
          align: "left",
          sortable: false,
        },
        {
          name: "shell",
          label: "Shell",
          field: "shell",
          align: "left",
          sortable: false,
        },
        {
          name: "uid",
          label: "UID",
          field: "uid",
          align: "left",
          sortable: true,
        },
        {
          name: "gid",
          label: "GID",
          field: "gid",
          align: "left",
          sortable: true,
        },
        {
          name: "smb",
          label: "SMB",
          field: "smb_user",
          align: "left",
        },
      ],
      table_pagination: {
        rowsPerPage: 15,
        sortBy: "name",
        descending: false,
      },
      table_selected: [],
      table_loading: false,
      editUserDialog: false,
      editUserDialogPassword: "",
      editUserDialogPasswordConfirm: "",
      editUserDialogSmb: false,
      editUserDialogSmbPassword: "",
      editUserDialogSmbPasswordConfirm: "",
    };
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
  },
  methods: {
    getUsers() {
      this.table_loading = true;
      this.$api
        .get("/system/users")
        .then((response) => {
          this.users = response.data;
          this.table_loading = false;
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data : error;
          this.$refs.errorDialog.showError("Error getting users", [errormsg]);
          this.table_loading = false;
        });
    },
    editUserDialogShow() {
      this.editUserDialogSmb = this.table_selected[0].smb_user ? true : false;
      this.editUserDialog = true;
    },
    editUserGeneral() {
      this.$api
        .post("system/users/change-password", {
          username: this.table_selected[0].name,
          password: this.editUserDialogPassword,
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error changing password", [errormsg]);
        });
    },
    editUserSmb() {
      if (this.editUserDialogSmb) {
        this.$api
          .post("system/users/change-smb-password", {
            username: this.table_selected[0].name,
            password: this.editUserDialogSmbPassword,
          })
          .then((response) => {
            this.getUsers();
          })
          .catch((error) => {
            const errormsg = error.response
              ? error.response.data.detail
              : error;
            this.$refs.errorDialog.show("Error changing smb password", [
              errormsg,
            ]);
          });
      } else {
        this.$api
          .post("system/users/remove-smb-user", {
            username: this.table_selected[0].name,
          })
          .then((response) => {
            this.getUsers();
          })
          .catch((error) => {
            const errormsg = error.response
              ? error.response.data.detail
              : error;
            this.$refs.errorDialog.show("Error removing smb user", [errormsg]);
          });
      }
    },
    removeUser() {
      this.table_loading = true;
      this.$api
        .post("system/users/remove-user", {
          username: this.table_selected[0].name,
        })
        .then((response) => {
          this.getUsers();
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error removing user", [errormsg]);
        });
    },
  },
  computed: {
    formattedUsers() {
      return this.users.map((user) => ({
        ...user,
        groups: user.groups.join(", "), // Convert the groups array to a string
      }));
    },
  },
  mounted() {
    this.getUsers();
  },
};
</script>
