<template>
  <q-page padding>
    <q-card>
      <q-inner-loading :showing="loadingVisible"/>
      <q-card-section>
        <div class="text-h6 text-center" v-show="showData">
          System Information
        </div>
      </q-card-section>
      <q-separator color="transparent" dark inset />
      <q-card-section>
        <div v-show="showData">
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Motherboard:</p>
            <p class="col">{{ systemInfo.motherboard }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Processor:</p>
            <p class="col">{{ systemInfo.processor }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Memory:</p>
            <p class="col">{{ systemInfo.memory }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">
              Operating System:
            </p>
            <p class="col">{{ systemInfo.os }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Linux Kernel:</p>
            <p class="col">{{ systemInfo.linuxVersion }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Uptime:</p>
            <p class="col">{{ systemInfo.uptime }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Hostname:</p>
            <p class="col">
              {{ systemInfo.hostname }}
              <q-btn
                round
                icon="edit"
                flat
                text-color="primary"
                size="sm"
                class="q-ml-xs"
                padding="none"
                @click="editHostName()"
              >
                <ToolTip content="Edit Hostname" />
              </q-btn>
            </p>
          </div>
        </div>
      </q-card-section>
    </q-card>
    <editHostName
      ref="editHostNameDialog"
      @hostname-edit-finished="getSystemInfo()"
    />
    <errorDialog ref="errorDialog" />
  </q-page>
</template>

<script>
import editHostName from "src/components/EditHostName.vue";
import errorDialog from "src/components/ErrorDialog.vue";
import ToolTip from "src/components/ToolTip.vue";

import { ref } from "vue";
export default {
  data() {
    const loadingVisible = ref(true);
    const showData = ref(false);
    return {
      systemInfo: {
        motherboard: "",
        processor: "",
        memory: "",
        os: "",
        hostname: "",
        linuxVersion: "",
        uptime: "",
      },
      loadingVisible,
      showData,
    };
  },
  components: {
    editHostName,
    errorDialog,
    ToolTip,
  },
  methods: {
    getSystemInfo() {
      this.$api
        .get("/host/system-info/all")
        .then((response) => {
          this.systemInfo = response.data;
          this.loadingVisible = false;
          this.showData = true;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting system info", [
            error.response.data.detail,
          ]);
        });
    },
    editHostName() {
      this.$refs.editHostNameDialog.show((name = this.hostname));
    },
  },
  mounted() {
    this.getSystemInfo();
  },
};
</script>
