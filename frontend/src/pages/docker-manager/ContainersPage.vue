<template>
  <q-page padding>
    <q-table
      title="Containers"
      :loading="containersLoading"
      :rows="containerRows"
      :columns="containerColumns"
      row-key="id"
      no-data-label="No containers defined"
      :pagination="containerPagination"
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="mdi-refresh"
          flat
          round
          @click="containersUpdate"
        >
          <q-tooltip :offset="[0, 5]">Refresh Containers</q-tooltip>
        </q-btn>
        <q-btn color="primary" icon="mdi-plus" flat round @click="containerNew">
          <q-tooltip :offset="[0, 5]">New Custom Container</q-tooltip>
        </q-btn>
      </template>
      <template #body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props">
            {{ props.row.name }}
          </q-td>
          <q-td
            key="status"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.status }}
          </q-td>
          <q-td
            key="actions"
            :props="props"
            class="text-weight-regular text-body2"
          >
            <q-btn
              icon="mdi-play"
              flat
              round
              size="sm"
              padding="xs"
              @click="containerStart(props.row.id)"
              v-if="props.row.status !== 'running'"
            >
              <q-tooltip :offset="[0, 5]">Start</q-tooltip>
            </q-btn>
            <q-btn
              icon="mdi-stop"
              flat
              round
              size="sm"
              padding="xs"
              @click="containerStop(props.row.id)"
              v-if="props.row.status === 'running'"
            >
              <q-tooltip :offset="[0, 5]">Stop</q-tooltip>
            </q-btn>
            <q-btn
              icon="mdi-pencil"
              flat
              round
              size="sm"
              padding="xs"
              v-if="
                props.row.container_type !== 'unmanaged' &&
                props.row.status !== 'running' &&
                props.row.status !== 'paused'
              "
              @click="containerEdit(props.row.id)"
            >
              <q-tooltip :offset="[0, 5]">Edit</q-tooltip>
            </q-btn>
            <q-btn
              icon="mdi-delete"
              flat
              round
              size="sm"
              padding="xs"
              v-if="
                props.row.status !== 'running' && props.row.status !== 'paused'
              "
              @click="containerDelete(props.row.id)"
            >
              <q-tooltip :offset="[0, 5]">Delete</q-tooltip>
            </q-btn>
            <q-btn
              icon="mdi-open-in-new"
              flat
              round
              size="sm"
              padding="xs"
              v-if="props.row.status == 'running' && props.row.webui.enable"
              @click="containerWebui(props.row.id)"
            >
              <q-tooltip :offset="[0, 5]">WebUI</q-tooltip>
            </q-btn>
            <q-icon
              name="mdi-alert"
              color="warning"
              size="xs"
              v-if="props.row.container_type == 'unmanaged'"
            >
              <q-tooltip :offset="[0, 5]">
                This container is not managed by the WebUI.
              </q-tooltip>
            </q-icon>
          </q-td>
          <q-td
            key="network"
            :props="props"
            class="text-weight-regular text-body2"
          >
            <div v-if="props.row.container_type !== 'unmanaged'">
              {{ props.row.config.network.name }}
            </div>
            <div
              v-if="
                props.row.container_type !== 'unmanaged' &&
                props.row.config.network.ip != undefined &&
                props.row.config.network.dhcp_ip == undefined
              "
            >
              ip: {{ props.row.config.network.ip }}
            </div>
            <div
              v-if="
                props.row.container_type !== 'unmanaged' &&
                props.row.config.network.dhcp_ip != undefined
              "
            >
              ip: {{ props.row.config.network.dhcp_ip }}
            </div>
          </q-td>
          <q-td
            key="image"
            :props="props"
            class="text-weight-regular text-body2"
          >
            <span v-if="props.row.container_type !== 'unmanaged'"
              >{{ props.row.config.repository }}:{{
                props.row.config.tag
              }}</span
            >
            <span v-else></span>
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <ContainerTemplateInstall
      ref="editContainer"
      @finished="containersUpdate"
    />
    <ErrorDialog ref="errorDialog" />
  </q-page>
</template>

<script>
import ContainerTemplateInstall from "src/components/ContainerTemplateInstall.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
export default {
  data() {
    return {
      docker_version: null,
      docker_api_version: null,
      containersLoading: true,
      containerRows: [],
      containerColumns: [
        {
          label: "Name",
          field: "name",
          name: "name",
          align: "left",
          sortable: true,
        },
        {
          label: "Status",
          field: "status",
          name: "status",
          align: "left",
          sortable: true,
        },
        {
          label: "Actions",
          field: "actions",
          name: "actions",
          align: "left",
          sortable: false,
        },
        {
          label: "Network",
          field: "network",
          name: "network",
          align: "left",
          sortable: false,
        },
        {
          label: "Image",
          field: "image",
          name: "image",
          align: "left",
          sortable: true,
        },
      ],
      containerPagination: {
        sortBy: "name",
        rowsPerPage: 15,
      },
    };
  },
  components: {
    ContainerTemplateInstall,
    ErrorDialog,
  },
  methods: {
    containersUpdate() {
      this.containersLoading = true;
      this.$api
        .get("docker-manager/containers")
        .then((response) => {
          this.containerRows = response.data;
          this.containersLoading = false;
        })
        .catch((error) => {
          let errormsg =
            error.response != undefined ? error.response.data : error;
          this.$refs.errorDialog.show("Error getting docker data", [errormsg]);
        });
    },
    containerStart(id) {
      this.$api
        .post("docker-manager/container/" + id + "/start")
        .then((response) => {
          this.containersUpdate();
        })
        .catch((error) => {
          let errormsg =
            error.response != undefined ? error.response.data : error;
          this.$refs.errorDialog.show("Error starting container", [errormsg]);
        });
    },
    containerStop(id) {
      this.$api
        .post("docker-manager/container/" + id + "/stop")
        .then((response) => {
          this.containersUpdate();
        })
        .catch((error) => {
          let errormsg =
            error.response != undefined ? error.response.data : error;
          this.$refs.errorDialog.show("Error stopping container", [errormsg]);
        });
    },
    containerDelete(id) {
      this.$api
        .post("docker-manager/container/" + id + "/delete")
        .then((response) => {
          this.containersUpdate();
        })
        .catch((error) => {
          let errormsg =
            error.response != undefined ? error.response.data : error;
          this.$refs.errorDialog.show("Error deleting container", [errormsg]);
        });
    },
    containerWebui(id) {
      let container = this.containerRows.find(
        (container) => container.id === id,
      );
      if (container.webui.enable) {
        if (container.webui.url !== undefined) {
          window.open(container.webui.url, "_blank");
        } else if (container.webui["container-port"] !== undefined) {
          let port = container.webui["container-port"];
          let protocol = container.webui.ssl ? "https://" : "http://";
          let path = container.webui.path != null ? container.webui.path : "/";
          let ip;

          if (container.config.network.ip != null) {
            ip = container.config.network.ip;
            window.open(protocol + ip + ":" + port + path, "_blank");
          } else if (container.config.network.dhcp_ip != null) {
            ip = container.config.network.dhcp_ip;
            window.open(protocol + ip + ":" + port + path, "_blank");
          } else {
            this.$refs.errorDialog.show(
              "Error opening WebUI",
              "No IP address found for container",
            );
          }
        }
      }
    },
    containerEdit(id) {
      let dialogMode;
      // if the container has container_type 'custom' then use dialogMode 'edit-custom'else use dialogMode 'edit'
      let container = this.containerRows.find(
        (container) => container.id === id,
      );
      if (container.container_type == "custom") {
        dialogMode = "edit-custom";
      } else {
        dialogMode = "edit";
      }
      this.$refs.editContainer.showDialog(id, dialogMode);
    },
    containerNew() {
      this.$refs.editContainer.showDialog(null, "new-custom");
    },
  },
  mounted() {
    this.containersUpdate();
  },
};
</script>
