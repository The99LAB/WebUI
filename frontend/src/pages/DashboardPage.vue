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
  <WsReconnectDialog
    ref="wsReconnectDialog"
    @ws-reconnect="connectWebSocket"
  ></WsReconnectDialog>
</template>

<script>
import WsReconnectDialog from "src/components/WsReconnectDialog.vue";

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
  components: {
    WsReconnectDialog,
  },
  methods: {
    connectWebSocket() {
      const jwt_token = localStorage.getItem("jwt-token");
      this.ws = new WebSocket(
        this.$WS_ENDPOINT + "/dashboard?token=" + jwt_token
      );

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        this.cpu_progress = data.cpu_percent;
        this.cpu_progress_text = data.cpu_percent + "%";
        this.mem_progress = data.mem_percent;
        this.mem_progress_text = data.mem_percent + "%";
        this.loadingVisible = false;
      };

      this.ws.onclose = (event) => {
        this.$refs.wsReconnectDialog.show();
      };
    },
  },
  created() {
    this.connectWebSocket();
  },
  unmounted() {
    this.ws.onclose = () => {};
    this.ws.close();
  },
};
</script>
