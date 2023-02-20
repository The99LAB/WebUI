<template>
    <q-select
      label="PCI Device"
      v-model="selectedPciDevice"
      :options="pciDevicesList"
      option-label="label"
    >
        <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps">
            <q-item-section>
                <q-item-label>{{ scope.opt.label }}</q-item-label>
            </q-item-section>
            </q-item>
        </template>
    </q-select>
    <ErrorDialog ref="errorDialog" />
</template>
<script>
import ErrorDialog from 'src/components/ErrorDialog.vue';

export default {
data() {
    return {
    pciDevicesList: [],
    selectedPciDevice: null,
    };
},
components: {
    ErrorDialog,
},
methods: {
    updatePciDevices() {
    this.$api
        .get("/host/system-devices/pcie")
        .then((response) => {
        this.pciDevicesList = response.data;
        if (this.pciDevicesList.length > 0) {
            this.selectedPciDevice = this.pciDevicesList[0];
        }
        })
        .catch((error) => {
        this.$refs.errorDialog.show("Error getting PCI devices list", [
            error,
        ]);
        });
    },
    getSelectedPciDevice() {
    return this.selectedPciDevice;
    },
},
mounted() {
    this.updatePciDevices();
},
};
</script>