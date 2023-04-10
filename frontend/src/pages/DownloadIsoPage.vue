<template>
  <q-page padding>
    <q-card>
      <q-card-section>
        <div class="text-h6">Download ISO</div>
      </q-card-section>
      <q-separator color="transparent" dark inset />
      <q-card-section>
        <q-input v-model="url" label="URL" />
      </q-card-section>
      <q-card-section>
        <q-input v-model="fileName" label="File Name" />
      </q-card-section>
      <q-card-section>
        <StoragePoolList ref="storagePool" />
      </q-card-section>
      <q-card-section>
        <q-btn color="primary" label="Download" @click="downloadIso()" />
      </q-card-section>
      <q-card-section>
        <q-linear-progress
          rounded
          v-show="showProgressBar"
          :value="progress"
          class="q-mt-md"
          animation-speed="100"
          size="25px"
          ><div class="absolute-full flex flex-center">
            <q-badge
              color="white"
              text-color="accent"
              :label="Math.round(progress * 100)"
            />
          </div>
        </q-linear-progress>
      </q-card-section>
    </q-card>
    <ErrorDialog ref="errorDialog" />
  </q-page>
</template>

<script>
import StoragePoolList from "src/components/StoragePoolList.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import { ref } from "vue";

export default {
  data() {
    return {
      url: "https://geo.mirror.pkgbuild.com/iso/2023.02.01/archlinux-x86_64.iso",
      fileName: "archlinux-x86_64.iso",
      showProgressBar: false,
      progress: 0,
    };
  },
  components: {
    StoragePoolList,
    ErrorDialog,
  },
  methods: {
    downloadIso() {
      const jwt_token = localStorage.getItem("jwt-token");
      this.ws = new WebSocket(
        this.$WS_ENDPOINT + "/downloadiso?token=" + jwt_token
      );
      this.ws.onopen = () => {
        this.ws.send(
          JSON.stringify({
            url: this.url,
            fileName: this.fileName,
            storagePool: this.$refs.storagePool.getSelectedPool(),
          })
        );
      };
      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        console.log("new data from ws", data);
        if (data.event == "downloadISOError") {
          this.$refs.errorDialog.show("Error Downloading ISO", [data.message]);
        } else if (data.event == "downloadISOProgress") {
          this.showProgressBar = true;
          this.progress = data.percentage / 100;
        } else if (data.event == "downloadISOComplete") {
          this.showProgressBar = false;
          this.progress = 0;
          this.$refs.errorDialog.show("ISO Download Complete", data.message);
        } else if (data.event == "auth_error") {
          localStorage.setItem("jwt-token", "");
          this.$router.push({ path: "/login" });
        }
      };
    },
  },
};
</script>
