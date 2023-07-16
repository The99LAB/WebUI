import { route } from "quasar/wrappers";
import {
  createRouter,
  createMemoryHistory,
  createWebHistory,
  createWebHashHistory,
} from "vue-router";
import routes from "./routes";
import jwtDecode from "jwt-decode";
import { useHostnameStore } from "src/stores/hostname.js";

function isTokenExpired(token) {
  if (token == null || token == undefined || token == "") {
    return true;
  }
  const decoded = jwtDecode(token);
  const currentTime = Date.now() / 1000;
  return decoded.exp < currentTime;
}

/*
 * If not building with SSR mode, you can
 * directly export the Router instantiation;
 *
 * The function below can be async too; either use
 * async/await or return a Promise which resolves
 * with the Router instance.
 */

export default route(function (/* { store, ssrContext } */) {
  const createHistory = process.env.SERVER
    ? createMemoryHistory
    : process.env.VUE_ROUTER_MODE === "history"
    ? createWebHistory
    : createWebHashHistory;

  const Router = createRouter({
    scrollBehavior: () => ({ left: 0, top: 0 }),
    routes: process.env.NODE_ENV === 'production' ? routes.filter(route => !route.devOnly) : routes,

    // Leave this as is and make changes in quasar.conf.js instead!
    // quasar.conf.js -> build -> vueRouterMode
    // quasar.conf.js -> build -> publicPath
    history: createHistory(process.env.VUE_ROUTER_BASE),
  });

  Router.afterEach((to, from) => {
    const hostnameStore = useHostnameStore();
    const hostname = hostnameStore.getHostname;

    if (hostname == null) {
      document.title = to.meta.title;
    } else {
      document.title = hostname + " - " + to.meta.title;
    }
  });

  // // check if user is logged in
  Router.beforeEach((to, from, next) => {
    var token = localStorage.getItem("jwt-token");
    const tokenIsExpired = isTokenExpired(token);

    if (token == "" || token == null || token == undefined || tokenIsExpired) {
      localStorage.removeItem("jwt-token");
      if (to.path == "/login") {
        next();
      } else {
        next("/login");
      }
    } else {
      next();
    }
  });

  return Router;
});
