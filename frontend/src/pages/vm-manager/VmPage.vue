<template>
  <q-page padding>
    <q-table
      title="Virtual Machines"
      :loading="vmTableLoading"
      :rows="rows"
      :columns="columns"
      row-key="uuid"
      separator="none"
      no-data-label="Failed to get data from backend or no vm's defined"
      :pagination="vmTablePagination"
    >
      <template v-slot:loading>
        <q-inner-loading showing />
      </template>
      <template v-slot:top-right>
        <q-btn color="primary" icon="mdi-plus" round flat @click="createVm()">
          <q-tooltip :offset="[5, 5]">Create new VM</q-tooltip>
        </q-btn>
      </template>
      <template #body="props">
        <q-tr :props="props">
          <q-td
            key="name"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.name }}
          </q-td>
          <q-td
            key="state"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.state }}
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
              @click="startVm(props.row.uuid)"
              v-if="props.row.state != 'Running'"
            >
              <q-tooltip :offset="[0, 5]">Start</q-tooltip>
            </q-btn>
            <q-btn
              icon="mdi-stop"
              flat
              round
              size="sm"
              padding="xs"
              @click="stopVm(props.row.uuid)"
              v-if="props.row.state == 'Running'"
            >
              <q-tooltip :offset="[0, 5]">Stop</q-tooltip>
            </q-btn>
            <q-btn
              icon="mdi-bomb"
              flat
              round
              size="sm"
              padding="xs"
              @click="forceStopVm(props.row.uuid)"
              v-if="props.row.state == 'Running'"
            >
              <q-tooltip :offset="[0, 5]">Force Stop</q-tooltip>
            </q-btn>
            <q-btn
              icon="mdi-open-in-new"
              flat
              round
              size="sm"
              padding="xs"
              v-if="props.row.VNC && props.row.state == 'Running'"
              @click="vncVm(props.row.uuid)"
            >
              <q-tooltip :offset="[0, 5]">WebUI</q-tooltip>
            </q-btn>
            <q-btn
              icon="mdi-pencil"
              flat
              round
              size="sm"
              padding="xs"
              v-if="props.row.state == 'Shutoff'"
              @click="editVm(props.row.uuid)"
            >
              <q-tooltip :offset="[0, 5]">Edit</q-tooltip>
            </q-btn>
            <q-btn
              icon="mdi-file-document"
              flat
              round
              size="sm"
              padding="xs"
              @click="logsVm(props.row.uuid)"
            >
              <q-tooltip :offset="[0, 5]">Log</q-tooltip>
            </q-btn>
          </q-td>
          <q-td
            key="vcpus"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.vcpus }}
          </q-td>
          <q-td
            key="memory_min"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.memory_min }} {{ props.row.memory_min_unit }}
          </q-td>
          <q-td
            key="memory_max"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.memory_max }} {{ props.row.memory_max_unit }}
          </q-td>
          <q-td
            key="autostart"
            :props="props"
            class="text-weight-regular text-body2"
          >
            <q-toggle
              v-model="props.row.autostart"
              @update:model-value="autostartVm(props.row.uuid)"
            />
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <ErrorDialog ref="errorDialog" />
    <CreateVm ref="createVm" />
    <EditVm ref="editVm" />
    <LogDialog ref="logVm" />
    <WsReconnectDialog
      ref="wsReconnectDialog"
      @ws-reconnect="connectWebSocket"
    />
  </q-page>
</template>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";
import CreateVm from "src/components/vm-manager/CreateVm.vue";
import EditVm from "src/components/vm-manager/EditVm.vue";
import LogDialog from "src/components/vm-manager/VmLogDialog.vue";
import WsReconnectDialog from "src/components/WsReconnectDialog.vue";

export default {
  data() {
    return {
      rows: [],
      columns: [
        {
          label: "Name",
          field: "name",
          name: "name",
          align: "left",
          sortable: true,
        },
        {
          label: "State",
          field: "state",
          name: "state",
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
          label: "vCPUs",
          field: "vcpus",
          name: "vcpus",
          align: "left",
          sortable: true,
        },
        {
          label: "Memory min",
          field: "memory_min",
          name: "memory_min",
          align: "left",
          sortable: true,
        },
        {
          label: "Memory max",
          field: "memory_max",
          name: "memory_max",
          align: "left",
          sortable: true,
        },
      ],
      selected: [],
      vmTableLoading: false,
      vmTablePagination: {
        rowsPerPage: 15,
        sortBy: "name",
        descending: false,
      },
    };
  },
  components: {
    ErrorDialog,
    CreateVm,
    EditVm,
    LogDialog,
    WsReconnectDialog,
  },
  methods: {
    startVm(uuid) {
      console.log("starting vm with uuid", uuid);
      this.$api.post("vm-manager/" + uuid + "/start").catch((error) => {
        this.$refs.errorDialog.show("Error starting VM", [
          "vm uuid: " + uuid,
          "Error: " + error.response.data.detail,
        ]);
      });
    },
    stopVm(uuid) {
      console.log("stopping vm with uuid", uuid);
      this.$api.post("vm-manager/" + uuid + "/stop").catch((error) => {
        this.$refs.errorDialog.show("Error stopping VM", [
          "vm uuid: " + uuid,
          "Error: " + error.response.data.detail,
        ]);
      });
    },
    forceStopVm(uuid) {
      console.log("force stopping vm with uuid", uuid);
      this.$api.post("vm-manager/" + uuid + "/forcestop").catch((error) => {
        this.$refs.errorDialog.show("Error force stopping VM", [
          "vm uuid: " + uuid,
          "Error: " + error.response.data.detail,
        ]);
      });
    },
    logsVm(uuid) {
      console.log("logs vm with uuid", uuid);
      this.$refs.logVm.show(uuid);
    },
    removeVm(uuid) {
      console.log("removing vm with uuid", uuid);
      this.$api.post("vm-manager/" + uuid + "/remove").catch((error) => {
        this.$refs.errorDialog.show("Error removing VM", [
          "vm uuid: " + uuid,
          "Error: " + error.response.data.detail,
        ]);
      });
    },
    vncVm(uuid) {
      console.log("vnc vm with uuid", uuid);
      const novnc_url =
        this.vncSettings.protocol +
        "://" +
        this.vncSettings.ip +
        ":" +
        this.vncSettings.port +
        "/" +
        this.vncSettings.path +
        "?autoconnect=true&?reconnect=true&?resize=scale&?path=?token=" +
        uuid;
      window.open(novnc_url, "_blank");
    },
    autostartVm(uuid) {
      this.vmTableLoading = true;
      let autostart = this.rows.find((vm) => vm.uuid === uuid).autostart;
      this.$api
        .post("vm-manager/" + uuid + "/autostart", { autostart: autostart })
        .then((response) => {
          this.vmTableLoading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error setting autostart", [
            "vm uuid: " + uuid,
            "Error: " + error.response.data.detail,
          ]);
          this.vmTableLoading = false;
        });
    },
    editVm(uuid) {
      this.$refs.editVm.show(uuid);
    },
    createVm() {
      this.$refs.createVm.show();
    },
    getVncSettings() {
      this.vmTableLoading = true;
      this.$api
        .get("setting/vnc")
        .then((response) => {
          this.vncSettings = response.data;
          this.vmTableLoading = false;
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error getting VNC settings", [errormsg]);
        });
    },
    connectWebSocket() {
      const jwt_token = localStorage.getItem("jwt-token");
      this.ws = new WebSocket(this.$WS_ENDPOINT + "/vmdata?token=" + jwt_token);

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type == "vmdata") {
          if (data.data != null) {
            this.rows = data.data;
          }
        } else if (data.type == "auth_error") {
          localStorage.setItem("jwt-token", "");
          this.$router.push({ path: "/login" });
        }
      };
      this.ws.onclose = () => {
        this.$refs.wsReconnectDialog.show();
        this.vmTableLoading = true;
      };
    },
  },
  created() {
    this.connectWebSocket();
  },
  mounted() {
    this.getVncSettings();
  },
  unmounted() {
    this.vmTableLoading = false;
    this.ws.onclose = () => {};
    this.ws.close();
  },
};
</script>
