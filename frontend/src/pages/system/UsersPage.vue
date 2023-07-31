<template>
  <q-page padding>
    <q-table
      title="Users"
      :rows="formattedUsers"
      :columns="table_culumns"
      :pagination="table_pagination"
    >
    </q-table>
    <ErrorDialog ref="errorDialog" />
  </q-page>
</template>
<script>
import ErrorDialog from "src/components/ErrorDialog.vue";

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
      ],
      table_pagination: {
        rowsPerPage: 15,
        sortBy: "name",
        descending: false,
      },
    };
  },
  components: {
    ErrorDialog,
  },
  methods: {
    getUsers() {
      this.$api
        .get("/system/users")
        .then((response) => {
          this.users = response.data;
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data : error;
          this.$refs.errorDialog.showError("Error getting users", [errormsg]);
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
