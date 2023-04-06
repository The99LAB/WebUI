<template>
  <q-dialog v-model="layout">
    <q-card>
      <q-card-section>
        <div class="row">
          <div class="text-h6">Edit Host Name</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        <q-form>
          <div class="row">
            <div class="col">
              <q-input label="Name" v-model="hostName" />
            </div>
          </div>
        </q-form>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Finish" @click="editHostName()" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <errorDialog ref="errorDialog" />
</template>

<script>
import { ref } from "vue";
import errorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      hostName: "",
      layout: ref(false),
    };
  },
  components: {
    errorDialog,
  },
  emits: ["hostname-edit-finished"],
  methods: {
    show(name = null) {
      this.layout = true;
      if (name != null) {
        this.hostName = name;
      } else {
        this.getHostName();
      }
    },
    getHostName() {
      this.$api
        .get("/host/system-info/hostname")
        .then((response) => {
          this.hostName = response.data.hostname;
        })
        .catch((error) => {
          console.log("Error getting hostname: " + error.response.data.detail);
        });
    },
    editHostName() {
      const formData = new FormData();
      formData.append("hostname", this.hostName);
      this.$api
        .post("/host/system-info/hostname", formData)
        .then((this.layout = false), this.$emit("hostname-edit-finished"))
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing hostname", [
            error.response.data.detail,
          ]);
        });
    },
  },
  mounted() {},
};
</script>
