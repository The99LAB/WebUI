<template>
  <q-page padding>
    <p class="text-h6">Settings</p>
    <p class="text-subtitle2">OVMF Paths</p>
    <!-- Replace with table? -->
    <div v-for="ovmf_path in ovmf_paths" :key="ovmf_path" class="row">
      <div class="col">
        <p>{{ ovmf_path.name }}</p>
      </div>
      <div class="col">
        <p>{{ ovmf_path.path }}</p>
      </div>
    </div>
    <div class="row">
      <q-btn color="primary" icon="mdi-plus" label="Add" />
      <q-separator spaced vertical dark />
      <q-btn color="primary" icon="mdi-check" label="Apply" />
      <q-separator spaced vertical dark />
      <q-btn color="primary" icon="mdi-delete" label="Remove" />
    </div>
    <q-separator spaced="xl" />
    <p class="text-subtitle2">NOVNC settings</p>
    <div class="row">
      <div class="col">
        <p>Path</p>
      </div>
      <div class="col">
        <q-input v-model="novnc_path" >
          <template v-slot:append>
            <q-btn
              round
              dense
              flat
              icon="mdi-check"
              title="Apply"
              @click="changeSetting('novnc_path', novnc_path)"
            />
          </template>
        </q-input>
      </div> 
    </div>
    <div class="row">
      <div class="col">
        <p>Port</p>
      </div>
      <div class="col">
        <q-input v-model="novnc_port" type="number">
          <template v-slot:append>
            <q-btn
              round
              dense
              flat
              icon="mdi-check"
              title="Apply"
              @click="changeSetting('novnc_port', novnc_port)"
            /> 
          </template>
        </q-input>
      </div>
    </div>
    <div class="row">
      <div class="col">
        <p>Protocool</p>
      </div>
      <div class="col">
        <q-select
          v-model="novnc_protocool"
          :options="protocool_options"
          label="Protocool">
          <template v-slot:append>
            <q-btn
              round
              dense
              flat
              icon="mdi-check"
              title="Apply"
              @click="changeSetting('novnc_protocool', novnc_protocool)"
            />
          </template>
        </q-select>
      </div>
    </div>
    <q-separator spaced="xl" />
    <p class="text-subtitle2">QEMU settings</p>
    <div class="row">
      <div class="col">
        <p>Path</p>
      </div>
      <div class="col">
        <q-input v-model="qemu_path"> 
          <template v-slot:append>
            <q-btn
              round
              dense
              flat
              icon="mdi-check"
              title="Apply"
              @click="changeSetting('qemu_path', qemu_path)"
            />
          </template>
        </q-input>
      </div>
    </div>
  </q-page>
  <ErrorDialog ref="errorDialog" />
</template>
<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      ovmf_paths: ref(null),
      novnc_path: ref(null),
      novnc_port: ref(null),
      novnc_protocool: ref(null),
      qemu_path: ref(null),
      protocool_options: ["http", "https"],
    };
  },
  components: {
    ErrorDialog,
  },
  methods: {
    getData(){
      this.$api.get("/host/settings")
      .then((response) => {
        this.ovmf_paths = response.data.ovmf_paths
        this.novnc_path = response.data.novnc_path
        this.novnc_port = response.data.novnc_port
        this.novnc_protocool = response.data.novnc_protocool
        this.qemu_path = response.data.qemu_path
      })
      .catch((error) => {
        this.$refs.errorDialog.show("Error getting settings", [error.response.data]);
      });
    },
    changeSetting(setting, value){
      this.$api.post("/host/settings", {
        setting: setting,
        value: value
      })
      .then((response) => {
        this.getData()
      })
      .catch((error) => {
        this.$refs.errorDialog.show("Error changing setting", [error.response.data]);
      });
    }
  },
  mounted() {
    this.getData()
  }
};
</script>
