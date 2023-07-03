import { defineStore } from 'pinia'
import { api } from 'boot/axios'

export const useHostnameStore = defineStore('hostname', {
  state: () => ({
    hostname: null
  }),

  getters: {
    getHostname() {
      if (this.hostname == null) {
        this.getHostnameApi()
      }
      return this.hostname
    }
  },

  actions: {
    getHostnameApi() {
      console.log("getHostnameApi")
      api
        .get("/no-auth/hostname")
        .then((response) => {
          this.hostname = response.data.hostname;
        })
    }
  }
})
