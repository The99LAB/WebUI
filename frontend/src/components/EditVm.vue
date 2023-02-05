<template>
    <q-dialog v-model="layout">
        <q-layout view="hHh lpR fFf" container class="bg-white">
            <q-header bordered class="bg-primary text-white" height-hint="98">
                <q-toolbar>
                    <q-toolbar-title>Edit VM</q-toolbar-title>
                    <q-btn icon="close" flat round dense v-close-popup @click="tab = 'general'"/>
                </q-toolbar>

                <q-tabs allign="left" v-model="tab">
                    <q-tab name="general" label="General" />
                    <q-tab name="memory" label="Memory" />
                    <q-tab name="disk" label="Disk" />
                    <q-tab name="network" label="Network" />
                    <q-tab name="xml" label="Xml" />
                </q-tabs>
                <q-separator />
            </q-header>

            <q-page-container>
                <q-page padding>
                    <q-tab-panels v-model="tab">
                        <q-tab-panel name="general">
                            <q-input label="Name" v-model="general_name">
                                <template v-slot:append>
                                    <q-btn round dense flat icon="mdi-check" @click="generalChangeName(general_name)"/>
                                </template>
                            </q-input>
                            <q-select label="Machine" v-model="general_machine" disable/>
                            <q-select label="BIOS" v-model="general_bios" disable/>
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
                            <div v-for="disk in diskList" :key="disk">
                                <q-separator spaced="lg" inset v-if="disk.number!=0"/>
                                <div class="row">
                                    <div class="col">
                                        <q-input label="Disk Number" v-model="disk.number" type="number" min="1" readonly/>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        <q-select label="Device Type" v-model="disk.devicetype" :options="diskTypeOptions" @update:model-value="val => diskChangeType(disk.number, val)" />
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        <q-select label="Driver Type" v-model="disk.drivertype" :options="diskDriverTypeOptions" @update:model-value="val => diskChangeDriverType(disk.number, val)"/>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        <q-select label="Bus Format" v-model="disk.busformat" :options="diskBusOptions" @update:model-value="val => diskChangeBus(disk.number, val)"/>
                                    </div>
                                </div>
                                <div class="row">
                                    <div class="col">
                                        <q-input label="Source File" v-model="disk.sourcefile">
                                            <template v-slot:append>
                                                <q-btn round dense flat icon="mdi-eye" @click="diskShowSourceFileDialog(disk.number)"/>
                                                <q-btn round dense flat icon="mdi-check" @click="diskChangeSourceFile(disk.number, disk.sourcefile)"/>
                                            </template>
                                        </q-input>
                                    </div>
                                </div>
                                <q-separator inset vertical />
                                <div class="row">
                                    <div class="col">
                                        <q-toggle label="Read Only" v-model="disk.readonly" disable/>
                                    </div>
                                    <div class="col-md-auto">
                                        <q-btn color="primary" icon="delete"  @click="diskDelete(disk.number)" />
                                    </div>
                                </div>
                            </div>
                        </q-tab-panel>
                        <q-tab-panel name="network">
                            <NetworkList ref="network_source" />
                            <q-select label="Model" v-model="network_model" :options="networkModelOptions" />
                        </q-tab-panel>
                        <q-tab-panel name="xml">
                            <q-input filled v-model="xml" type="textarea" autogrow/>
                        </q-tab-panel>
                    </q-tab-panels>
                </q-page>
                <q-footer reveal bordered>
                    <q-toolbar>
                        <q-space/>
                        <q-btn flat label="Add" @click="diskAdd()" v-if="tab=='disk'"/>
                        <q-btn flat label="Apply" @click="applyEdits()" v-if="tab!='disk' && tab!='general'"/>
                    </q-toolbar>
                </q-footer>
            </q-page-container>
        </q-layout>
    </q-dialog>
    <ErrorDialog ref="errorDialog"/>
    <ConfirmDialog ref="confirmDialog" @confirm-yes="diskDeleteConfirm()"/>
    <AddDisk ref="addDisk" @disk-add-finished="refreshData()"/>
    <sourceFileDialog ref="sourceFileDialog" @sourcefile-add-finished="refreshData()"/>
</template>


<script>
import { ref } from 'vue'
import ErrorDialog from 'src/components/ErrorDialog.vue'
import NetworkList from 'src/components/NetworkList.vue'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import AddDisk from 'src/components/AddDisk.vue'
import sourceFileDialog from 'src/components/sourceFileDialog.vue'

export default {
  data () {
    return {
        layout: ref(false),
        tab: ref('general'),
        general_name: null,
        general_machine: null,
        general_bios: null,
        memoryMinOptions: ["1024", "2048", "4096", "8192", "16384", "32768", "65536"],
        memoryUnitOptions: ["MB", "GB", "TB"],
        memory_minMemory: null,
        memory_minMemoryUnit: ref("GB"),
        memory_maxMemory: null,
        memory_maxMemoryUnit: ref("GB"),
        diskUnitOptions: ["MB", "GB", "TB"],
        diskDriverTypeOptions: ["raw", "qcow2"],
        diskBusOptions: ["sata", "scsi", "virtio", "usb"],
        diskTypeOptions: ["disk", "cdrom"],
        diskList: [],
        diskDeleteNumber: null,
        network_model: null,
        networkModelOptions: ["virtio", "e1000", "rtl8139"],
        xml: null
    }
  },
    components: {
        ErrorDialog,
        NetworkList,
        ConfirmDialog,
        AddDisk,
        sourceFileDialog
    },
    methods: {
        show(uuid) {
            this.uuid = uuid
            this.refreshData()
        },
        refreshData() {
            this.$api.get('/vm-manager/' + this.uuid + '/data')
            .then(response => {
                this.general_name = response.data.name
                this.general_machine = response.data.machine
                this.general_bios = response.data.bios
                this.memory_minMemory = response.data.memory_min
                this.memory_minMemoryUnit = response.data.memory_min_unit
                this.memory_maxMemory = response.data.memory_max
                this.memory_maxMemoryUnit = response.data.memory_max_unit
                this.diskList = response.data.disks
                this.layout = true
            }).catch(error => {
                this.$refs.errorDialog.show(error.response.data)
            })

            this.$api.get('/vm-manager/' + this.uuid + '/xml')
            .then(response => {
                this.xml = response.data.xml
            }).catch(error => {
                this.$refs.errorDialog.show(error.response.data)
            })

        },
        applyEdits() {
            console.log("Applying edits...")
            if (this.tab == "memory"){
                console.log("Memory tab")
                console.log("uuid: " + this.uuid)
                this.$api.post('/vm-manager/' + this.uuid + '/edit-memory', {
                    memory_min: this.memory_minMemory,
                    memory_min_unit: this.memory_minMemoryUnit,
                    memory_max: this.memory_maxMemory,
                    memory_max_unit: this.memory_maxMemoryUnit
                }).then(response => {
                    this.refreshData()
                }).catch(error => {
                    this.$refs.errorDialog.show("Error changing memory", [error.response.data])
                })
            }
            else if (this.tab == "network"){
                console.log("Network tab")
            }
            else if (this.tab == "xml"){
                console.log("XML tab")
                this.$api.post('/vm-manager/' + this.uuid + '/edit-xml', {
                    xml: this.xml
                }).then(response => {
                    this.refreshData()
                }).catch(error => {
                    this.$refs.errorDialog.show("Error changing XML", [error.response.data])
                })
            }
        },
        generalChangeName(value){
            this.$api.post('/vm-manager/' + this.uuid + '/edit-general-name', {
                value: value
            }).then(response => {
                this.refreshData()
            }).catch(error => {
                this.$refs.errorDialog.show(error.response.data)
            })
        },
        diskChangeType(disknumber, value){
            this.$api.post('/vm-manager/' + this.uuid + '/edit-disk-type', {
                number: disknumber,
                value: value
            }).then(response => {
                this.refreshData()
            }).catch(error => {
                this.$refs.errorDialog.show(error.response.data)
            })

        },
        diskChangeDriverType(disknumber, value){
            this.$api.post('/vm-manager/' + this.uuid + '/edit-disk-driver-type', {
                number: disknumber,
                value: value
            }).then(response => {
                this.refreshData()
            }).catch(error => {
                this.$refs.errorDialog.show(error.response.data)
            })

        },
        diskChangeBus(disknumber, value){
            this.$api.post('/vm-manager/' + this.uuid + '/edit-disk-bus', {
                number: disknumber,
                value: value
            }).then(response => {
                this.refreshData()
            }).catch(error => {
                this.$refs.errorDialog.show(error.response.data)
            })
        },
        diskChangeSourceFile(disknumber, value){
            this.$api.post('/vm-manager/' + this.uuid + '/edit-disk-source-file', {
                number: disknumber,
                value: value
            }).then(response => {
                this.refreshData()
            }).catch(error => {
                this.$refs.errorDialog.show(error.response.data)
            })
        },
        diskShowSourceFileDialog(disknumber){
            this.$refs.sourceFileDialog.show(disknumber, this.uuid)
        },
        diskDelete(disknumber){
            this.$refs.confirmDialog.show("Delete disk", ["Are you sure you want to delete this disk?", "This only removes the disk from the vm, not from the storage pool."])
            this.diskDeleteNumber = disknumber
        },
        diskDeleteConfirm() {
            this.$api.post('/vm-manager/' + this.uuid + '/edit-disk-delete', {
                number: this.diskDeleteNumber
            }).then(response => {
                this.refreshData()
            }).catch(error => {
                this.$refs.errorDialog.show(error.response.data)
            })
        },
        diskAdd(){
            this.$refs.addDisk.show(this.uuid)
        }
    },
}
</script>