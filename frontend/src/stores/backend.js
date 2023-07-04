import { defineStore } from "pinia";
import { api } from "boot/axios";
/*
  Stores information from the backend:
  - hostname
  - vnc settings
*/

export const useBackendStore = defineStore("backend", {
  state: () => ({
    hostname: null,
  }),

  getters: {
    getHostname() {
      if (this.hostname == null) {
        this.getHostnameApi();
      }
      return this.hostname;
    },
  },

  actions: {
    getHostnameApi() {
      console.log("getHostnameApi");
      api.get("/no-auth/hostname").then((response) => {
        this.hostname = response.data.hostname;
      });
    },
  },
});
