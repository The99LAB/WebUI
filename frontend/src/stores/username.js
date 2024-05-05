import { defineStore } from "pinia";

export const useUsernameStore = defineStore("username", {
  state: () => ({
    username: null,
  }),

  getters: {
    getUsername() {
      if (this.username == null) {
        if (localStorage.getItem("username") != null) {
          this.username = localStorage.getItem("username");
        }
      }
      return this.username;
    },
  },

  actions: {
    setUsername(username) {
      this.username = username;
      localStorage.setItem("username", username);
    },
    clearUsername() {
      this.username = null;
      localStorage.removeItem("username");
    },
  },
});
