<template>
  <q-page padding>
    <div class="row justify-evenly">
      <div class="text-center" v-show="!loadingVisible">
        <p>CPU</p>
        <q-circular-progress
          show-value
          class="text-light-blue q-ma-md"
          size="150px"
          color="light-blue"
          :value="cpu_progress"
          >{{ cpu_progress_text }}</q-circular-progress
        >
      </div>
      <div class="text-center" v-show="!loadingVisible">
        <p>Memory</p>
        <q-circular-progress
          show-value
          class="text-light-blue q-ma-md"
          size="150px"
          color="light-blue"
          :value="mem_progress"
        >
          {{ mem_progress_text }}
        </q-circular-progress>
      </div>
    </div>
    <q-inner-loading :showing="loadingVisible">
      <q-spinner-gears size="50px" color="primary" />
    </q-inner-loading>
  </q-page>
</template>

<script>
import io from "socket.io-client";

export default {
  data() {
    return {
      cpu_progress: 0,
      cpu_progress_text: "",
      mem_progress: 0,
      mem_progress_text: "",
      loadingVisible: true,
    };
  },
  created() {
    this.socket = io(this.$SOCKETIO_ENDPOINT, {
      transportOptions: {
        polling: {
          extraHeaders: {
            Authorization: "Bearer " + localStorage.getItem("jwt-token"),
          },
        },
      },
    });
    
  },
  mounted() {
    this.socket.emit("dashboard_data");
    this.dataInterval = setInterval(() => {
      this.socket.emit("dashboard_data");
    }, 1000);
    this.socket.on("cpu_overall", (data) => {
      this.cpu_progress = data;
      this.cpu_progress_text = data + "%";
    });
    this.socket.on("mem_overall", (data) => {
      this.mem_progress = data;
      this.mem_progress_text = data + "%";
      this.loadingVisible = false;
    });
  },
  beforeUnmount() {
    clearInterval(this.dataInterval);
    this.socket.disconnect();
  },
};
</script>
