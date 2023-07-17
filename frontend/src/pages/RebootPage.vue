<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page padding class="row justify-center items-center">
        <q-card>
          <q-linear-progress
            rounded
            :query="true"
            track-color="primary"
            color="secondary"
          />
          <q-card-section class="text-center">
            System is currently {{status}}{{ dotsText }}
          </q-card-section>
          <q-card-section>
            <img
              class="q-px-md"
              src="/src/assets/Server99-logo-full.png"
              alt="Logo"
              style="width: 25em"
            />
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>
<script>
import { ref } from "vue";

export default {
  data() {
    return {
      dots: 0,
      dotsText: ref(""),
      status: "rebooting",
      statusRefreshInterval: 5000,
    };
  },
  mounted() {
    this.dots = setInterval(() => {
      if (this.dots < 3) {
        this.dots++;
      } else {
        this.dots = 0;
      }
      this.dotsText = ".".repeat(this.dots);
    }, 500);
    this.checkSystemStatus();
  },
  methods: {
    checkSystemStatus() {
        this.$api.get("/no-auth/system-status")
        .then((response) => {
            if (response.data === "running") {
                this.$router.push({ name: "login" });
            } else {
                this.status = "rebooting"
                setTimeout(this.checkSystemStatus, this.statusRefreshInterval);
            }
        }).catch((error) => {
            this.status = "offline";
            setTimeout(this.checkSystemStatus, this.statusRefreshInterval);
        });
    }
  }
};
</script>
