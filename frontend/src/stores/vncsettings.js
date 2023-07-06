import { defineStore } from "pinia";
import { api } from "boot/axios";

export const useVncSettingsStore = defineStore("vncsettings", {
  state: () => ({
    vnc_port: null,
    vnc_protocool: null,
    vnc_path: null,
    vnc_ip: null,
  }),

  getters: {
    getVncSettings() {
      if (
        this.vnc_port == null ||
        this.vnc_protocool == null ||
        this.vnc_path == null ||
        this.vnc_ip == null
      ) {
        if (localStorage.getItem("vnc_settings") != null) {
          const vnc_settings = JSON.parse(localStorage.getItem("vnc_settings"));
          this.vnc_port = vnc_settings.port;
          this.vnc_protocool = vnc_settings.protocool;
          this.vnc_path = vnc_settings.path;
          this.vnc_ip = vnc_settings.ip;
        }
        this.getVncSettingsApi();
      }
      return {
        port: this.vnc_port,
        protocool: this.vnc_protocool,
        path: this.vnc_path,
        ip: this.vnc_ip,
      };
    },
  },

  actions: {
    getVncSettingsApi() {
      console.log("getVncSettingsApi");
      api.get("/host/settings/vnc").then((response) => {
        this.vnc_port = response.data.port;
        this.vnc_protocool = response.data.protocool;
        this.vnc_path = response.data.path;
        this.vnc_ip = response.data.ip;
        localStorage.setItem("vnc_settings", JSON.stringify(response.data))
      });
    },
  },
});
