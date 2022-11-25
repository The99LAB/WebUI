<template>
  <q-page padding>
    <q-btn color="primary" label="Get Results" @click="getVmResults" />
    <h4>Vm Manager</h4>
    <q-table :rows="rows" :columns="columns" row-key="name" separator="none" hide-pagination @row-click="rowClick" />

  </q-page>

</template>

<script>
import io from "socket.io-client";
const columns = [
  {
    name: 'name',
    required: true,
    label: 'Name',
    align: 'left',
    field: 'name',
    sortable: true
  },
  {
    name: 'memory',
    required: true,
    label: 'Memory',
    align: 'left',
    field: 'memory',
    sortable: true
  },
  {
    name: 'vcpus',
    required: true,
    label: 'Cpus',
    align: 'left',
    field: 'vcpus',
    sortable: true
  },
  {
    name: 'state',
    required: false,
    label: 'State',
    align: 'left',
    field: 'state',
    sortable: true
  },
]

const rows = [
  {
    name: 'Windows 10',
    uuid: "SOME_UUID",
    memory: 2048,
    vcpus: 6,
    state: "Running"
  },
]
export default {
  data() {
    return {
      columns,
      rows
    }
  },
  methods: {
    getVmResults() {
      this.socket.emit("vm_results")
    },
    rowClick(event, row) {
      // Here you can navigato to where ever you have to
      // this.$router.push('home')
      console.log(row);
    }
  },
  created() {
    this.socket = io(process.env.SOCKETIO_ENDPOINT);
  },
  mounted() {
    this.socket.on("vm_results", (msg) => {
      console.log("vm results:", msg)
    })
  }
}
</script>
