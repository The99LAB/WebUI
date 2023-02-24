import { boot } from "quasar/wrappers";
import axios from "axios";

// Be careful when using SSR for cross-request state pollution
// due to creating a Singleton instance here;
// If any client changes this (global) instance, it might be a
// good idea to move this instance creation inside of the
// "export default () => {}" function below (which runs individually
// for each client)
var API_ENDPOINT = "";
if (process.env.NODE_ENV === "development") {
  API_ENDPOINT = process.env.API_ENDPOINT;
} else if (process.env.NODE_ENV === "production") {
  API_ENDPOINT =
    window.location.protocol +
    "//" +
    window.location.hostname +
    ":" +
    process.env.PRODUCTION_BACKEND_PORT +
    "/api";
}

const api = axios.create({ baseURL: API_ENDPOINT });

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("jwt-token");
  if (token) {
    config.headers["Authorization"] = "Bearer " + token;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response.status === 401) {
      localStorage.removeItem("jwt-token");

      // if current page is not login page, reload page, which will redirect to login page
      if (!window.location.href.endsWith("/login")) {
        window.location.reload();
      }
    }
    return Promise.reject(error);
  }
);

export default boot(({ app }) => {
  // for use inside Vue files (Options API) through this.$axios and this.$api

  app.config.globalProperties.$axios = axios;
  // ^ ^ ^ this will allow you to use this.$axios (for Vue Options API form)
  //       so you won't necessarily have to import axios in each vue file

  app.config.globalProperties.$api = api;
  // ^ ^ ^ this will allow you to use this.$api (for Vue Options API form)
  //       so you can easily perform requests against your app's API
});

export { api };
