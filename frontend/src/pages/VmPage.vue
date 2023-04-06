<template>
  <q-page padding>
    <div class="row">
      <q-space />
      <q-btn
        class="q-ma-sm"
        color="primary"
        icon="mdi-plus"
        label="Create VM"
        @click="createVm()"
      />
    </div>
    <q-table
      :loading="vmTableLoading"
      :rows="rows"
      :columns="columns"
      row-key="uuid"
      separator="none"
      no-data-label="Failed to get data from backend or no vm's defined"
      hide-pagination
    >
      <template #body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props">
            <q-btn
              flat
              dense
              :ripple="false"
              :icon="props.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              @click="props.expand = !props.expand"
              no-caps
              :label="props.row.name"
              class="text-weight-regular text-body2 disable-focus-helper"
            />
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
            {{ props.row.memory_min }} {{ props.row.memory_unit }}
          </q-td>
          <q-td
            key="memory_max"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.memory_max }} {{ props.row.memory_unit }}
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
            </div>
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <ErrorDialog ref="errorDialog"></ErrorDialog>
    <CreateVm ref="createVm"></CreateVm>
    <EditVm ref="editVm"></EditVm>
    <WsReconnectDialog
      ref="wsReconnectDialog"
      @ws-reconnect="connectWebSocket"
    ></WsReconnectDialog>
  </q-page>
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import CreateVm from "src/components/CreateVm.vue";
import EditVm from "src/components/EditVm.vue";
import WsReconnectDialog from "src/components/WsReconnectDialog.vue";

const selected = ref();

const rows = [];

const columns = [
  { label: "Name", field: "name", name: "name", align: "left" },
  { label: "State", field: "state", name: "state", align: "left" },
  { label: "vCPUs", field: "vcpus", name: "vcpus", align: "left" },
  {
    label: "Memory min",
    field: "memory_min",
    name: "memory_min",
    align: "left",
  },
  {
    label: "Memory max",
    field: "memory_max",
    name: "memory_max",
    align: "left",
  },
];

export default {
  data() {
    return {
      rows,
      columns,
      selected,
      vmTableLoading: ref(true),
      novnc_port: null,
      novnc_protocool: null,
      novnc_path: null,
      novnc_ip: null,
    };
  },
  components: {
    ErrorDialog,
    CreateVm,
    EditVm,
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
    removeVm(uuid) {
      console.log("removing vm with uuid", uuid);
      this.$api.post("vm-manager/" + uuid + "/remove").catch((error) => {
        this.$refs.errorDialog.show("Error removing VM", [
          "vm uuid: " + uuid,
          "Error: " + error.response.data.detail,
        ]);
      });
    },
    getVncSettings() {
      this.$api.get("/host/settings/vnc").then((response) => {
        this.novnc_port = response.data.port;
        this.novnc_protocool = response.data.protocool;
        this.novnc_path = response.data.path;
        this.novnc_ip = response.data.ip;
      });
    },
    vncVm(uuid) {
      console.log("vnc vm with uuid", uuid);
      const novnc_url =
        this.novnc_protocool +
        "://" +
        this.novnc_ip +
        ":" +
        this.novnc_port +
        "/" +
        this.novnc_path +
        "?autoconnect=true&?reconnect=true&?resize=scale&?path=?token=" +
        uuid;
      window.open(novnc_url, "_blank");
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
          this.rows = data.data;
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

<style lang="scss">
.disable-focus-helper {
  .q-focus-helper {
    opacity: 0 !important;
  }
}
</style>
