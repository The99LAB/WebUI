import { boot } from "quasar/wrappers";

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

export default boot(({ app }) => {
  app.config.globalProperties.$SOCKETIO_ENDPOINT = SOCKETIO_ENDPOINT;
});