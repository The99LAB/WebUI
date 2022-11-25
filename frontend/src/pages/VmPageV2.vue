<template>
  <q-page padding>
    <h4>Vm Manager V2</h4>
    <q-btn color="primary" label="Get Results" @click="getVmResults" />
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
              <q-btn class="q-ma-sm" color="primary" icon="mdi-play" label="Start" @click="startVm(props.row.uuid)" />
              <q-btn class="q-ma-sm" color="primary" icon="mdi-stop" label="Stop" @click="stopVm(props.row.uuid)" />
              <q-btn class="q-ma-sm" color="primary" icon="mdi-bomb" label="Force stop"
                @click="forceStopVm(props.row.uuid)" />
            </div>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </q-page>

</template>

<script>
import { ref } from 'vue'
import io from "socket.io-client";
import { api } from 'src/boot/axios'

const selected = ref()

const rows = [
  {
    uuid: "1",
    name: 'Windows 10',
    memory: 2048,
    vcpus: 6,
    state: 'Running'
  },
  {
    uuid: "2",
    name: 'Windows 11',
    memory: 2048,
    vcpus: 4,
    state: 'Running'
  }
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
      selected
    }
  },
  methods: {
    getVmResults() {
      this.socket.emit("vm_results")
    },
    startVm(uuid) {
      console.log("starting vm with uuid", uuid)
      api.post("startvm/" + uuid)
        .then(response => console.log("resoponse from startvm", response))
        .catch(error => {
          console.log("Error starting vm with uuid", uuid, "error", error);
        });
    },
    stopVm(uuid) {
      console.log("stopping vm with uuid", uuid)
    },
    forceStopVm(uuid) {
      console.log("force stopping vm with uuid", uuid)
    }
  },
  created() {
    this.socket = io(process.env.SOCKETIO_ENDPOINT);
  },
  mounted() {
    this.socket.on("vm_results", (msg) => {
      console.log("vm results:", msg)
      this.rows = msg
    })
  }
}
</script>
