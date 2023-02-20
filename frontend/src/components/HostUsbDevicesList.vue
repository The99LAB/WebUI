<template>
  <q-select
    label="USB Device"
    v-model="selectedUsbDevice"
    :options="usbDevicesList"
    option-label="name"
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
      usbDevicesList: [],
      selectedUsbDevice: null,
    };
  },
  components: {
    ErrorDialog,
  },
  methods: {
    updateUsbDevices() {
      this.$api
        .get("/host/system-devices/usb")
        .then((response) => {
          this.usbDevicesList = response.data;
          if (this.usbDevicesList.length > 0) {
            this.selectedUsbDevice = this.usbDevicesList[0];
          }
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting USB devices list", [error]);
        });
    },
    getSelectedUsbDevice() {
      return this.selectedUsbDevice;
    },
    getSelectedUsbDeviceName() {
      return this.selectedUsbDevice["name"];
    },
    getSelectedUsbVendorId() {
      return this.selectedUsbDevice["vendorid"];
    },
    getSelectedUsbProductId() {
      return this.selectedUsbDevice["productid"];
    },
  },
  mounted() {
    this.updateUsbDevices();
  },
};
</script>
