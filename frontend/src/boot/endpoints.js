import { boot } from "quasar/wrappers";
import io from "socket.io-client";

var SOCKETIO_ENDPOINT = "";
if (process.env.NODE_ENV === "development") {
  SOCKETIO_ENDPOINT = process.env.SOCKETIO_ENDPOINT;
} else if (process.env.NODE_ENV === "production") {
  SOCKETIO_ENDPOINT =
    window.location.protocol +
    "//" +
    window.location.hostname +
    ":" +
    process.env.PRODUCTION_BACKEND_PORT +
    "/api";
}

const socket = io(SOCKETIO_ENDPOINT, {
  transportOptions: {
    polling: {
      extraHeaders: {
        Authorization: "Bearer " + localStorage.getItem("jwt-token"),
      },
    },
  },
});

export default boot(({ app }) => {
  app.config.globalProperties.$socket = socket;
});
