<template>
  <q-page padding>
    <div class="row justify-evenly">
      <div style="text-align:center;">
        <p>CPU</p>
        <q-circular-progress show-value class="text-light-blue q-ma-md" size="150px" color="light-blue"
          :value="cpu_progress">{{ cpu_progress_text }}</q-circular-progress>
      </div>

      <div style="text-align:center;">
        <p>Memory</p>
        <q-circular-progress show-value class="text-light-blue q-ma-md" size="150px" color="light-blue"
          :value="mem_progress"> {{ mem_progress_text }}
        </q-circular-progress>
      </div>
    </div>
    <ErrorDialog ref="errorDialog"/>
  </q-page>
</template>

<script>
import io from "socket.io-client";
import ErrorDialog from 'src/components/ErrorDialog.vue'

export default {
  data() {
    return {
      cpu_progress: 0,
      cpu_progress_text: "",
      mem_progress: 0,
      mem_progress_text: ""
    }
  },
  components: {
    ErrorDialog,
  },
  created() {
    this.socket = io(process.env.SOCKETIO_ENDPOINT);
  },
  mounted() {
    this.socket.on("connect", () => {
      this.socket.emit("cpuoverall_usage")
      this.socket.emit("mem_usage")

      this.cpuinterval = setInterval(() => {
        this.socket.emit("cpuoverall_usage")
      }, 1000)

      this.meminterval = setInterval(() => {
        this.socket.emit("mem_usage")
      }, 1000)
    })
    this.socket.on("cpuoverall_usage", (msg) => {
      this.cpu_progress = msg
      this.cpu_progress_text = msg + "%"
    })
    this.socket.on("mem_usage", (msg) => {
      this.mem_progress = msg
      this.mem_progress_text = msg + "%"
    })
    this.socket.on("connect_error", (msg) => {
      this.$refs.errorDialog.show("Connection Error", ["Could not connect to the backend server.", msg])
    })
  },
  beforeUnmount() {
    clearInterval(this.cpuinterval)
    clearInterval(this.meminterval)
    this.socket.disconnect()
  },
}
</script>

