<template>
    <q-dialog v-model="layout">
        <q-layout view="hHh lpR fFf" container class="bg-white">
            <q-header bordered class="bg-primary text-white" height-hint="98">
                <q-toolbar>
                    <q-toolbar-title>Edit VM</q-toolbar-title>
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-toolbar>

                <q-tabs allign="left" v-model="tab">
                    <q-tab name="general" label="General" />
                    <q-tab name="memory" label="Memory" />
                    <q-tab name="disk" label="Disk" />
                    <q-tab name="cdrom" label="CD-ROM" />
                    <q-tab name="network" label="Network" />
                </q-tabs>
                <q-separator />
            </q-header>

            <q-page-container>
                <q-page padding>
                    <q-tab-panels v-model="tab">
                        <q-tab-panel name="general">
                            <q-input label="Name" v-model="general_name" disable />
                            <q-select label="OS" v-model="general_os" :options="osOptions" disable/>
                            <q-select label="Machine" v-model="general_machine" :options="machineOptions" disable/>
                            <q-select label="BIOS" v-model="general_bios" :options="biosOptions" disable/>
                        </q-tab-panel>

                        <q-tab-panel name="memory">
                            <div class="row">
                                <div class="col">
                                    <q-input label="Memory minimum" v-model="memory_minMemory" type="number" min="1"/>
                                </div>
                                <div class="col-md-auto">
                                    <q-select v-model="memory_minMemoryUnit" :options="memoryUnitOptions" />
                                </div>
                            </div>
                            
                            <div class="row">
                                <div class="col">
                                    <q-input label="Memory maximum" v-model="memory_maxMemory" type="number" min="1"/>
                                </div>
                                <div class="col-md-auto">
                                    <q-select v-model="memory_maxMemoryUnit" :options="memoryUnitOptions" />
                                </div>
                                <q-space/>
                            </div>
                        </q-tab-panel>

                        <q-tab-panel name="disk">
                            <div class="row">
                                <div class="col">
                                    <q-input label="Disk size" v-model="disk_size" type="number" min="1"/>
                                </div>
                                <div class="col-md-auto">
                                    <q-select v-model="disk_size_unit" :options="diskUnitOptions" />
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <q-select label="Disk type" v-model="disk_type" :options="diskTypeOptions" />
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <q-select label="Disk bus" v-model="disk_bus" :options="diskBusOptions" />
                                </div>
                            </div>
                            <div class="row">
                                <div class="col">
                                    <q-select label="Pool" v-model="disk_pool" :options="diskPoolOptions" />
                                </div>
                            </div>
                        </q-tab-panel>
                        <q-tab-panel name="cdrom">
                            <q-select label="Pool" v-model="cdrom_pool" :options="cdromPoolOptions" />
                            <q-select label="Path" v-model="cdrom_path" :options="cdromPathOptions" />
                            <q-select label="Bus" v-model="cdrom_bus" :options="cdromBusOptions" />
                        </q-tab-panel>
                        <q-tab-panel name="network">
                            <q-select label="Network" v-model="network_source" :options="networkSourceOptions" />
                            <q-select label="Model" v-model="network_model" :options="networkModelOptions" />
                        </q-tab-panel>
                    </q-tab-panels>
                </q-page>
                <q-footer reveal bordered class="">
                    <q-toolbar>
                        <q-space/>
                        <q-btn flat label="Apply" @click="applyEdits()" />
                    </q-toolbar>
                </q-footer>
            </q-page-container>
        </q-layout>
    </q-dialog>
    <ErrorDialog ref="errorDialog"/>
</template>


<script>
import { ref } from 'vue'
import ErrorDialog from 'src/components/ErrorDialog.vue'

export default {
  data () {
    return {
        layout: ref(false),
        tab: ref('general'),
        osOptions: ["Microsoft Windows 11", "Microsft Windows 10", "Microsoft Windows 7"],
        machineOptions: ["q35", "i440fx"],
        biosOptions: ["ovmf"],
        memoryMinOptions: ["1024", "2048", "4096", "8192", "16384", "32768", "65536"],
        memoryUnitOptions: ["MB", "GB", "TB"],
        general_name: ref(null),
        general_os: ref("Microsoft Windows 11"),
        general_machine: ref("q35"),
        general_bios: ref("ovmf"),
        memory_minMemory: ref(1024),
        memory_minMemoryUnit: ref("MB"),
        memory_maxMemory: ref(1024),
        memory_maxMemoryUnit: ref("MB"),
        disk_size: ref(10),
        disk_size_unit: ref("GB"),
        diskUnitOptions: ["MB", "GB", "TB"],
        diskTypeOptions: ["raw", "qcow2"],
        disk_type: ref("raw"),
        disk_bus: ref("sata"),
        diskBusOptions: ["sata", "scsi", "virtio", "usb"],
        cdrom_bus: ref("sata"),
        cdromBusOptions: ["sata", "scsi", "virtio", "usb"],
        network_source: ref("default"),
        network_sourceOptions: ["default"],
        network_model: ref("virtio"),
        networkModelOptions: ["virtio", "e1000", "rtl8139"]
    }
  },
    components: {
        ErrorDialog
    },
    methods: {
        show(uuid) {
            console.log("Showing edit dialog for VM: " + uuid)
            this.uuid = uuid
            this.$api.get('/vm-manager/' + uuid + '/data').then(response => {
                console.log(response.data)
                // this.general_name = response.data.name
                // this.general_os = response.data.os
                // this.general_machine = response.data.machine
                // this.general_bios = response.data.bios
                // this.memory_minMemory = response.data.memory_min
                // this.memory_minMemoryUnit = response.data.memory_min_unit
                // this.memory_maxMemory = response.data.memory_max
                // this.memory_maxMemoryUnit = response.data.memory_max_unit
                // this.disk_size = response.data.disk_size
                // this.disk_size_unit = response.data.disk_size_unit
                // this.disk_type = response.data.disk_type
                // this.disk_bus = response.data.disk_bus
                // this.cdrom_bus = response.data.cdrom_bus
                // this.network_source = response.data.network_source
                // this.network_model = response.data.network_model
            }).catch(error => {
                console.log(error)
                this.$refs.errorDialog.show(error.response.data)
            })
            // this.layout = true
        },
        applyEdits() {
            console.log("Applying edits...")
            if (this.tab == "general"){
                console.log("General tab")
            }
            else if (this.tab == "memory"){
                console.log("Memory tab")
                console.log("uuid: " + this.uuid)
                const formData = new FormData()
                formData.append('memory_min', this.memory_minMemory)
                formData.append('memory_min_unit', this.memory_minMemoryUnit)
                formData.append('memory_max', this.memory_maxMemory)
                formData.append('memory_max_unit', this.memory_maxMemoryUnit)
                this.$api.post('/vm-manager/' + this.uuid + '/edit-memory', formData).then(response => {
                    console.log("Memory edit successful response:" + response)
                }).catch(error => {
                    this.$refs.errorDialog.show(error.response.data)
                })
            }
            else if (this.tab == "disk"){
                console.log("Disk tab")
            }
            else if (this.tab == "cdrom"){
                console.log("CD-ROM tab")
            }
            else if (this.tab == "network"){
                console.log("Network tab")
            }
        },
    },
}
</script>