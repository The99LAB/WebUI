<template>
  <q-select
    label="Virtual machine"
    v-model="selectedVm"
    :options="vmList"
    option-label="name"
    @update:model-value="alertVmSelected"
  >
    <template v-slot:option="scope">
      <q-item v-bind="scope.itemProps">
        <q-item-section>
          <q-item-label>{{ scope.opt.name }}</q-item-label>
        </q-item-section>
      </q-item>
    </template>
  </q-select>
  <ErrorDialog ref="errorDialog" />
</template>
<script>
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      vmList: [],
      selectedVm: null,
    };
  },
  emits: ["vm-selected"],
  components: {
    ErrorDialog,
  },

  methods: {
    updateVms() {
      this.$api
        .get("/vm-manager/all")
        .then((response) => {
          this.vmList = response.data;
          if (this.vmList.length > 0 && this.selectedVm == null) {
            this.selectedVm = this.vmList[0];
            this.alertVmSelected();
          }
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting VM list", [
            error.response.data.detail,
          ]);
        });
    },
    alertVmSelected() {
      this.$emit("vm-selected", this.selectedVm);
    },
    getSelectedVm() {
      return this.selectedVm;
    },
  },
  mounted() {
    this.updateVms();
  },
};
</script>
