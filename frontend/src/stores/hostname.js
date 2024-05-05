import { defineStore } from "pinia";
import { api } from "boot/axios";

export const useHostnameStore = defineStore("hostname", {
  state: () => ({
    hostname: null,
  }),

  getters: {
    getHostname() {
      if (this.hostname == null) {
        if (localStorage.getItem("hostname") != null) {
          this.hostname = localStorage.getItem("hostname");
        } else {
          this.getHostnameApi();
        }
      }
      return this.hostname;
    },
  },

  actions: {
    getHostnameApi() {
      console.log("getHostnameApi");
      api.get("/no-auth/hostname").then((response) => {
        this.hostname = response.data.hostname;
        localStorage.setItem("hostname", this.hostname);
      });
    },
  },
});
