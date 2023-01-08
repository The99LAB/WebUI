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
  </q-page>
</template>

<script>
export default {
  data() {
    return {
      cpu_progress: 0,
      cpu_progress_text: "",
      mem_progress: 0,
      mem_progress_text: ""
    }
  },
  mounted() {
    this.$socket.emit("get_cpu_overall_usage")
    this.$socket.emit("get_mem_usage")

    this.cpuinterval = setInterval(() => {
      this.$socket.emit("get_cpu_overall_usage")
    }, 1000)

    this.meminterval = setInterval(() => {
      this.$socket.emit("get_mem_usage")
    }, 1000)

    this.$socket.on("cpu_overall_usage", (msg) => {
      this.cpu_progress = msg
      this.cpu_progress_text = msg + "%"
    })
    this.$socket.on("mem_usage", (msg) => {
      this.mem_progress = msg
      this.mem_progress_text = msg + "%"
    })
  },
  beforeUnmount() {
    clearInterval(this.cpuinterval)
    clearInterval(this.meminterval)
  },
}
</script>

