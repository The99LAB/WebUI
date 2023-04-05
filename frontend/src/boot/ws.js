import { boot } from "quasar/wrappers";

var WS_ENDPOINT = "";
if (process.env.NODE_ENV === "development") {
  WS_ENDPOINT = process.env.WEBSOCKET_ENDPOINT_DEV;
} else if (process.env.NODE_ENV === "production") {
  WS_ENDPOINT =
    "ws://" +
    window.location.hostname +
    ":" +
    process.env.PRODUCTION_BACKEND_PORT;
}

export default boot(({ app }) => {
  app.config.globalProperties.$WS_ENDPOINT = WS_ENDPOINT;
});
