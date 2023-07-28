<template>
  <q-page padding>
    <q-card>
      <q-card-section>
        <div class="text-h6 text-center">System</div>
        <q-separator color="transparent" spaced="xs" />
        <div v-if="!loadingSystem">
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
        <q-inner-loading :showing="loadingSystem" />
      </q-card-section>
      <q-card-section>
        <div class="text-h6 text-center">WebUI</div>
        <q-separator color="transparent" spaced="xs" />
        <div class="row items-start">
          <p class="col text-right q-mr-sm text-weight-bold">Version:</p>
          <p class="col">1.2</p>
        </div>
      </q-card-section>
      <q-card-section>
        <div class="text-h6 text-center">Docker</div>
        <q-separator color="transparent" spaced="xs" />
        <div v-if="!loadingDocker">
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Version:</p>
            <p class="col">{{ dockerInfo.Version }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">API Version:</p>
            <p class="col">{{ dockerInfo.ApiVersion }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Git Commit:</p>
            <p class="col">{{ dockerInfo.GitCommit }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Go Version:</p>
            <p class="col">{{ dockerInfo.GoVersion }}</p>
          </div>
          <div class="row items-start">
            <p class="col text-right q-mr-sm text-weight-bold">Platform:</p>
            <p class="col" v-if="dockerInfo.Platform">
              {{ dockerInfo.Platform.Name }}
            </p>
          </div>
        </div>
        <q-inner-loading :showing="loadingDocker" />
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
    return {
      systemInfo: {},
      dockerInfo: {},
      loadingSystem: ref(false),
      loadingDocker: ref(false),
    };
  },
  components: {
    editHostName,
    errorDialog,
    ToolTip,
  },
  methods: {
    getSystemInfo() {
      this.loadingSystem = true;
      this.$api
        .get("/host/system-info/all")
        .then((response) => {
          this.systemInfo = response.data;
          this.loadingSystem = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting system info", [
            error.response.data.detail,
          ]);
        });
    },
    getDockerInfo() {
      this.loadingDocker = true;
      this.$api
        .get("docker-manager/info")
        .then((response) => {
          this.dockerInfo = response.data;
          this.loadingDocker = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting docker info", [
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
    this.getDockerInfo();
  },
};
</script>
