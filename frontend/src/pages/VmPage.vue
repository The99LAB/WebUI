<template>
  <q-page padding>
    <div class="row">
      <q-space />
      <q-btn class="q-ma-sm" color="primary" icon="mdi-plus" label="Create VM" @click="createVm()" />
    </div>
    <q-table :rows="rows" :columns="columns" row-key="uuid" separator="none" hide-pagination>
      <template #body="props">
        <q-tr :props="props">
          <q-td key="name" :props="props">
            <q-btn flat round :icon="props.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              @click="props.expand = !props.expand" no-caps :label=props.row.name
              class="text-weight-regular text-body2" />
          </q-td>
          <q-td key="state" :props="props" class="text-weight-regular text-body2">
            {{ props.row.state }}
          </q-td>
          <q-td key="memory" :props="props" class="text-weight-regular text-body2">
            {{ props.row.memory }}
          </q-td>
          <q-td key="vcpus" :props="props" class="text-weight-regular text-body2">
            {{ props.row.vcpus }}
          </q-td>
        </q-tr>

        <q-tr v-show="props.expand" :props="props">
          <q-td colspan="100%">
            <div>
              {{ props.row.uuid }}
            </div>
            <div>
              <q-btn class="q-ma-sm" color="primary" icon="mdi-play" label="Start" v-if="props.row.state != 'Running'" @click="startVm(props.row.uuid)" />
              <q-btn class="q-ma-sm" color="primary" icon="mdi-stop" label="Stop" v-if="props.row.state == 'Running'" @click="stopVm(props.row.uuid)"  />
              <q-btn class="q-ma-sm" color="primary" icon="mdi-bomb" label="Force stop" v-if="props.row.state == 'Running'" @click="forceStopVm(props.row.uuid)" />
              <q-btn  class="q-ma-sm" color="primary" icon="mdi-eye" label="VNC" v-if="props.row.VNC && props.row.state=='Running'" @click="vncVm(props.row.uuid)"/>
              <q-btn class="q-ma-sm" color="primary" icon="mdi-pencil" label="Edit" v-if="props.row.state == 'Shutdown'" @click="editVm(props.row.uuid)"/>
            </div>
          </q-td>
        </q-tr>

      </template>
    </q-table>
    <ErrorDialog ref="errorDialog"></ErrorDialog>
    <CreateVm ref="createVm"></CreateVm>
  </q-page>
</template>

<script>
import { ref } from 'vue'
import io from "socket.io-client";
import { api } from 'src/boot/axios'
import ErrorDialog from 'src/components/ErrorDialog.vue'
import CreateVm from 'src/components/CreateVm.vue'

const selected = ref()

const rows = [
]

const columns = [
  { label: 'Name', field: 'name', name: 'name', align: 'left' },
  { label: 'State', field: 'state', name: 'state', align: 'left' },
  { label: 'Memory', field: 'memory', name: 'memory', align: 'left' },
  { label: 'Cpus', field: 'vcpus', name: 'vcpus', align: 'left' }
]

export default {
  data() {
    return {
      rows,
      columns,
      selected,
    }
  },
  components: {
    ErrorDialog,
    CreateVm,
  },
  methods: {
    startVm(uuid) {
      console.log("starting vm with uuid", uuid)
      api.post("vm-manager/" + uuid + "/start")
        .catch(error => {
          this.$refs.errorDialog.show("Error starting VM", ["vm uuid: " + uuid, "Error: " + error])
        });
    },
    stopVm(uuid) {
      console.log("stopping vm with uuid", uuid)
      api.post("vm-manager/" + uuid+ "/stop")
        .catch(error => {
          this.$refs.errorDialog.show("Error stopping VM", ["vm uuid: " + uuid, "Error: " + error])
        });
    },
    forceStopVm(uuid) {
      console.log("force stopping vm with uuid", uuid)
      api.post("vm-manager/" + uuid + "/forcestop")
        .then(response => console.log("resoponse from forcestopvm", response))
        .catch(error => {
          this.$refs.errorDialog.show("Error force stopping VM", ["vm uuid: " + uuid, "Error: " + error])
        });
    },
    vncVm(uuid) {
      console.log("vnc vm with uuid", uuid)
      // open vnc in new tab
      window.open(process.env.VNC_ENDPOINT_PROTOCOOL + "://" + window.location.hostname + ":"+ process.env.VNC_ENDPOINT_PORT + "/vnc.html?autoconnect=true&?resize=scale&?path=?token=" + uuid, "_blank")
    },
    editVm(uuid) {
      console.log("edit vm with uuid", uuid)
    },
    createVm() {
      this.$refs.createVm.show()
    }
  },
  created() {
    this.socket = io(process.env.SOCKETIO_ENDPOINT);
  },
  mounted() {
    this.socket.emit("vm_results")
    this.vmresultInterval = setInterval(() => {
      this.socket.emit("vm_results")
    }, 1000)
    this.socket.on("vm_results", (msg) => {
      console.log("vm results:", msg)
      this.rows = msg
    })
    this.socket.on("connect_error", (msg) => {
      this.$refs.errorDialog.show("Connection Error", ["Could not connect to the backend server.", msg])
    })
  }
}
</script>
