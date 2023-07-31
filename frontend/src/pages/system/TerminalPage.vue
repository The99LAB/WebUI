<template>
  <q-page id="page">
    <div ref="terminal"></div>
  </q-page>
</template>

<script>
import { Terminal } from "xterm";
import "xterm/css/xterm.css";

export default {
  data() {
    return {
      socket: null,
      term: null,
    };
  },
  mounted() {
    this.term = new Terminal({
      cursorBlink: true,
      macOptionIsMeta: true,
    });
    this.term.open(this.$refs.terminal);
    this.term.onData((data) => {
      this.socket.send(JSON.stringify({ type: "input", input: data }));
    });
    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type == "pty_output") {
        this.term.write(data.output);
      } else if (data.event == "auth_error") {
        localStorage.setItem("jwt-token", "");
        this.$router.push({ path: "/login" });
      }
    };
  },
  unmounted() {
    this.socket.close();
  },
  created() {
    this.connectWebSocket();
  },
  methods: {
    connectWebSocket() {
      const jwt_token = localStorage.getItem("jwt-token");
      this.socket = new WebSocket(this.$WS_ENDPOINT + "/terminal?token=" + jwt_token);
      this.socket.onopen = (event) => {
        this.fitTerminal();
      };
    },
    fitTerminal() {
      // lookup qpage by id
      const qPage = document.getElementById("page");
      // get the available width and height of the page
      const availableWidth = qPage.clientWidth;
      const availableHeight = qPage.clientHeight;
      // get the height and width of a row in pixels
      const rowHeight = this.term._core._renderService._charSizeService.height;
      const rowWidth = this.term._core._renderService._charSizeService.width;
      // calculate rows and cols depending on row height and width
      const rows = Math.floor(availableHeight / rowHeight );
      const cols = Math.floor(availableWidth / rowWidth);
      // resize the terminal and send the new dimensions to the server
      this.term.resize(cols, rows);
      this.socket.send(JSON.stringify({ type: "resize", dims: { cols: this.term.cols, rows: this.term.rows} }));
    }
  },
};
</script>
<style lang="scss" scoped>
#page {
  background-color: black;
}
</style>