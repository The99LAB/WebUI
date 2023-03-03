<template>
  <q-dialog v-model="layout">
    <q-layout view="hHh lpR fFf" container class="bg-white">
      <q-header bordered class="bg-primary text-white" height-hint="98">
        <q-toolbar>
          <q-toolbar-title>Edit VM</q-toolbar-title>
          <q-btn
            icon="close"
            flat
            round
            dense
            v-close-popup
            @click="tab = 'general'"
          />
        </q-toolbar>

        <q-tabs allign="left" v-model="tab">
          <q-tab name="general" label="General" />
          <q-tab name="cpu" label="CPU" />
          <q-tab name="memory" label="Memory" />
          <q-tab name="disk" label="Disk" />
          <q-tab name="network" label="Network" />
          <q-tab name="graphics" label="Graphics" />
          <q-tab name="passthrough" label="Passthrough" />
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
                  <q-btn
                    round
                    dense
                    flat
                    icon="mdi-check"
                    @click="generalChangeName(general_name)"
                  />
                </template>
              </q-input>
              <q-select label="Machine" v-model="general_machine" disable />
              <q-select label="BIOS" v-model="general_bios" disable />
              <q-toggle
                label="Autostart"
                v-model="general_autostart"
                @update:model-value="toggleAutostart"
              />
            </q-tab-panel>
            <q-tab-panel name="cpu">
              <!-- cpu model -->
              <q-select
                label="CPU Model"
                v-model="cpu_model"
                :options="cpuModelOptions"
                @update:model-value="calculateCpu"
              />
              <q-input
                label="Current vCPU"
                v-model="currentVcpu"
                type="number"
                min="1"
                :max="vcpu"
                :rules="[
                  (val) =>
                    val <= vcpu ||
                    'Current vCPU cannot be bigger than vCPU value',
                ]"
                disable
                v-if="customTopology"
              />
              <q-input
                label="Current vCPU"
                v-model="currentVcpu"
                type="number"
                min="1"
                :max="vcpu"
                :rules="[
                  (val) =>
                    val <= vcpu ||
                    'Current vCPU cannot be bigger than vCPU value',
                ]"
                v-else
              />
              <q-input
                label="vCPU"
                v-model="vcpu"
                type="number"
                min="1"
                disable
                v-if="customTopology"
              />
              <q-input
                label="vCPU"
                v-model="vcpu"
                type="number"
                min="1"
                @update:model-value="(val) => (topologySockets = val)"
                v-else
              />
              <q-toggle
                label="Custom Topology"
                v-model="customTopology"
                @update:model-value="calculateCpu"
              />
              <div v-if="customTopology">
                <q-input
                  label="Sockets"
                  v-model="topologySockets"
                  type="number"
                  min="1"
                  @update:model-value="calculateCpu"
                />
                <q-input
                  label="Dies"
                  v-model="topologyDies"
                  type="number"
                  min="1"
                  @update:model-value="calculateCpu"
                />
                <q-input
                  label="Cores"
                  v-model="topologyCores"
                  type="number"
                  min="1"
                  @update:model-value="calculateCpu"
                />
                <q-input
                  label="Threads"
                  v-model="topologyThreads"
                  type="number"
                  min="1"
                  @update:model-value="calculateCpu"
                />
              </div>
              <div v-else>
                <q-input
                  label="Sockets"
                  v-model="topologySockets"
                  type="number"
                  min="1"
                  @update:model-value="calculateCpu"
                  disable
                />
                <q-input
                  label="Dies"
                  v-model="topologyDies"
                  type="number"
                  min="1"
                  @update:model-value="calculateCpu"
                  disable
                />
                <q-input
                  label="Cores"
                  v-model="topologyCores"
                  type="number"
                  min="1"
                  @update:model-value="calculateCpu"
                  disable
                />
                <q-input
                  label="Threads"
                  v-model="topologyThreads"
                  type="number"
                  min="1"
                  @update:model-value="calculateCpu"
                  disable
                />
              </div>
            </q-tab-panel>
            <q-tab-panel name="memory">
              <div class="row">
                <div class="col">
                  <q-input
                    label="Memory minimum"
                    v-model="memory_minMemory"
                    type="number"
                    min="1"
                  />
                </div>
                <div class="col-md-auto">
                  <q-select
                    v-model="memory_minMemoryUnit"
                    :options="memoryUnitOptions"
                  />
                </div>
              </div>
              <div class="row">
                <div class="col">
                  <q-input
                    label="Memory maximum"
                    v-model="memory_maxMemory"
                    type="number"
                    min="1"
                  />
                </div>
                <div class="col-md-auto">
                  <q-select
                    v-model="memory_maxMemoryUnit"
                    :options="memoryUnitOptions"
                  />
                </div>
                <q-space />
              </div>
            </q-tab-panel>

            <q-tab-panel name="disk">
              <div v-for="disk in diskList" :key="disk">
                <q-separator spaced="lg" inset v-if="disk.number != 0" />
                <div class="row">
                  <div class="col">
                    <q-input
                      label="Disk Number"
                      v-model="disk.number"
                      type="number"
                      min="1"
                      readonly
                    />
                  </div>
                </div>
                <div class="row">
                  <div class="col">
                    <q-select
                      label="Device Type"
                      v-model="disk.devicetype"
                      :options="diskTypeOptions"
                      @update:model-value="
                        (val) => diskChangeType(disk.number, val)
                      "
                    />
                  </div>
                </div>
                <div class="row">
                  <div class="col">
                    <q-select
                      label="Driver Type"
                      v-model="disk.drivertype"
                      :options="diskDriverTypeOptions"
                      @update:model-value="
                        (val) => diskChangeDriverType(disk.number, val)
                      "
                    />
                  </div>
                </div>
                <div class="row">
                  <div class="col">
                    <q-select
                      label="Bus Format"
                      v-model="disk.busformat"
                      :options="diskBusOptions"
                      @update:model-value="
                        (val) => diskChangeBus(disk.number, val)
                      "
                    />
                  </div>
                </div>
                <div class="row" v-if="disk.sourcefile != null">
                  <div class="col">
                    <q-input label="Source File" v-model="disk.sourcefile">
                      <template v-slot:append>
                        <q-btn
                          round
                          dense
                          flat
                          icon="mdi-eye"
                          @click="diskShowSourceFileDialog(disk.number)"
                        />
                        <q-btn
                          round
                          dense
                          flat
                          icon="mdi-check"
                          @click="
                            diskChangeSourceFile(disk.number, disk.sourcefile)
                          "
                        />
                      </template>
                    </q-input>
                  </div>
                </div>
                <div class="row" v-if="disk.sourcedev != null">
                  <div class="col">
                    <q-input label="Source Device" v-model="disk.sourcedev">
                      <template v-slot:append>
                        <q-btn
                          round
                          dense
                          flat
                          icon="mdi-check"
                          @click="
                            diskChangeSourceDev(disk.number, disk.sourcedev)
                          "
                        />
                      </template>
                    </q-input>
                  </div>
                </div>
                <div class="row">
                  <div class="col">
                    <q-input
                      label="Boot order"
                      v-model="disk.bootorder"
                      type="number"
                      min="1"
                    >
                      <template v-slot:append>
                        <q-btn
                          round
                          dense
                          flat
                          icon="mdi-check"
                          @click="
                            diskChangeBootorder(disk.number, disk.bootorder)
                          "
                        />
                      </template>
                    </q-input>
                  </div>
                </div>
                <q-separator inset vertical />
                <div class="row">
                  <div class="col">
                    <q-toggle
                      label="Read Only"
                      v-model="disk.readonly"
                      disable
                    />
                  </div>
                  <div class="col-md-auto">
                    <q-btn
                      color="primary"
                      icon="delete"
                      @click="diskDelete(disk.number)"
                    />
                  </div>
                </div>
              </div>
              <p v-if="diskList.length == 0">No disks</p>
            </q-tab-panel>
            <q-tab-panel name="network">
              <div v-for="network in networkList" :key="network">
                <q-separator spaced="lg" inset v-if="network.number != 0" />
                <div class="row">
                  <div class="col">
                    <q-input
                      label="Interface Number"
                      v-model="network.number"
                      type="number"
                      min="1"
                      readonly
                    >
                      <template v-slot:after>
                        <q-btn
                          color="primary"
                          icon="delete"
                          @click="networkDelete(network.number)"
                        />
                      </template>
                    </q-input>
                  </div>
                </div>
                <div class="row">
                  <div class="col">
                    <q-input
                      label="MAC Address"
                      v-model="network.mac_addr"
                      readonly
                    />
                  </div>
                </div>
                <div class="row">
                  <div class="col">
                    <q-input label="Source" v-model="network.source" readonly />
                  </div>
                </div>
                <div class="row">
                  <div class="col">
                    <q-input label="Model" v-model="network.model" readonly />
                  </div>
                </div>
                <div class="row">
                  <div class="col">
                    <q-input
                      label="Boot order"
                      v-model="network.bootorder"
                      readonly
                    />
                  </div>
                </div>
              </div>
              <p v-if="networkList.length == 0">No networks</p>
            </q-tab-panel>
            <q-tab-panel name="graphics">
              <div v-for="graphicsdevice in graphicsdevicesList" :key="graphicsdevice">
                <q-separator spaced="lg" inset v-if="graphicsdevice.index != 0" />
                <q-input label="Device Type" model-value="Graphics" readonly >
                  <template v-slot:after>
                    <q-btn icon="delete" round dense flat @click="graphicsDelete(graphicsdevice.index)"/>
                  </template>
                </q-input>
                <q-input label="Graphics Type" v-model="graphicsdevice.type" readonly/>
              </div>
              <div v-for="videodevice in videodevicesList" :key="videodevice">
                <q-separator spaced="lg" inset />
                <q-input label="Device Type" model-value="Video" readonly >
                  <template v-slot:after v-if="videodevicesList.length > 1">
                    <q-btn icon="mdi-delete" round dense flat @click="videoDelete(videodevice.index)"/>
                  </template>
                </q-input>
                <q-input label="Video Type" v-model="videodevice.type" readonly/>
              </div>
            </q-tab-panel>
            <q-tab-panel name="passthrough">
              <div v-for="usbdevice in usbdevicesList" :key="usbdevice">
                <q-input model-value="USB Device" label="Type" readonly>
                  <template v-slot:after>
                    <q-btn
                      color="primary"
                      icon="delete"
                      @click="
                        usbdeviceDelete(usbdevice.productid, usbdevice.vendorid)
                      "
                    />
                  </template>
                </q-input>
                <q-input v-model="usbdevice.name" label="Name" readonly />
                <q-input
                  v-model="usbdevice.vendorid"
                  label="Vendor Id"
                  readonly
                />
                <q-input
                  v-model="usbdevice.productid"
                  label="Product Id"
                  readonly
                />
                <q-separator spaced="lg" inset />
              </div>
              <div v-for="pcidevice in pcidevicesList" :key="pcidevice">
                <q-input model-value="PCI Device" label="Type" readonly>
                  <template v-slot:after>
                    <q-btn
                      color="primary"
                      icon="delete"
                      @click="
                        pciedeviceDelete(
                          pcidevice.domain,
                          pcidevice.bus,
                          pcidevice.slot,
                          pcidevice.function
                        )
                      "
                    />
                  </template>
                </q-input>
                <q-input
                  v-model="pcidevice.devicepath"
                  label="Device Path"
                  readonly
                />
                <q-input
                  v-model="pcidevice.vendorName"
                  label="Vendor Name"
                  readonly
                />
                <q-input
                  v-model="pcidevice.productName"
                  label="Product Name"
                  readonly
                />
                <q-toggle
                  v-model="pcidevice.customRomFile"
                  label="Rom File"
                  @update:model-value="
                    (val) => pcieToggleRomFile(val, pcidevice.xml)
                  "
                />
                <q-input
                  v-if="pcidevice.customRomFile"
                  v-model="pcidevice.romfile"
                  label="Rom File"
                >
                  <template v-slot:append>
                    <q-btn
                      round
                      dense
                      flat
                      icon="mdi-check"
                      @click="
                        pcieChangeRomFile(pcidevice.xml, pcidevice.romfile)
                      "
                    />
                  </template>
                </q-input>
                <q-separator spaced="lg" inset />
              </div>
            </q-tab-panel>
            <q-tab-panel name="xml">
              <q-input filled v-model="xml" type="textarea" autogrow />
            </q-tab-panel>
          </q-tab-panels>
        </q-page>
        <q-footer reveal bordered>
          <q-toolbar>
            <q-space />
            <q-btn flat label="Add" @click="diskAdd()" v-if="tab == 'disk'" />
            <q-btn
              flat
              label="Add Network"
              @click="networkAdd()"
              v-if="tab == 'network'"
            />
            <q-btn
              flat
              label="Add USB Device"
              @click="usbdeviceAdd()"
              v-if="tab == 'passthrough'"
            />
            <q-btn
              flat
              label="Add PCI Device"
              @click="pciedeviceAdd()"
              v-if="tab == 'passthrough'"
            />
            <q-btn
              flat
              label="Add Graphics"
              @click="graphicsAdd()"
              v-if="tab == 'graphics'"
            />
            <q-btn
              flat
              label="Add Video"
              @click="videoAdd()"
              v-if="tab == 'graphics'"
            />
            <q-btn
              flat
              label="Apply"
              @click="applyEdits()"
              v-if="
                tab == 'memory' ||
                tab == 'xml' ||
                tab == 'cpu'
              "
            />
          </q-toolbar>
        </q-footer>
      </q-page-container>
    </q-layout>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
  <ConfirmDialog ref="confirmDialog" @confirm-yes="confirmDialogYes()" />
  <AddDisk ref="addDisk" @disk-add-finished="refreshData()" />
  <sourceFileDialog
    ref="sourceFileDialog"
    @sourcefile-add-finished="refreshData()"
  />
  <AddNetwork ref="addNetwork" @network-add-finished="refreshData()" />
  <AddUsbDevice ref="addUsbDevice" @usb-device-add-finished="refreshData()" />
  <AddPcieDevice
    ref="addPcieDevice"
    @pcie-device-add-finished="refreshData()"
  />
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";
import AddDisk from "src/components/AddDisk.vue";
import sourceFileDialog from "src/components/SourceFileDialog.vue";
import AddNetwork from "src/components/AddNetwork.vue";
import AddUsbDevice from "src/components/AddUsbDevice.vue";
import AddPcieDevice from "src/components/AddPcieDevice.vue";

export default {
  data() {
    return {
      layout: ref(false),
      tab: ref("general"),
      general_name: null,
      general_machine: null,
      general_bios: null,
      general_autostart: null,
      memoryMinOptions: [
        "1024",
        "2048",
        "4096",
        "8192",
        "16384",
        "32768",
        "65536",
      ],
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
      networkList: [],
      networkDeleteNumber: null,
      usbdevicesList: [],
      pcidevicesList: [],
      cpuModelOptions: ["host-model", "host-passthrough"],
      cpu_model: null,
      currentVcpu: null,
      vcpu: null,
      customTopology: false,
      topologySockets: null,
      topologyDies: null,
      topologyCores: null,
      topologyThreads: null,
      graphicsdevicesList: [],
      videodevicesList: [],
      xml: null,
    };
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
    AddDisk,
    sourceFileDialog,
    AddNetwork,
    AddUsbDevice,
    AddPcieDevice,
  },
  methods: {
    show(uuid) {
      this.uuid = uuid;
      this.refreshData();
    },
    refreshData() {
      this.$api
        .get("/vm-manager/" + this.uuid + "/data")
        .then((response) => {
          this.general_name = response.data.name;
          this.general_machine = response.data.machine;
          this.general_bios = response.data.bios;
          this.general_autostart = response.data.autostart;
          this.memory_minMemory = response.data.memory_min;
          this.memory_minMemoryUnit = response.data.memory_min_unit;
          this.memory_maxMemory = response.data.memory_max;
          this.memory_maxMemoryUnit = response.data.memory_max_unit;
          this.currentVcpu = response.data.current_vcpu;
          this.cpu_model = response.data.cpu_model;
          this.vcpu = response.data.vcpu;
          this.customTopology = response.data.custom_topology;
          this.topologySockets = response.data.topology_sockets;
          this.topologyDies = response.data.topology_dies;
          this.topologyCores = response.data.topology_cores;
          this.topologyThreads = response.data.topology_threads;
          this.diskList = response.data.disks;
          this.networkList = response.data.networks;
          this.usbdevicesList = response.data.usbdevices;
          this.pcidevicesList = response.data.pcidevices;
          this.graphicsdevicesList = response.data.graphicsdevices;
          this.videodevicesList = response.data.videodevices;
          this.layout = true;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error loading VM data.", [
            error.response.data,
          ]);
        });

      this.$api
        .get("/vm-manager/" + this.uuid + "/xml")
        .then((response) => {
          this.xml = response.data.xml;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error loading VM XML.", [
            error.response.data,
          ]);
        });
    },
    applyEdits() {
      if (this.tab == "memory") {
        this.$api
          .post("/vm-manager/" + this.uuid + "/edit-memory", {
            memory_min: this.memory_minMemory,
            memory_min_unit: this.memory_minMemoryUnit,
            memory_max: this.memory_maxMemory,
            memory_max_unit: this.memory_maxMemoryUnit,
          })
          .then((response) => {
            this.refreshData();
          })
          .catch((error) => {
            this.$refs.errorDialog.show("Error changing memory", [
              error.response.data,
            ]);
          });
      } else if (this.tab == "cpu") {
        if (this.currentVcpu > this.vcpu) {
          this.$refs.confirmDialog.show("VCPU error", [
            "Current VCPU is greater than the new VCPU. This is not allowed.",
          ]);
          return;
        }
        this.$api
          .post("/vm-manager/" + this.uuid + "/edit-cpu", {
            vcpu: this.vcpu,
            cpu_model: this.cpu_model,
            current_vcpu: this.currentVcpu,
            custom_topology: this.customTopology,
            topology_sockets: this.topologySockets,
            topology_dies: this.topologyDies,
            topology_cores: this.topologyCores,
            topology_threads: this.topologyThreads,
          })
          .then((response) => {
            this.refreshData();
          })
          .catch((error) => {
            this.$refs.errorDialog.show("Error changing CPU", [
              error.response.data,
            ]);
          });
      } else if (this.tab == "xml") {
        this.$api
          .post("/vm-manager/" + this.uuid + "/edit-xml", {
            xml: this.xml,
          })
          .then((response) => {
            this.refreshData();
          })
          .catch((error) => {
            this.$refs.errorDialog.show("Error changing XML", [
              error.response.data,
            ]);
          });
      }
    },
    generalChangeName(value) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-general-name", {
          value: value,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error changing name", [
            error.response.data,
          ]);
        });
    },
    diskChangeType(disknumber, value) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-type", {
          number: disknumber,
          value: value,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing disk type", [
            error.response.data,
          ]);
        });
    },
    diskChangeDriverType(disknumber, value) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-driver-type", {
          number: disknumber,
          value: value,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing driver type", [
            error.response.data,
          ]);
        });
    },
    diskChangeBus(disknumber, value) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-bus", {
          number: disknumber,
          value: value,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing bus", [
            error.response.data,
          ]);
        });
    },
    diskChangeSourceFile(disknumber, value) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-source-file", {
          number: disknumber,
          value: value,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing source file", [
            error.response.data,
          ]);
        });
    },
    diskChangeSourceDev(disknumber, value) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-source-dev", {
          number: disknumber,
          value: value,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing source device", [
            error.response.data,
          ]);
        });
    },
    diskShowSourceFileDialog(disknumber) {
      this.$refs.sourceFileDialog.show(disknumber, this.uuid);
    },
    diskChangeBootorder(disknumber, value) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-bootorder", {
          number: disknumber,
          value: value,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error changing bootorder", [
            error.response.data,
          ]);
        });
    },
    diskDelete(disknumber) {
      this.$refs.confirmDialog.show("Delete disk", [
        "Are you sure you want to delete this disk?",
        "This only removes the disk from the vm, not from the storage pool.",
      ]);
      this.diskDeleteNumber = disknumber;
    },
    diskDeleteConfirm() {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-delete", {
          number: this.diskDeleteNumber,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting disk", [
            error.response.data,
          ]);
        });
    },
    diskAdd() {
      this.$refs.addDisk.show(this.uuid);
    },
    confirmDialogYes() {
      if (this.tab == "disk") {
        this.diskDeleteConfirm();
      } else if (this.tab == "network") {
        this.networkDeleteConfirm();
      }
    },
    networkAdd() {
      this.$refs.addNetwork.show(this.uuid);
    },
    networkDelete(networknumber) {
      this.$refs.confirmDialog.show("Delete network", [
        "Are you sure you want to delete this network?",
        "This only removes the network from the vm, not from the network pool.",
      ]);
      this.networkDeleteNumber = networknumber;
    },
    networkDeleteConfirm() {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-network-delete", {
          number: this.networkDeleteNumber,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting network", [
            error.response.data,
          ]);
        });
    },
    calculateCpu() {
      this.vcpu =
        this.topologySockets *
        this.topologyDies *
        this.topologyCores *
        this.topologyThreads;
      this.currentVcpu = this.vcpu;
    },
    toggleAutostart() {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-general-autostart", {
          value: this.general_autostart,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error changing autostart", [
            error.response.data,
          ]);
        });
    },
    usbdeviceAdd() {
      this.$refs.addUsbDevice.show(this.uuid);
    },
    usbdeviceDelete(productid, vendorid) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-usb-delete", {
          productid: productid,
          vendorid: vendorid,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting usb device", [
            error.response.data,
          ]);
        });
    },
    pciedeviceAdd() {
      this.$refs.addPcieDevice.show(this.uuid);
    },
    pciedeviceDelete(device_domain, device_bus, device_slot, device_function) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-pcie-delete", {
          domain: device_domain,
          bus: device_bus,
          slot: device_slot,
          function: device_function,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting pcie device", [
            error.response.data,
          ]);
        });
    },
    pcieChangeRomFile(xml, romfile) {
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-pcie-romfile", {
          xml: xml,
          romfile: romfile,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error changing pcie rom file", [
            error.response.data,
          ]);
        });
    },
    pcieToggleRomFile(value, xml) {
      if (value == false) {
        this.pcieChangeRomFile(xml, "");
      }
    },
    graphicsDelete(index){
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-graphics-delete", {
          index: index,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting graphics", [
            error.response.data,
          ]);
        });
    },
    videoDelete(index){
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-video-delete", {
          index: index,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting video", [
            error.response.data,
          ]);
        });
    },   
  },
};
</script>
