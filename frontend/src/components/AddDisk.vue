<template>
    <q-dialog v-model="alert">
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Add Disk</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator spaced="lg" inset />
        <q-card-section class="q-pt-none q-px-xl">
            <StoragePoolAndVolumeList ref="storagePoolVolumeList"/>
            <q-select v-model="diskDriverType" :options="diskDriverTypeOptions" label="Driver Type" />
            <q-select v-model="diskBus" :options="diskBusOptions" label="Bus Format" />
        </q-card-section>
        <q-card-actions align="right">
            <q-btn flat label="Finish" @click="addDisk()" />
        </q-card-actions>
      </q-card>
    </q-dialog>
</template>

<script>
import { ref } from 'vue'
import StoragePoolAndVolumeList from 'src/components/StoragePoolAndVolumeList.vue'

export default {
    data() {
        return {
            alert: ref(false),
            pool: null,
            volume: null,
            diskDriverTypeOptions: ["raw", "qcow2"],
            diskDriverType: "raw",
            diskBusOptions: ["sata", "scsi", "virtio", "usb"],
            diskBus: "virtio",
        }
    },
    emits: ["disk-add-finished"],
    components: {
        StoragePoolAndVolumeList
    },
    methods : {
        show() {
            this.alert = true
        },
        addDisk() {
            this.pool = this.$refs.storagePoolVolumeList.getSelectedPool()
            this.volume = this.$refs.storagePoolVolumeList.getSelectedVolume()
            console.log("Pool: " + this.pool)
            console.log("Volume: " + this.volume)
            console.log("Driver Type: " + this.diskDriverType)
            console.log("Bus: " + this.diskBus)
            // this.$emit("disk-add-finished")
        },
    }
}
</script>