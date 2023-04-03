<template>
  <q-page> <div style="width: 100%; height: 100%" ref="terminal"></div></q-page>
</template>

<script>
import { Terminal } from "xterm";
import { FitAddon } from "xterm-addon-fit";
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

    // https://github.com/xtermjs/xterm.js/issues/2941
    this.fit = new FitAddon();
    this.term.loadAddon(this.fit);

    this.term.open(this.$refs.terminal);
    this.fit.fit();
    this.term.resize(15, 50);
    console.log(`size: ${this.term.cols} columns, ${this.term.rows} rows`);
    this.fit.fit();

    this.term.onData((data) => {
      console.log("browser terminal received new data:", data);
      this.socket.emit("pty_input", { input: data });
    });

    this.socket.on("pty_output", (data) => {
      console.log("new output received from server:", data.output);
      this.term.write(data.output);
    });

    this.socket.on("connect", () => {
      this.fitToscreen();
      console.log("connected to server");
    });

    this.socket.on("disconnect", () => {
      console.log("disconnected from server");
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
      console.log("sending new dimensions to server's pty", dims);
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

<style>
@import url("https://unpkg.com/xterm@5.1.0/css/xterm.css");
</style>
