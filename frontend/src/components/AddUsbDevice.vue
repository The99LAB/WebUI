<template>
    <q-dialog v-model="visible">
        <q-card>
            <q-card-section class="row items-center q-pb-none">
                <div class="text-h6">Add USB Device</div>
                <q-space />
                <q-btn icon="close" flat round dense v-close-popup />
            </q-card-section>
            <q-separator spaced="lg" inset />
            <q-card-section class="q-pt-none q-px-xl">
                <HostUsbDevicesList ref="hostUsbDevicesList" />
            </q-card-section>
            <q-card-actions align="right">
                <q-btn flat label="Finish" @click="addUsbDevice()" />
            </q-card-actions>
        </q-card>
    </q-dialog>
    <ErrorDialog ref="errorDialog" />
</template>

<script>
import { ref } from "vue";
import HostUsbDevicesList from "src/components/HostUsbDevicesList.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
    data() {
        return {
            visible: ref(false),
            uuid: null,
        };
    },
    emits: ["usb-device-add-finished"],
    components: {
        HostUsbDevicesList,
        ErrorDialog,
    },
    methods: {
        show(uuid) {
            this.uuid = uuid;
            this.visible = true;
        },
        addUsbDevice() {
            this.$api.post("/vm-manager/" + this.uuid + "/edit-usb-add", {
                    "productid": this.$refs.hostUsbDevicesList.getSelectedUsbProductId(),
                    "vendorid": this.$refs.hostUsbDevicesList.getSelectedUsbVendorId(),
                })
                .then((response) => {
                    this.$emit("usb-device-add-finished");
                    this.visible = false;
                })
                .catch((error) => {
                    this.$refs.errorDialog.show("Error", ["Failed to add USB device.", error.response.data]);
                });
        },
    },
}


</script>