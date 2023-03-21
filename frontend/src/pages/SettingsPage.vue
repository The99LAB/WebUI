<template>
  <q-page padding>
    <p class="text-h6">Settings</p>
    <p class="text-subtitle2">OVMF Paths</p>
    <div v-for="ovmfPath in ovmfPaths" :key="ovmfPath" class="row">
      <div class="col">
        <p>{{ ovmfPath.name }}</p>
      </div>
      <div class="col">
        <p>{{ ovmfPath.path }}</p>
      </div>
    </div>
    <div class="row">
      <q-btn color="primary" icon="mdi-plus" label="Add" />
      <q-separator spaced vertical dark />
      <q-btn color="primary" icon="mdi-check" label="Apply" />
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
        <q-input v-model="novnc_port" >
          <template v-slot:append>
            <q-btn
              round
              dense
              flat
              icon="mdi-check"
              title="Apply"
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
        <q-input v-model="novnc_protocool" >
          <template v-slot:append>
            <q-btn
              round
              dense
              flat
              icon="mdi-check"
              title="Apply"
            />
          </template>
        </q-input>
      </div>
    </div>
    <q-separator spaced="xl" />
    <p class="text-subtitle2">QEMU settings</p>
    <div class="row">
      <div class="col">
        <p>Path</p>
      </div>
      <div class="col">
        <q-input v-model="qemupath"> 
          <template v-slot:append>
            <q-btn
              round
              dense
              flat
              icon="mdi-check"
              title="Apply"
            />
          </template>
        </q-input>
      </div>
    </div>
  </q-page>
</template>

<script>
import { ref } from "vue";

export default {
  data() {
    return {
      ovmfPaths: ref(null),
      novnc_path: ref(null),
      novnc_port: ref(null),
      novnc_protocool: ref(null),
      qemupath: ref(null),
    };
  },
  methods: {
    getData(){
      this.$api.get("/host/settings")
      .then((response) => {
        this.ovmfPaths = response.data.OVMF_paths
        this.novnc_path = response.data.novnc_path
        this.novnc_port = response.data.novnc_port
        this.novnc_protocool = response.data.novnc_protocool
        this.qemupath = response.data.QEMU_path
      })
      .catch((error) => {
        console.log(error)
      });
    }
  },
  mounted() {
    this.getData()
  }
};
</script>
