<template>
  <q-page padding>
    <h1>Hotplug USB</h1>
    <HostUsbDevicesList ref="usbDevicesList" />
    <q-btn label="Hotplug USB" color="primary" @click="hotplugUsb" />
  </q-page>
</template>
<script>
import HostUsbDevicesList from "src/components/HostUsbDevicesList.vue";

export default {
  data() {
    return {};
  },
  methods: {
    hotplugUsb() {
      console.log(this.$refs.usbDevicesList.getSelectedUsbDevice()["name"]);
      console.log(this.$refs.usbDevicesList.getSelectedUsbDeviceName());
      console.log(this.$refs.usbDevicesList.getSelectedUsbVendorId());
      console.log(this.$refs.usbDevicesList.getSelectedUsbProductId());
    },
  },
  mounted() {},
  components: {
    HostUsbDevicesList,
  },
};
</script>
