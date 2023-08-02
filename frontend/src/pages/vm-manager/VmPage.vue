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
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="mdi-plus"
          label="new VM"
          @click="createVm()"
        />
      </template>
      <template #body="props">
        <q-tr :props="props">
          <q-td
            key="name"
            :props="props"
            class="text-weight-regular text-body2"
            @click="props.expand = !props.expand"
            style="cursor: pointer; user-select: none"
          >
            <q-icon
              :name="props.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              size="sm"
            />
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
        <q-tr v-show="props.expand" :props="props">
          <q-td colspan="100%">
            <div>
              <q-btn
                class="q-ma-sm"
                color="primary"
                icon="mdi-play"
                label="Start"
                v-if="props.row.state != 'Running'"
                @click="startVm(props.row.uuid)"
              />
              <q-btn
                class="q-ma-sm"
                color="primary"
                icon="mdi-delete"
                label="Remove"
                v-if="props.row.state == 'Shutoff'"
                @click="removeVm(props.row.uuid)"
              />
              <q-btn
                class="q-ma-sm"
                color="primary"
                icon="mdi-stop"
                label="Stop"
                v-if="props.row.state == 'Running'"
                @click="stopVm(props.row.uuid)"
              />
              <q-btn
                class="q-ma-sm"
                color="primary"
                icon="mdi-bomb"
                label="Force stop"
                v-if="props.row.state == 'Running'"
                @click="forceStopVm(props.row.uuid)"
              />
              <q-btn
                class="q-ma-sm"
                color="primary"
                icon="mdi-eye"
                label="VNC"
                v-if="props.row.VNC && props.row.state == 'Running'"
                @click="vncVm(props.row.uuid)"
              />
              <q-btn
                class="q-ma-sm"
                color="primary"
                icon="mdi-pencil"
                label="Edit"
                v-if="props.row.state == 'Shutoff'"
                @click="editVm(props.row.uuid)"
              />
              <q-btn
                class="q-ma-sm"
                color="primary"
                icon="mdi-file-document"
                label="Logs"
                @click="logsVm(props.row.uuid)"
              />
            </div>
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <ErrorDialog ref="errorDialog" />
    <CreateVm ref="createVm" />
    <EditVm ref="editVm" />
    <LogDialog ref="logDialog" />
    <WsReconnectDialog
      ref="wsReconnectDialog"
      @ws-reconnect="connectWebSocket"
    />
  </q-page>
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import CreateVm from "src/components/CreateVm.vue";
import EditVm from "src/components/EditVm.vue";
import LogDialog from "src/components/LogDialog.vue";
import WsReconnectDialog from "src/components/WsReconnectDialog.vue";
import { useVncSettingsStore } from "stores/vncsettings";
import { storeToRefs } from "pinia";

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
        {
          label: "Autostart",
          field: "autostart",
          name: "autostart",
          align: "left",
        },
      ],
      selected: [],
      vmTableLoading: ref(true),
      vmTablePagination: {
        rowsPerPage: 15,
        sortBy: "name",
        descending: false,
      },
    };
  },
  setup() {
    const store = useVncSettingsStore();
    const { getVncSettings } = storeToRefs(store);
    return {
      vncSettings: getVncSettings,
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
      this.$api
        .get("vm-manager/" + uuid + "/logs")
        .then((response) => {
          this.$refs.logDialog.show("VM Logs", response.data.log);
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting logs", [
            "vm uuid: " + uuid,
            "Error: " + error.response.data.detail,
          ]);
        });
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
      if (
        this.vncSettings.protocool == null ||
        this.vncSettings.ip == null ||
        this.vncSettings.port == null ||
        this.vncSettings.path == null
      ) {
        this.$refs.errorDialog.show("Error getting VNC settings", [
          "Error: VNC settings not set",
          "Please set VNC settings in the settings page.",
        ]);
        return;
      } else {
        const novnc_url =
          this.vncSettings.protocool +
          "://" +
          this.vncSettings.ip +
          ":" +
          this.vncSettings.port +
          "/" +
          this.vncSettings.path +
          "?autoconnect=true&?reconnect=true&?resize=scale&?path=?token=" +
          uuid;
        window.open(novnc_url, "_blank");
      }
    },
    autostartVm(uuid) {
      let autostart = this.rows.find((vm) => vm.uuid === uuid).autostart;
      this.$api
        .post("vm-manager/" + uuid + "/autostart", { autostart: autostart })
        .catch((error) => {
          this.$refs.errorDialog.show("Error setting autostart", [
            "vm uuid: " + uuid,
            "Error: " + error.response.data.detail,
          ]);
        });
    },
    editVm(uuid) {
      this.$refs.editVm.show(uuid);
    },
    createVm() {
      this.$refs.createVm.show();
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
          this.vmTableLoading = false;
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
  mounted() {},
  unmounted() {
    this.vmTableLoading = false;
    this.ws.onclose = () => {};
    this.ws.close();
  },
};
</script>
