<template>
  <q-page padding>
    <q-card>
      <q-inner-loading :showing="loadingVisible">
        <q-spinner-gears size="50px" color="primary" />
      </q-inner-loading>
      <q-card-section>
        <div class="text-h6 text-center" v-show="showData">
          System Information
        </div>
      </q-card-section>
      <q-separator color="transparent" dark inset />
      <q-card-section>
        <div class="row justify-center text-body2" v-show="showData">
          <div class="col text-right q-mr-sm text-weight-bold">
            <p>Motherboard</p>
            <p>Processor</p>
            <p>Memory</p>
            <p>Operating System</p>
            <p>Linux Version</p>
            <p>Host Name</p>
          </div>
          <div class="col text-weight-regular" v-show="showData">
            <p>{{ motherboard }}</p>
            <p>{{ processor }}</p>
            <p>{{ memory }}</p>
            <p>{{ os }}</p>
            <p>{{ linuxVersion }}</p>
            <p>
              {{ hostname
              }}<q-btn
                round
                icon="edit"
                flat
                text-color="primary"
                size="sm"
                padding="none"
                @click="editHostName()"
              ></q-btn>
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

import { ref } from "vue";
export default {
  data() {
    const loadingVisible = ref(true);
    const showData = ref(false);
    return {
      motherboard: "",
      processor: "",
      memory: "",
      os: "",
      hostname: "",
      linuxVersion: "",
      loadingVisible,
      showData,
    };
  },
  components: {
    editHostName,
    errorDialog,
  },
  methods: {
    getSystemInfo() {
      this.$api
        .get("/host/system-info/all")
        .then((response) => {
          this.motherboard = response.data.motherboard;
          this.processor = response.data.processor;
          this.memory = response.data.memory;
          this.os = response.data.os;
          this.hostname = response.data.hostname;
          this.linuxVersion = response.data.linuxVersion;
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
