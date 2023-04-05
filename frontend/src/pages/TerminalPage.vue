<template>
  <q-page>
    <div ref="terminal"></div>
  </q-page>
</template>

<script>
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import "xterm/css/xterm.css";

export default {
  data() {
    return {
      socket: null,
      term: null,
      fit: null,
    };
  },
  mounted() {
    this.term = new Terminal({
      cursorBlink: true,
      macOptionIsMeta: true,
    });

    this.fit = new FitAddon();
    this.term.loadAddon(this.fit);

    this.term.open(this.$refs.terminal);
    this.term.resize(15, 49);
    this.fit.fit();

    this.term.onData((data) => {
      this.socket.send(JSON.stringify({ type: "input", input: data }));
    });

    this.socket.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type == "pty_output") {
        this.term.write(data.output);
      }
    };
    window.addEventListener("resize", this.debouncedFitToscreen);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.debouncedFitToscreen);

  },
  unmounted() {
    this.socket.close()
  },
  created() {
    this.connectWebSocket();
  },

  methods: {
    connectWebSocket() {
      this.socket = new WebSocket(this.$WS_ENDPOINT + "/terminal");
      this.socket.onopen = (event) => {
        this.fitToscreen();
      };
    },
    fitToscreen() {
      this.fit.fit();
      const dims = { cols: this.term.cols, rows: this.term.rows };
      this.socket.send(JSON.stringify({ type: "resize", dims: dims }));
    },
    debounce(func, waitMs) {
      let timeout;
      return function (...args) {
        const context = this;
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(context, args), waitMs);
      };
    },
  },
  computed: {
    debouncedFitToscreen() {
      const waitMs = 50;
      return this.debounce(this.fitToscreen, waitMs);
    },
  },
};
</script>
