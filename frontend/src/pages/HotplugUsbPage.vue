<template>
  <q-page padding>
    <q-separator color="transparent" spaced dark />
    <HostUsbDevicesList ref="usbDevicesList" />
    <VmList ref="vmList" />
    <q-separator color="transparent" spaced />
    <div class="row">
      <q-btn label="Add device to vm" color="primary" @click="addHotplugUsb" />
      <q-separator color="transparent" spaced vertical dark />
      <q-btn
        label="Remove device from vm"
        color="primary"
        @click="removeHotplugUsb"
      />
    </div>
    <ErrorDialog ref="errorDialog" />
  </q-page>
</template>
<script>
import HostUsbDevicesList from "src/components/HostUsbDevicesList.vue";
import VmList from "src/components/VmList.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {};
  },
  methods: {
    addHotplugUsb() {
      if (this.$refs.vmList.getSelectedVm() == null) {
        this.$refs.errorDialog.show("Error adding USB device to VM", [
          "No VM selected",
        ]);
        return;
      }
      if (
        this.$refs.usbDevicesList.getSelectedUsbVendorId() == null ||
        this.$refs.usbDevicesList.getSelectedUsbProductId() == null
      ) {
        this.$refs.errorDialog.show("Error adding USB device to VM", [
          "No USB device selected",
        ]);
        return;
      }
      this.$api
        .post(
          "/vm-manager/" +
            this.$refs.vmList.getSelectedVm()["uuid"] +
            "/edit-usbhotplug-add",
          {
            vendorid: this.$refs.usbDevicesList.getSelectedUsbVendorId(),
            productid: this.$refs.usbDevicesList.getSelectedUsbProductId(),
          }
        )
        .catch((error) => {
          this.$refs.errorDialog.show("Error adding USB device to VM", [
            error.response.data,
          ]);
        });
    },
    removeHotplugUsb() {
      if (this.$refs.vmList.getSelectedVm() == null) {
        this.$refs.errorDialog.show("Error removing USB device from VM", [
          "No VM selected",
        ]);
        return;
      }
      if (
        this.$refs.usbDevicesList.getSelectedUsbVendorId() == null ||
        this.$refs.usbDevicesList.getSelectedUsbProductId() == null
      ) {
        this.$refs.errorDialog.show("Error removing USB device from VM", [
          "No USB device selected",
        ]);
        return;
      }
      this.$api
        .post(
          "/vm-manager/" +
            this.$refs.vmList.getSelectedVm()["uuid"] +
            "/edit-usbhotplug-delete",
          {
            vendorid: this.$refs.usbDevicesList.getSelectedUsbVendorId(),
            productid: this.$refs.usbDevicesList.getSelectedUsbProductId(),
          }
        )
        .catch((error) => {
          this.$refs.errorDialog.show("Error removing USB device from VM", [
            error.response.data,
          ]);
        });
    },
  },
  mounted() {
    this.hostUsbDevicesInterval = setInterval(() => {
      this.$refs.usbDevicesList.updateUsbDevices();
    }, 1000);
    this.vmInterval = setInterval(() => {
      this.$refs.vmList.updateVms();
    }, 1000);
  },
  beforeUnmount() {
    clearInterval(this.hostUsbDevicesInterval);
    clearInterval(this.vmInterval);
  },
  components: {
    HostUsbDevicesList,
    VmList,
    ErrorDialog,
  },
};
</script>
