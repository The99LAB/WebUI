<template>
  <q-page> 
    <div ref="terminal"></div>
  </q-page>
</template>

<script>
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
import 'xterm/css/xterm.css';
import io from "socket.io-client";

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
      this.socket.emit("pty_input", { input: data });
    });

    this.socket.on("pty_output", (data) => {
      this.term.write(data.output);
    });

    this.socket.on("connect", () => {
      this.fitToscreen();
    });

    this.socket.on("disconnect", () => {
    });

    window.addEventListener("resize", this.debouncedFitToscreen);
  },
  beforeUnmount() {
    window.removeEventListener("resize", this.debouncedFitToscreen);
  },
  created() {
    this.socket = io(this.$SOCKETIO_ENDPOINT + "/pty", {
      transportOptions: {
        polling: {
          extraHeaders: {
            Authorization: `Bearer ${localStorage.getItem("jwt-token")}`,
          },
        },
      },
    });
    this.socket.emit("pty_input", { input: "\n" });
  },
  unmounted() {
    this.socket.off("pty_output");
    this.socket.off("connect");
    this.socket.off("disconnect");
    this.socket.disconnect();
  },
  methods: {
    fitToscreen() {
      this.fit.fit();
      const dims = { cols: this.term.cols, rows: this.term.rows };
      this.socket.emit("resize", dims);
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