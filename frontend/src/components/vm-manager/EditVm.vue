<template>
  <q-dialog
    v-model="layout"
    full-width
    full-height
    :maximized="$q.screen.lt.md"
  >
    <q-layout
      view="hHh lpR fFf"
      container
      :class="{ 'bg-dark': $q.dark.isActive, 'bg-white': !$q.dark.isActive }"
    >
      <q-header bordered>
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
        <q-toolbar class="row items-center" v-if="$q.screen.gt.sm">
          <div style="width: 10em" class="text-left">
            <p class="text-h6 q-ma-none">Edit VM</p>
          </div>
          <q-space />
          <q-tabs v-model="tab">
            <q-tab name="general" label="General" />
            <q-tab name="devices" label="Devices" />
            <q-tab name="passthrough" label="Passthrough" />
            <q-tab name="xml" label="Xml" />
          </q-tabs>
          <q-space />
          <div style="width: 10em" class="text-right">
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
          </div>
        </q-toolbar>
        <q-toolbar v-if="$q.screen.lt.md">
          <q-toolbar-title class="text-h6">Edit VM</q-toolbar-title>
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
        <q-tabs v-model="tab" v-if="$q.screen.lt.md">
          <q-tab name="general" label="General" />
          <q-tab name="devices" label="Devices" />
          <q-tab name="passthrough" label="Passthrough" />
          <q-tab name="xml" label="Xml" />
        </q-tabs>
      </q-header>

      <q-page-container>
        <q-page padding class="row q-pa-md">
          <q-tab-panels v-model="tab" style="width: 100%">
            <q-tab-panel name="general">
              <div class="justify-center q-gutter-md">
                <q-card>
                  <q-card-section>
                    <div class="row">
                      <div class="col q-mr-lg">
                        <q-input label="Name" v-model="name" />
                        <div class="row items-center q-mt-md">
                          <p class="text-body2 q-ma-none">Autostart:</p>
                          <q-toggle v-model="autostart" />
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
                          v-model="machine_type"
                          readonly
                        />
                        <q-input label="BIOS" v-model="bios_type" readonly />
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
                        v-model="cpu_mode"
                        :options="cpu_mode_options"
                        @update:model-value="calculateCpu"
                      />
                      <q-input
                        label="Current vCPU"
                        v-model="current_vcpu"
                        type="number"
                        min="1"
                        :max="vcpu"
                        :rules="[
                          (val) =>
                            val <= vcpu ||
                            'Current vCPU cannot be bigger than vCPU value',
                        ]"
                        :readonly="cpu_custom_topology"
                      />
                      <q-input
                        label="vCPU"
                        v-model="vcpu"
                        type="number"
                        min="1"
                        @update:model-value="(val) => (cpu_topology_sockets = val)"
                        :readonly="cpu_custom_topology"
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
                          v-model="cpu_custom_topology"
                          @update:model-value="calculateCpu"
                        />
                      </div>
                      <q-input
                        label="Sockets"
                        v-model="cpu_topology_sockets"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!cpu_custom_topology"
                      />
                      <q-input
                        label="Dies"
                        v-model="cpu_topology_dies"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!cpu_custom_topology"
                      />
                      <q-input
                        label="Cores"
                        v-model="cpu_topology_cores"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!cpu_custom_topology"
                      />
                      <q-input
                        label="Threads"
                        v-model="cpu_topology_threads"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!cpu_custom_topology"
                      />
                    </div>
                  </q-card-section>
                </q-card>
              </div>
            </q-tab-panel>
            <q-tab-panel name="devices" class="q-pa-none">
              <div class="row full-height">
                <div class="col-">
                  <div class="row items-center" style="height: 7%">
                    <p class="text-h6 q-ma-none">Devices</p>
                    <q-space />
                    <q-btn
                      flat
                      round
                      color="primary"
                      icon="add"
                      @click="addDevice()"
                    >
                      <q-tooltip :offset="[5, 5]">Add Device</q-tooltip>
                    </q-btn>
                  </div>
                  <q-separator class="q-mt-xs" />
                  <q-scroll-area
                    style="height: 92%"
                    class="devices_scroll_area"
                  >
                    <q-list>
                      <q-item
                        clickable
                        v-ripple
                        v-for="disk in disk_devices"
                        :key="disk"
                        :active="disk.active"
                        @click="setSelectedDevice('disk', disk)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon
                            color="primary"
                            :name="
                              disk.device_type == 'cdrom'
                                ? 'mdi-disc'
                                : 'mdi-harddisk'
                            "
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
                      <q-item
                        clickable
                        v-ripple
                        v-for="network in network_devices"
                        :key="network"
                        :active="network.active"
                        @click="setSelectedDevice('network', network)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon color="primary" name="mdi-ethernet" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>
                            Network Interface {{ network.number }}
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item
                        clickable
                        v-ripple
                        v-for="graphics in graphics_devices"
                        :key="graphics"
                        :active="graphics.active"
                        @click="setSelectedDevice('graphics', graphics)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon color="primary" name="mdi-monitor" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>
                            Display {{ graphics.type.toUpperCase() }}
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item
                        clickable
                        v-ripple
                        v-for="video in video_devices"
                        :key="video"
                        :active="video.active"
                        @click="setSelectedDevice('video', video)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon color="primary" name="mdi-monitor" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>
                            Video
                            {{
                              video.type == "virtio"
                                ? "VirtIO"
                                : video.type.toUpperCase()
                            }}
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item
                        clickable
                        v-ripple
                        v-for="sound in sound_devices"
                        :key="sound"
                        :active="sound.active"
                        @click="setSelectedDevice('sound', sound)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon color="primary" name="mdi-volume-high" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label> Sound {{ sound.model }} </q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-scroll-area>
                </div>
                <q-separator vertical />
                <div class="col q-ml-md">
                  <div class="row">
                    <p class="text-h6 q-ma-none">
                      {{
                        selectedDeviceTitle == null
                          ? "Select a device to edit"
                          : selectedDeviceTitle
                      }}
                    </p>
                    <q-space />
                    <q-btn flat round color="primary" icon="check" disable>
                      <ToolTip content="Apply Changes" />
                    </q-btn>
                    <q-btn
                      flat
                      round
                      color="primary"
                      icon="delete"
                      @click="deviceDelete(selectedDevice.index)"
                    >
                      <ToolTip content="Delete Device" />
                    </q-btn>
                  </div>
                  <div v-if="selectedDeviceType == 'disk'">
                    <q-input
                      label="Device Type"
                      v-model="selectedDevice.device_type"
                      readonly
                    />
                    <q-input
                      label="Driver Type"
                      v-model="selectedDevice.driver_type"
                      readonly
                    />
                    <q-input
                      label="Bus Format"
                      v-model="selectedDevice.bus_format"
                      readonly
                    />
                    <q-input
                      :label="
                        selectedDevice.read_only
                          ? 'Source File (Read Only)'
                          : 'Source File'
                      "
                      v-model="selectedDevice.source_file"
                      v-if="selectedDevice.source_file != null"
                      readonly
                    />
                    <q-input
                      label="Source Device"
                      v-model="selectedDevice.source_device"
                      v-if="selectedDevice.source_device != null"
                      readonly
                    />
                    <q-input
                      label="Boot order"
                      v-model="selectedDevice.boot_order"
                      v-if="selectedDevice.boot_order != null"
                      type="number"
                      min="1"
                      readonly
                    />
                  </div>
                  <div v-if="selectedDeviceType == 'network'">
                    <q-input
                      label="Source"
                      v-model="selectedDevice.source"
                      readonly
                    />
                    <q-input
                      label="Model"
                      v-model="selectedDevice.model"
                      readonly
                    />
                    <q-input
                      label="MAC Address"
                      v-model="selectedDevice.mac_address"
                      readonly
                    />
                  </div>
                  <div v-if="selectedDeviceType == 'graphics'">
                    <q-input
                      label="Device Type"
                      model-value="Graphics"
                      readonly
                    />
                    <q-input
                      label="Type"
                      v-model="selectedDevice.type"
                      readonly
                    />
                  </div>
                  <div v-if="selectedDeviceType == 'video'">
                    <q-input label="Device Type" model-value="Video" readonly />
                    <q-input
                      label="Model"
                      v-model="selectedDevice.type"
                      readonly
                    />
                  </div>
                  <div v-if="selectedDeviceType == 'sound'">
                    <q-input label="Device Type" model-value="Sound" readonly />
                    <q-input
                      label="Sound model"
                      v-model="selectedDevice.model"
                      readonly
                    />
                  </div>
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
              <div v-for="usbdevice in usb_devices" :key="usbdevice">
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
              <div v-for="pcidevice in pci_devices" :key="pcidevice">
                <q-separator
                  color="primary"
                  spaced="lg"
                  v-if="pci_devices.length > 0 && usb_devices.length >= 0"
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
            <q-tab-panel name="xml" class="q-pa-none">
              <q-input filled v-model="xml" type="textarea" autogrow />
            </q-tab-panel>
          </q-tab-panels>
        </q-page>
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

<style lang="scss" scoped>
body.screen--xs {
  .devices_scroll_area {
    width: 8em;
  }
}

body.screen--sm {
  .devices_scroll_area {
    width: 15em;
  }
}

body.screen--md {
  .devices_scroll_area {
    width: 15em;
  }
}

body.screen--lg {
  .devices_scroll_area {
    width: 15em;
  }
}

body.screen--xl {
  .devices_scroll_area {
    width: 15em;
  }
}
</style>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";
import AddDisk from "src/components/vm-manager/AddDisk.vue";
import AddNetwork from "src/components/vm-manager/AddNetwork.vue";
import AddUsbDevice from "src/components/vm-manager/AddUsbDevice.vue";
import AddPcieDevice from "src/components/vm-manager/AddPcieDevice.vue";
import AddGraphics from "src/components/vm-manager/AddGraphics.vue";
import AddVideo from "src/components/vm-manager/AddVideo.vue";
import AddSound from "src/components/vm-manager/AddSound.vue";
import ToolTip from "src/components/ToolTip.vue";

export default {
  data() {
    return {
      layout: false,
      loading: false,
      tab: "general",
      name: null,
      machine_type: null,
      bios_type: null,
      autostart: null,
      memoryUnitOptions: ["MB", "GB", "TB"],
      memory_minMemory: null,
      memory_minMemoryUnit: "GB",
      memory_maxMemory: null,
      memory_maxMemoryUnit: "GB",
      memory_enable_shared: null,
      disk_devices: [],
      network_devices: [],
      sound_devices: [],
      usb_devices: [],
      pci_devices: [],
      cpu_mode_options: ["host-model", "host-passthrough"],
      cpu_mode: null,
      current_vcpu: null,
      vcpu: null,
      cpu_custom_topology: false,
      cpu_topology_sockets: null,
      cpu_topology_dies: null,
      cpu_topology_cores: null,
      cpu_topology_threads: null,
      graphics_devices: [],
      video_devices: [],
      xml: null,
      selectedDeviceType: null,
      selectedDeviceTitle: null,
      selectedDevice: null,
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
          this.name = response.data.name;
          this.machine_type = response.data.machine_type;
          this.bios_type = response.data.bios_type;
          this.autostart = response.data.autostart;
          this.memory_minMemory = response.data.memory_min;
          this.memory_minMemoryUnit = response.data.memory_min_unit;
          this.memory_maxMemory = response.data.memory_max;
          this.memory_maxMemoryUnit = response.data.memory_max_unit;
          this.memory_enable_shared = response.data.memory_enable_shared;
          this.current_vcpu = response.data.current_vcpu;
          this.cpu_mode = response.data.cpu_mode;
          this.vcpu = response.data.vcpu;
          this.cpu_custom_tpology = response.data.cpu_custom_topology;
          this.cpu_topology_sockets = response.data.cpu_topology_sockets;
          this.cpu_topology_dies = response.data.cpu_topology_dies;
          this.cpu_topology_cores = response.data.cpu_topology_cores;
          this.cpu_topology_threads = response.data.cpu_topology_threads;
          this.disk_devices = response.data.disk_devices;
          this.network_devices = response.data.network_devices;
          this.usb_devices = response.data.usb_devices;
          this.pci_devices = response.data.pci_devices;
          this.graphics_devices = response.data.graphics_devices;
          this.video_devices = response.data.video_devices;
          this.sound_devices = response.data.sound_devices;
          this.xml = response.data.xml;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error loading VM data.", [
            error.response.data.detail,
          ]);
        })
        .finally(() => {
          this.loading = false;
        });
    },
    setSelectedDevice(deviceType, device) {
      this.selectedDeviceType = deviceType;
      this.selectedDevice = device;
      this.disk_devices.forEach((disk) => {
        if (deviceType == "disk" && disk.index == device.index) {
          this.selectedDeviceTitle =
            (disk.bus_format == "virtio"
              ? "VirtIO"
              : disk.bus_format.toUpperCase()) +
            " " +
            (disk.device_type == "cdrom"
              ? "CDROM"
              : disk.device_type == "disk"
              ? "Disk"
              : disk.device_type) +
            " " +
            disk.index;
          disk.active = true;
        } else {
          disk.active = false;
        }
      });
      this.network_devices.forEach((network) => {
        if (deviceType == "network" && network.number == device.number) {
          this.selectedDeviceTitle = "Network Interface " + network.number;
          network.active = true;
        } else {
          network.active = false;
        }
      });
      this.graphics_devices.forEach((graphicsdevice) => {
        if (deviceType == "graphics" && graphicsdevice.index == device.index) {
          this.selectedDeviceTitle =
            "Display " + graphicsdevice.type.toUpperCase();
          graphicsdevice.active = true;
        } else {
          graphicsdevice.active = false;
        }
      });
      this.video_devices.forEach((videodevice) => {
        if (deviceType == "video" && videodevice.index == device.index) {
          this.selectedDeviceTitle =
            "Video " +
            (videodevice.type == "virtio"
              ? "VirtIO"
              : videodevice.type.toUpperCase());
          videodevice.active = true;
        } else {
          videodevice.active = false;
        }
      });
      this.sound_devices.forEach((sounddevice) => {
        if (deviceType == "sound" && sounddevice.index == device.index) {
          this.selectedDeviceTitle = "Sound " + sounddevice.model;
          sounddevice.active = true;
        } else {
          sounddevice.active = false;
        }
      });
    },
    deviceDelete() {
      this.$refs.confirmDialog.show(
        "Delete device",
        ["Are you sure you want to delete this device?"],
        this.deviceDeleteConfirm,
      );
    },
    deviceDeleteConfirm() {
      console.log("device type:", this.selectedDeviceType);
      console.log("device:", this.selectedDevice);
      if (this.selectedDeviceType == "disk"){
        this.$api.post("/vm-manager/" + this.uuid + "/edit-disk-delete", {
          index: this.selectedDevice.index,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting disk", [
            error.response.data.detail,
          ]);
        });
      } else if (this.selectedDeviceType == "network"){
        this.$api.post("/vm-manager/" + this.uuid + "/edit-network-delete", {
          number: this.selectedDevice.number,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting network", [
            error.response.data.detail,
          ]);
        });
      } else if (this.selectedDeviceType == "graphics"){
        this.$api.post("/vm-manager/" + this.uuid + "/edit-graphics-delete", {
          index: this.selectedDevice.index,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting graphics", [
            error.response.data.detail,
          ]);
        });
      } else if (this.selectedDeviceType == "video"){
        this.$api.post("/vm-manager/" + this.uuid + "/edit-video-delete", {
          index: this.selectedDevice.index,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting video", [
            error.response.data.detail,
          ]);
        });
      } else if (this.selectedDeviceType == "sound"){
        this.$api.post("/vm-manager/" + this.uuid + "/edit-sound-delete", {
          index: this.selectedDevice.index,
        })
        .then((response) => {
          this.refreshData();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting sound", [
            error.response.data.detail,
          ]);
        });
      }
      else {
        this.$refs.errorDialog.show("Error deleting device", [
          "Device type not recognized",
        ]);
      }
    },
    calculateCpu() {
      this.vcpu =
        this.cpu_topology_sockets *
        this.cpu_topology_dies *
        this.cpu_topology_cores *
        this.cpu_topology_threads;
      this.current_vcpu = this.vcpu;
    },
  },
};
</script>
