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
</template>
<script>
export default {
  data() {
    return {
        usbDevicesList: [],
        selectedUsbDevice: null,
    };
  },
  methods: {
    updateUsbDevices() {
        this.$api.get("/host/system-devices/usb")
        .then((response) => {
          this.usbDevicesList = response.data;
          console.log("USB devices list: ", response.data)
          if (this.usbDevicesList.length > 0) {
            this.selectedUsbDevice = this.usbDevicesList[0];
          }
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error.response.data);
        });
    },
    getSelectedUsbDeviceName() {
        return this.selectedUsbDevice["name"];
    },
  },
    mounted() {
        this.updateUsbDevices();
    },
};
</script>