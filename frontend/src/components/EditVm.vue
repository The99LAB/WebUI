<template>
  <q-dialog v-model="layout" full-width full-height>
    <q-layout
      view="hHh lpR fFf"
      container
      :class="{ 'bg-dark': $q.dark.isActive, 'bg-white': !$q.dark.isActive }"
    >
      <q-header bordered>
        <q-toolbar class="row items-center">
          <p class="text-h6 q-ma-none">Edit VM</p>
          <q-space />
          <!-- 
            general:
              - name
              - autostart
              - machine
              - bios
              - memory
              - cpu
              - boot order ?
            
            devices:
              - video
              - graphics
              - tablet
              - sound
              - network
              - disks
            
            passthrough:
              - usb
              - pci

            xml:
              - xml
           -->
          <q-tabs allign="middle" v-model="tab">
            <q-tab name="general" label="General" />
            <q-tab name="devices" label="Devices" />
            <q-tab name="disk" label="Disk" />
            <q-tab name="network" label="Network" />
            <q-tab name="graphics" label="Graphics" />
            <q-tab name="sound" label="Sound" />
            <q-tab name="passthrough" label="Passthrough" />
            <q-tab name="xml" label="Xml" />
          </q-tabs>
          <q-space />
          <q-btn flat label="Apply" v-if="tab == 'general' || tab == 'xml'">
            <ToolTip content="Apply changes" />
          </q-btn>
          <q-btn
            icon="close"
            flat
            round
            dense
            v-close-popup
            @click="tab = 'general'"
          >
            <ToolTip content="Close" />
          </q-btn>
        </q-toolbar>
      </q-header>

      <q-page-container>
        <q-page padding>
          <q-tab-panels v-model="tab">
            <q-tab-panel name="general">
              <div class="justify-center q-gutter-md">
                <q-card>
                  <q-card-section>
                    <div class="row">
                      <div class="col q-mr-lg">
                        <q-input label="Name" v-model="general_name" />
                        <div class="row items-center q-mt-md">
                          <p class="text-body2 q-ma-none">Autostart:</p>
                          <q-toggle v-model="general_autostart" />
                          <q-tooltip
                            :delay="500"
                            anchor="bottom left"
                            self="top start"
                            :offset="[0, 8]"
                          >
                            Automatically start the VM when the server boots
                          </q-tooltip>
                        </div>
                      </div>
                      <div class="col q-ml-lg">
                        <q-select
                          label="Machine"
                          v-model="general_machine"
                          readonly
                        />
                        <q-select
                          label="BIOS"
                          v-model="general_bios"
                          readonly
                        />
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
                <q-card>
                  <q-card-section class="row q-pb-none">
                    <p class="text-h6 q-ma-none">Memory</p>
                    <q-space />
                    <div class="row items-center">
                      <p class="text-body2 q-ma-none">Enable shared memory:</p>
                      <q-toggle v-model="memory_enable_shared" />
                    </div>
                  </q-card-section>
                  <q-card-section class="q-pt-none">
                    <div class="row">
                      <div class="col q-mr-lg">
                        <q-input
                          label="Current allocation"
                          v-model="memory_minMemory"
                          type="number"
                          min="1"
                        >
                          <template v-slot:append>
                            <q-select
                              v-model="memory_minMemoryUnit"
                              :options="memoryUnitOptions"
                            />
                          </template>
                        </q-input>
                      </div>
                      <div class="col q-ml-lg">
                        <q-input
                          label="Maximum allocation"
                          v-model="memory_maxMemory"
                          type="number"
                          min="1"
                        >
                          <template v-slot:append>
                            <q-select
                              v-model="memory_maxMemoryUnit"
                              :options="memoryUnitOptions"
                            />
                          </template>
                        </q-input>
                      </div>
                    </div>
                  </q-card-section>
                </q-card>
                <q-card>
                  <q-card-section class="row">
                    <div class="col q-mr-lg">
                      <p class="q-ma-none text-h6">CPU</p>
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
                        :readonly="customTopology"
                      />
                      <q-input
                        label="vCPU"
                        v-model="vcpu"
                        type="number"
                        min="1"
                        @update:model-value="(val) => (topologySockets = val)"
                        :readonly="customTopology"
                      />
                    </div>
                    <q-separator vertical />
                    <div class="col q-ml-lg">
                      <div class="row items-center">
                        <p class="q-ma-none text-subtitle1 text-weight-medium">
                          Custom Topology
                          <ToolTip
                            content='"Custom Topology" allows you to set the number of sockets, dies, cores, and threads manually. If you disable this option, the vCPU value will be used to calculate the topology.'
                          />
                        </p>
                        <q-space />
                        <q-toggle
                          v-model="customTopology"
                          @update:model-value="calculateCpu"
                        />
                      </div>
                      <q-input
                        label="Sockets"
                        v-model="topologySockets"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!customTopology"
                      />
                      <q-input
                        label="Dies"
                        v-model="topologyDies"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!customTopology"
                      />
                      <q-input
                        label="Cores"
                        v-model="topologyCores"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!customTopology"
                      />
                      <q-input
                        label="Threads"
                        v-model="topologyThreads"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!customTopology"
                      />
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </q-tab-panel>
            <q-tab-panel name="devices">
              <!-- column left side with all the devices -->
              <!-- https://quasar.dev/vue-components/list-and-list-items#example--menu -->
              <!-- right side, detail about the device -->
              <div class="row">
                <div class="col-">
                  <q-list bordered>
                    <q-item
                      clickable
                      v-ripple
                      v-for="disk in diskList"
                      :key="disk"
                      active
                      @click="console.log('click disk', disk.index)"
                    >
                      <q-item-section thumbnail class="q-pr-sm">
                        <q-icon
                          color="primary"
                          :name="
                            disk.device_type == 'cdrom'
                              ? 'mdi-disc'
                              : 'mdi-harddisk'
                          "
                          class="q-pl-sm"
                        />
                      </q-item-section>
                      <q-item-section>
                        <q-item-label>
                          {{
                            disk.bus_format == "virtio"
                              ? "VirtIO"
                              : disk.bus_format.toUpperCase()
                          }}
                          {{
                            disk.device_type == "cdrom"
                              ? "CDROM"
                              : disk.device_type == "disk"
                              ? "Disk"
                              : disk.device_type
                          }}
                          {{ disk.index }}
                        </q-item-label>
                      </q-item-section>
                    </q-item>
                  </q-list>
                </div>
                <div class="col q-ml-md">
                  <p class="text-h6 q-ma-none">Device</p>
                </div>
              </div>
            </q-tab-panel>
            <q-tab-panel name="disk">
              <div v-for="disk in diskList" :key="disk">
                <q-separator
                  color="primary"
                  spaced="lg"
                  v-if="disk.index != 0"
                />
                <q-input
                  label="Device Type"
                  v-model="disk.device_type"
                  readonly
                >
                  <template v-slot:append>
                    <q-btn
                      flat
                      round
                      color="primary"
                      icon="delete"
                      @click="diskDelete(disk.index)"
                    >
                      <q-tooltip :offset="[5, 5]">Delete Disk</q-tooltip>
                    </q-btn>
                  </template>
                </q-input>
                <q-input
                  label="Driver Type"
                  v-model="disk.driver_type"
                  readonly
                />
                <q-input
                  label="Bus Format"
                  v-model="disk.bus_format"
                  readonly
                />
                <q-input
                  :label="
                    disk.read_only ? 'Source File (Read Only)' : 'Source File'
                  "
                  v-model="disk.source_file"
                  v-if="disk.source_file != null"
                  readonly
                />
                <q-input
                  label="Source Device"
                  v-model="disk.source_device"
                  v-if="disk.source_device != null"
                  readonly
                />
                <q-input
                  label="Boot order"
                  v-model="disk.boot_order"
                  v-if="disk.boot_order != null"
                  type="number"
                  min="1"
                  readonly
                />
              </div>
            </q-tab-panel>
            <q-tab-panel name="network">
              <div v-for="network in networkList" :key="network">
                <q-separator
                  color="primary"
                  spaced="lg"
                  v-if="network.number != 0"
                />
                <q-input
                  label="Interface Number"
                  v-model="network.number"
                  type="number"
                  min="1"
                  readonly
                >
                  <template v-slot:append>
                    <q-btn
                      flat
                      round
                      color="primary"
                      icon="mdi-delete"
                      @click="networkDelete(network.number)"
                    >
                      <q-tooltip :offset="[5, 5]"
                        >Delete Network Interface</q-tooltip
                      >
                    </q-btn>
                  </template>
                </q-input>
                <q-input
                  label="MAC Address"
                  v-model="network.mac_address"
                  readonly
                />
                <q-input label="Source" v-model="network.source" readonly />
                <q-input label="Model" v-model="network.model" readonly />
                <q-input
                  label="Boot order"
                  v-model="network.boot_order"
                  v-if="network.boot_order != null"
                  readonly
                />
              </div>
            </q-tab-panel>
            <q-tab-panel name="graphics">
              <div
                v-for="graphicsdevice in graphicsdevicesList"
                :key="graphicsdevice"
              >
                <q-separator
                  color="primary"
                  spaced="lg"
                  v-if="graphicsdevice.index != 0"
                />
                <q-input label="Device Type" model-value="Graphics" readonly>
                  <template v-slot:append>
                    <q-btn
                      icon="mdi-delete"
                      color="primary"
                      round
                      flat
                      @click="graphicsDelete(graphicsdevice.index)"
                    >
                      <q-tooltip :offset="[5, 5]"
                        >Delete Graphics Device</q-tooltip
                      >
                    </q-btn>
                  </template>
                </q-input>
                <q-input
                  label="Graphics Type"
                  v-model="graphicsdevice.type"
                  readonly
                />
              </div>
              <div v-for="videodevice in videodevicesList" :key="videodevice">
                <q-separator
                  color="primary"
                  spaced="lg"
                  v-if="
                    graphicsdevicesList.length > 0 && videodevice.index >= 0
                  "
                />
                <q-input label="Device Type" model-value="Video" readonly>
                  <template
                    v-slot:after
                    v-if="
                      graphicsdevicesList.length < 1 ||
                      videodevicesList.length > 1
                    "
                  >
                    <q-btn
                      icon="mdi-delete"
                      color="primary"
                      round
                      dense
                      flat
                      @click="videoDelete(videodevice.index)"
                    >
                      <q-tooltip :offset="[5, 5]"
                        >Delete Video Device</q-tooltip
                      >
                    </q-btn>
                  </template>
                </q-input>
                <q-input
                  label="Video Type"
                  v-model="videodevice.type"
                  readonly
                />
              </div>
            </q-tab-panel>
            <q-tab-panel name="sound">
              <div v-for="sounddevice in sounddevicesList" :key="sounddevice">
                <q-separator
                  color="primary"
                  spaced="lg"
                  v-if="sounddevice.index != 0"
                />
                <q-input label="Device Type" model-value="Sound" readonly>
                  <template v-slot:append>
                    <q-btn
                      icon="delete"
                      color="primary"
                      round
                      dense
                      flat
                      @click="soundDelete(sounddevice.index)"
                    >
                      <q-tooltip :offset="[5, 5]"
                        >Delete Sound Device</q-tooltip
                      >
                    </q-btn>
                  </template>
                </q-input>
                <q-input
                  label="Sound model"
                  v-model="sounddevice.model"
                  readonly
                />
              </div>
            </q-tab-panel>
            <q-tab-panel name="passthrough">
              <div v-for="usbdevice in usbdevicesList" :key="usbdevice">
                <q-input model-value="USB Device" label="Type" readonly>
                  <template v-slot:append>
                    <q-btn
                      flat
                      round
                      color="primary"
                      icon="delete"
                      @click="
                        usbdeviceDelete(
                          usbdevice.product_id,
                          usbdevice.vendor_id,
                        )
                      "
                    >
                      <q-tooltip :offset="[5, 5]">Delete USB Device</q-tooltip>
                    </q-btn>
                  </template>
                </q-input>
                <q-input v-model="usbdevice.name" label="Name" readonly />
                <q-input
                  v-model="usbdevice.vendor_id"
                  label="Vendor Id"
                  readonly
                />
                <q-input
                  v-model="usbdevice.product_id"
                  label="Product Id"
                  readonly
                />
              </div>
              <div v-for="pcidevice in pcidevicesList" :key="pcidevice">
                <q-separator
                  color="primary"
                  spaced="lg"
                  v-if="pcidevicesList.length > 0 && usbdevicesList.length >= 0"
                />
                <q-input model-value="PCI Device" label="Type" readonly>
                  <template v-slot:append>
                    <q-btn
                      color="primary"
                      icon="delete"
                      round
                      flat
                      @click="pciedeviceDelete(pcidevice.index)"
                    >
                      <q-tooltip :offset="[5, 5]">Delete PCI Device</q-tooltip>
                    </q-btn>
                  </template>
                </q-input>
                <q-input
                  v-model="pcidevice.path"
                  label="Device Path"
                  readonly
                />
                <q-input
                  v-model="pcidevice.vendor_name"
                  label="Vendor Name"
                  readonly
                />
                <q-input
                  v-model="pcidevice.product_name"
                  label="Product Name"
                  readonly
                />
                <q-input
                  v-if="pcidevice.custom_rom_file"
                  v-model="pcidevice.rom_file"
                  label="Rom File"
                  readonly
                />
              </div>
            </q-tab-panel>
            <q-tab-panel name="xml">
              <q-input filled v-model="xml" type="textarea" autogrow />
            </q-tab-panel>
          </q-tab-panels>
        </q-page>
        <!-- <q-footer bordered>
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
              label="Add Sound"
              @click="soundAdd()"
              v-if="tab == 'sound'"
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
              v-if="tab == 'memory' || tab == 'xml' || tab == 'cpu'"
            />
          </q-toolbar>
        </q-footer> -->
      </q-page-container>
    </q-layout>
    <q-inner-loading :showing="loading" />
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
  <ConfirmDialog ref="confirmDialog" />
  <AddDisk ref="addDisk" @disk-add-finished="refreshData()" />
  <AddNetwork ref="addNetwork" @network-add-finished="refreshData()" />
  <AddUsbDevice ref="addUsbDevice" @usb-device-add-finished="refreshData()" />
  <AddPcieDevice
    ref="addPcieDevice"
    @pcie-device-add-finished="refreshData()"
  />
  <AddGraphics ref="addGraphics" @graphics-add-finished="refreshData()" />
  <AddVideo ref="addVideo" @video-add-finished="refreshData()" />
  <AddSound ref="addSound" @sound-add-finished="refreshData()" />
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";
import AddDisk from "src/components/AddDisk.vue";
import AddNetwork from "src/components/AddNetwork.vue";
import AddUsbDevice from "src/components/AddUsbDevice.vue";
import AddPcieDevice from "src/components/AddPcieDevice.vue";
import AddGraphics from "src/components/AddGraphics.vue";
import AddVideo from "src/components/AddVideo.vue";
import AddSound from "src/components/AddSound.vue";
import ToolTip from "src/components/ToolTip.vue";

export default {
  data() {
    return {
      layout: ref(false),
      loading: false,
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
      memory_enable_shared: null,
      diskUnitOptions: ["MB", "GB", "TB"],
      diskDriverTypeOptions: ["raw", "qcow2"],
      diskBusOptions: ["sata", "scsi", "virtio", "usb"],
      diskTypeOptions: ["disk", "cdrom"],
      diskList: [],
      diskDeleteNumber: null,
      networkList: [],
      networkDeleteNumber: null,
      sounddevicesList: [],
      sounddeviceDeleteIndex: null,
      usbdevicesList: [],
      usbdeviceDeleteVendorId: null,
      usbdeviceDeleteProductId: null,
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
    AddNetwork,
    AddUsbDevice,
    AddPcieDevice,
    AddGraphics,
    AddVideo,
    AddSound,
    ToolTip,
  },
  methods: {
    show(uuid) {
      this.uuid = uuid;
      this.refreshData();
    },
    refreshData() {
      this.loading = true;
      this.layout = true;
      this.$api
        .get("/vm-manager/" + this.uuid + "/data")
        .then((response) => {
          console.log(response.data);
          this.general_name = response.data.name;
          this.general_machine = response.data.machine_type;
          this.general_bios = response.data.bios_type;
          this.general_autostart = response.data.autostart;
          this.memory_minMemory = response.data.memory_min;
          this.memory_minMemoryUnit = response.data.memory_min_unit;
          this.memory_maxMemory = response.data.memory_max;
          this.memory_maxMemoryUnit = response.data.memory_max_unit;
          this.memory_enable_shared = response.data.memory_enable_shared;
          this.currentVcpu = response.data.current_vcpu;
          this.cpu_model = response.data.cpu_mode;
          this.vcpu = response.data.vcpu;
          this.customTopology = response.data.cpu_custom_topology;
          this.topologySockets = response.data.cpu_topology_sockets;
          this.topologyDies = response.data.cpu_topology_dies;
          this.topologyCores = response.data.cpu_topology_cores;
          this.topologyThreads = response.data.cpu_topology_threads;
          this.diskList = response.data.disk_devices;
          this.networkList = response.data.network_devices;
          this.usbdevicesList = response.data.usb_devices;
          this.pcidevicesList = response.data.pci_devices;
          this.graphicsdevicesList = response.data.graphics_devices;
          this.videodevicesList = response.data.video_devices;
          this.sounddevicesList = response.data.sound_devices;
          this.xml = response.data.xml;
          this.loading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error loading VM data.", [
            error.response.data.detail,
          ]);
          this.loading = false;
        });
    },
    applyEdits() {
      this.loading = true;
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
              error.response.data.detail,
            ]);
          });
      } else if (this.tab == "cpu") {
        if (this.currentVcpu > this.vcpu) {
          this.$refs.errorDialog.show("VCPU error", [
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
              error.response.data.detail,
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
              error.response.data.detail,
            ]);
          });
      }
      this.loading = false;
    },
    generalChangeName(value) {
      this.loading = true;
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-general-name", {
          value: value,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error changing name", [
            error.response.data.detail,
          ]);
        });
    },
    diskChangeType(disknumber, value) {
      this.loading = true;
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
            error.response.data.detail,
          ]);
        });
    },
    diskChangeDriverType(disknumber, value) {
      this.loading = true;
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
            error.response.data.detail,
          ]);
        });
    },
    diskChangeBus(disknumber, value) {
      this.loading = true;
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
            error.response.data.detail,
          ]);
        });
    },
    diskChangeSourceFile(disknumber, value) {
      this.loading = true;
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
            error.response.data.detail,
          ]);
        });
    },
    diskChangeSourceDev(disknumber, value) {
      this.loading = true;
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
            error.response.data.detail,
          ]);
        });
    },
    diskChangeBootorder(disknumber, value) {
      this.loading = true;
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
            error.response.data.detail,
          ]);
        });
    },
    diskDelete(index) {
      this.$refs.confirmDialog.show(
        "Delete disk",
        [
          "Are you sure you want to delete this disk?",
          "This only removes the disk from the vm, not the file itself.",
        ],
        this.diskDeleteConfirm,
      );
      this.diskDeleteNumber = index;
    },
    diskDeleteConfirm() {
      this.loading = true;
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-disk-delete", {
          index: this.diskDeleteNumber,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting disk", [
            error.response.data.detail,
          ]);
          this.loading = false;
        });
    },
    diskAdd() {
      this.$refs.addDisk.show(this.uuid);
    },
    networkAdd() {
      this.$refs.addNetwork.show(this.uuid);
    },
    networkDelete(networknumber) {
      this.$refs.confirmDialog.show(
        "Delete network",
        ["Are you sure you want to delete this network?"],
        this.networkDeleteConfirm,
      );
      this.networkDeleteNumber = networknumber;
    },
    networkDeleteConfirm() {
      this.loading = true;
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-network-delete", {
          number: this.networkDeleteNumber,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting network", [
            error.response.data.detail,
          ]);
          this.loading = false;
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
      this.loading = true;
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-general-autostart", {
          value: this.general_autostart,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error changing autostart", [
            error.response.data.detail,
          ]);
        });
    },
    usbdeviceAdd() {
      this.$refs.addUsbDevice.show(this.uuid);
    },
    usbdeviceDelete(productid, vendorid) {
      this.$refs.confirmDialog.show(
        "Remove USB device",
        ["Are you sure you want to remove this usb device?"],
        this.usbdeviceDeleteConfirm,
      );
      this.usbdeviceDeleteProductId = productid;
      this.usbdeviceDeleteVendorId = vendorid;
    },
    usbdeviceDeleteConfirm() {
      this.loading = true;
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-usb-delete", {
          product_id: this.usbdeviceDeleteProductId,
          vendor_id: this.usbdeviceDeleteVendorId,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting usb device", [
            error.response.data.detail,
          ]);
          this.loading = false;
        });
    },
    pciedeviceAdd() {
      this.$refs.addPcieDevice.show(this.uuid);
    },
    pciedeviceDelete(index) {
      this.loading = true;
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-pcie-delete", {
          index: index,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting pcie device", [
            error.response.data.detail,
          ]);
        });
    },
    graphicsAdd() {
      this.$refs.addGraphics.show(this.uuid);
    },
    graphicsDelete(index) {
      this.loading = true;
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-graphics-delete", {
          index: index,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting graphics", [
            error.response.data.detail,
          ]);
          this.loading = false;
        });
    },
    videoAdd() {
      this.$refs.addVideo.show(this.uuid);
    },
    videoDelete(index) {
      this.loading = true;
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-video-delete", {
          index: index,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting video", [
            error.response.data.detail,
          ]);
          this.loading = false;
        });
    },
    soundDelete(index) {
      this.sounddeviceDeleteIndex = index;
      this.$refs.confirmDialog.show(
        "Remove Sound device",
        ["Are you sure you want to remove this sound device?"],
        this.soundDeleteConfirm,
      );
    },
    soundDeleteConfirm() {
      this.loading = true;
      this.$api
        .post("/vm-manager/" + this.uuid + "/edit-sound-delete", {
          index: this.sounddeviceDeleteIndex,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting sound", [
            error.response.data.detail,
          ]);
          this.loading = false;
        });
    },

    soundAdd() {
      this.$refs.addSound.show(this.uuid);
    },
  },
};
</script>
