<template>
  <q-dialog v-model="layout" full-width full-height :maximized="$q.screen.lt.md">
    <q-layout
      view="hHh lpR fFf"
      container
      :class="{ 'bg-dark': $q.dark.isActive, 'bg-white': !$q.dark.isActive }"
    >
      <q-header bordered>
        <q-toolbar class="row items-center" v-if="$q.screen.gt.xs">
          <div style="width: 10em" class="text-left">
            <p class="text-h6 q-ma-none">Edit VM</p>
          </div>
          <q-space />
          <q-tabs v-model="tab">
            <q-tab name="general" label="General" />
            <q-tab name="devices" label="Devices" />
          </q-tabs>
          <q-space />
          <div style="width: 10em" class="text-right">
            <q-btn icon="close" flat round dense v-close-popup @click="$emit('finished')">
              <ToolTip content="Close" />
            </q-btn>
          </div>
        </q-toolbar>
        <q-toolbar v-if="$q.screen.lt.sm">
          <q-toolbar-title class="text-h6">Edit VM</q-toolbar-title>
          <q-btn icon="close" flat round dense v-close-popup @click="$emit('finished')">
            <ToolTip content="Close" />
          </q-btn>
        </q-toolbar>
        <q-tabs v-model="tab" v-if="$q.screen.lt.sm">
          <q-tab name="general" label="General" />
          <q-tab name="devices" label="Devices" />
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
                      <div class="col q-ma-sm">
                        <q-input label="Name" v-model="vm.name" />
                      </div>
                      <div class="col q-ma-sm">
                        <q-select
                          label="Video Type"
                          v-model="vm.video_type"
                          :options="video_types"
                          type="number"
                          min="1"
                        />
                      </div>
                    </div>
                    <div class="row items-center q-mt-md">
                      <q-toggle v-model="vm.autostart" left-label label="Autostart:">
                        <ToolTip content="Automatically start the VM when the server boots" />
                      </q-toggle>
                    </div>
                  </q-card-section>
                </q-card>
                <q-card>
                  <q-card-section class="row q-pb-none">
                    <p class="text-h6 q-ma-none">Memory</p>
                  </q-card-section>
                  <q-card-section class="q-pt-none">
                    <div class="row">
                      <div class="col q-mr-lg">
                        <q-input
                          label="Current allocation"
                          v-model="vm.memory_min"
                          type="number"
                          min="1"
                        >
                          <template v-slot:append>
                            <q-select v-model="memory_minMemoryUnit" :options="memoryUnitOptions" />
                          </template>
                        </q-input>
                      </div>
                      <div class="col q-ml-lg">
                        <q-input
                          label="Maximum allocation"
                          v-model="vm.memory_max"
                          type="number"
                          min="1"
                        >
                          <template v-slot:append>
                            <q-select v-model="memory_maxMemoryUnit" :options="memoryUnitOptions" />
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
                        v-model="vm.cpu_model"
                        :options="cpu_model_options"
                        @update:model-value="calculateCpu"
                      />
                      <q-input
                        label="Current vCPU"
                        v-model="vm.vcpu_current"
                        type="number"
                        min="1"
                        :max="vm.vcpu"
                        :rules="[
                          (val) =>
                            val <= vm.vcpu || 'Current vCPU cannot be bigger than vCPU value',
                        ]"
                        :readonly="vm.vcpu_custom_topology"
                      />
                      <q-input
                        label="vCPU"
                        v-model="vm.vcpu"
                        type="number"
                        min="1"
                        @update:model-value="(val) => (cpu_topology_sockets = val)"
                        :readonly="vm.vcpu_custom_topology"
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
                          v-model="vm.vcpu_custom_topology"
                          @update:model-value="calculateCpu"
                        />
                      </div>
                      <q-input
                        label="Sockets"
                        v-model="vm.vcpu_custom_topology_sockets"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!vm.vcpu_custom_topology"
                      />
                      <q-input
                        label="Dies"
                        v-model="vm.vcpu_custom_topology_dies"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!vm.vcpu_custom_topology"
                      />
                      <q-input
                        label="Cores"
                        v-model="vm.vcpu_custom_topology_cores"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!vm.vcpu_custom_topology"
                      />
                      <q-input
                        label="Threads"
                        v-model="vm.vcpu_custom_topology_threads"
                        type="number"
                        min="1"
                        @update:model-value="calculateCpu"
                        :readonly="!vm.vcpu_custom_topology"
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
                    <q-btn flat round color="primary" icon="add" @click="deviceAdd()">
                      <ToolTip content="Add Device" />
                    </q-btn>
                  </div>
                  <q-separator class="q-mt-xs" />
                  <q-scroll-area style="height: 92%" class="devices_scroll_area">
                    <q-list>
                      <q-item
                        clickable
                        v-ripple
                        v-for="(disk, index) in vm.devices_disk_file"
                        :key="disk"
                        :active="disk.active"
                        @click="deviceSelect('disk-file', disk, index)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon
                            color="primary"
                            :name="disk.device_type == 'cdrom' ? 'mdi-disc' : 'mdi-harddisk'"
                          />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>
                            {{ disk.disk_bus == 'virtio' ? 'VirtIO' : disk.disk_bus.toUpperCase() }}
                            {{
                              disk.device_type == 'cdrom'
                                ? 'CDROM'
                                : disk.device_type == 'disk'
                                  ? 'Disk'
                                  : disk.device_type
                            }}
                            {{ disk.index }}
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item
                        clickable
                        v-ripple
                        v-for="(disk, index) in vm.devices_disk_block"
                        :key="disk"
                        :active="disk.active"
                        @click="deviceSelect('disk-block', disk, index)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon
                            color="primary"
                            :name="disk.device_type == 'cdrom' ? 'mdi-disc' : 'mdi-harddisk'"
                          />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>
                            {{ disk.disk_bus == 'virtio' ? 'VirtIO' : disk.disk_bus.toUpperCase() }}
                            {{
                              disk.device_type == 'cdrom'
                                ? 'CDROM'
                                : disk.device_type == 'disk'
                                  ? 'Block Disk'
                                  : disk.device_type
                            }}
                            {{ disk.index }}
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item
                        clickable
                        v-ripple
                        v-for="(disk, index) in vm.devices_disk_iscsi"
                        :key="disk"
                        :active="disk.active"
                        @click="deviceSelect('disk-iscsi', disk, index)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon
                            color="primary"
                            :name="disk.device_type == 'cdrom' ? 'mdi-disc' : 'mdi-harddisk'"
                          />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label>
                            {{ disk.disk_bus == 'virtio' ? 'VirtIO' : disk.disk_bus.toUpperCase() }}
                            {{
                              disk.device_type == 'cdrom'
                                ? 'CDROM'
                                : disk.device_type == 'disk'
                                  ? 'iSCSI Disk'
                                  : disk.device_type
                            }}
                            {{ disk.index }}
                          </q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item
                        clickable
                        v-ripple
                        v-for="(pci, index) in vm.devices_pci"
                        :key="pci"
                        :active="pci.active"
                        @click="deviceSelect('pci', pci, index)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon color="primary" name="mdi-expansion-card" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label> PCI Device {{ index + 1 }} </q-item-label>
                        </q-item-section>
                      </q-item>
                      <q-item
                        clickable
                        v-ripple
                        v-for="(network, index) in vm.devices_network"
                        :key="network"
                        :active="network.active"
                        @click="deviceSelect('network', network, index)"
                      >
                        <q-item-section thumbnail class="q-pr-sm">
                          <q-icon color="primary" name="mdi-ethernet" />
                        </q-item-section>
                        <q-item-section>
                          <q-item-label> Network Interface {{ index + 1 }} </q-item-label>
                        </q-item-section>
                      </q-item>
                    </q-list>
                  </q-scroll-area>
                </div>
                <q-separator vertical />
                <div class="col q-ml-md">
                  <div class="row text-center items-center">
                    <div class="col text-h6">
                      {{
                        selectedDeviceTitle == null
                          ? 'Select a device to edit'
                          : selectedDeviceTitle
                      }}
                    </div>
                    <q-space />
                    <q-btn
                      flat
                      round
                      color="primary"
                      icon="check"
                      disable
                      v-if="selectedDevice != null"
                    >
                      <ToolTip content="Apply Changes" />
                    </q-btn>
                    <q-btn
                      flat
                      round
                      color="primary"
                      icon="delete"
                      @click="deviceDeleteInit()"
                      v-if="selectedDevice != null"
                    >
                      <ToolTip content="Delete Device" />
                    </q-btn>
                  </div>
                  <div v-if="selectedDeviceType == 'disk-file'">
                    <q-input label="Name" v-model="selectedDevice.name" readonly />
                    <q-input label="Device Type" v-model="selectedDevice.device_type" readonly />
                    <q-input label="Disk Bus" v-model="selectedDevice.disk_bus" readonly />
                    <q-input
                      label="Source File"
                      v-model="selectedDevice.disk_source_file"
                      readonly
                    />
                  </div>
                  <div v-if="selectedDeviceType == 'disk-block'">
                    <q-input label="Name" v-model="selectedDevice.name" readonly />
                    <q-input label="Device Type" v-model="selectedDevice.device_type" readonly />
                    <q-input label="Disk Bus" v-model="selectedDevice.disk_bus" readonly />
                    <q-input
                      label="Source Block Device"
                      v-model="selectedDevice.disk_source_block"
                      readonly
                    />
                  </div>
                  <div v-if="selectedDeviceType == 'disk-iscsi'">
                    <q-input label="Name" v-model="selectedDevice.name" readonly />
                    <q-input label="Device Type" v-model="selectedDevice.device_type" readonly />
                    <q-input label="Disk Bus" v-model="selectedDevice.disk_bus" readonly />
                    <q-input
                      label="iSCSI Name (IQN)"
                      v-model="selectedDevice.iscsi_name"
                      readonly
                    />
                    <q-input label="iSCSI Host" v-model="selectedDevice.iscsi_host" readonly />
                    <q-input label="iSCSI Port" v-model="selectedDevice.iscsi_port" readonly />
                  </div>
                  <div v-if="selectedDeviceType == 'pci'">
                    <q-input label="Name" v-model="selectedDevice.name" readonly />
                    <q-input label="Domain" v-model="selectedDevice.domain" readonly />
                    <q-input label="Bus" v-model="selectedDevice.bus" readonly />
                    <q-input label="Slot" v-model="selectedDevice.slot" readonly />
                    <q-input label="Function" v-model="selectedDevice.function" readonly />
                    <q-checkbox
                      label="Use Custom ROM"
                      v-model="selectedDevice.rom_use"
                      readonly
                      disable
                    />
                    <q-input
                      v-if="selectedDevice.rom_use"
                      label="ROM File"
                      v-model="selectedDevice.rom_file"
                      readonly
                    />
                  </div>
                  <div v-if="selectedDeviceType == 'network'">
                    <q-input label="Name" v-model="selectedDevice.name" readonly />
                    <q-input label="Type" v-model="selectedDevice.type" readonly />
                    <q-input
                      label="Libvirt network"
                      v-model="selectedDevice.libvirt_name"
                      readonly
                    />
                    <q-input
                      v-if="selectedDevice.mac"
                      label="MAC Address"
                      v-model="selectedDevice.mac"
                      readonly
                    />
                  </div>
                </div>
              </div>
            </q-tab-panel>
          </q-tab-panels>
        </q-page>
      </q-page-container>
      <q-footer v-if="tab == 'general'">
        <div class="row q-pa-sm">
          <q-space />
          <q-btn flat rounded icon-right="check" v-if="tab == 'general'" @click="generalApply">
            <ToolTip content="Apply changes" />
          </q-btn>
        </div>
      </q-footer>
    </q-layout>
    <q-inner-loading :showing="loading" />
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
  <ConfirmDialog ref="confirmDialog" />
  <AddDevice ref="addDevice" @finished="getdata" />
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
import ErrorDialog from 'src/components/ErrorDialog.vue'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import ToolTip from 'src/components/ToolTip.vue'
import AddDevice from './AddDevice.vue'
import { useApi } from 'src/composables/useApi'

export default {
  data() {
    return {
      vmid: null,
      vm: null,
      layout: false,
      loading: false,
      tab: 'general',
      cpu_model_options: ['host-model', 'host-passthrough'],
      memoryUnitOptions: ['B', 'KiB', 'MiB', 'GiB'],
      memory_minMemoryUnit: 'B',
      memory_maxMemoryUnit: 'B',
      video_types: ['virtio', 'qxl', 'vga'],
      selectedDeviceTitle: null,
      selectedDevice: null,
      selectedDeviceType: null,
    }
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
    ToolTip,
    AddDevice,
  },
  emits: ['finished'],
  methods: {
    show(id) {
      this.vmid = id
      this.vm = null
      this.tab = 'general'
      this.getdata()
    },
    getdata() {
      this.selectedDevice = null
      this.selectedDeviceType = null
      this.selectedDeviceTitle = null
      this.resetSelectedDevices()

      const api = useApi()
      api.vm
        .get(this.vmid)
        .then((data) => {
          this.layout = true
          this.vm = JSON.parse(JSON.stringify(data))
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error?.detail || error.message)
        })
    },
    resetSelectedDevices() {
      if (this.vm !== null) {
        this.vm.devices_network.forEach((element) => {
          element.active = false
        })
        this.vm.devices_disk_file.forEach((element) => {
          element.active = false
        })
        this.vm.devices_disk_block.forEach((element) => {
          element.active = false
        })
        this.vm.devices_disk_iscsi.forEach((element) => {
          element.active = false
        })
        this.vm.devices_pci.forEach((element) => {
          element.active = false
        })
      }
    },
    deviceSelect(type, device, index = null) {
      this.selectedDevice = device
      this.selectedDeviceType = type
      if (this.selectedDeviceType == 'disk-file') {
        this.resetSelectedDevices()
        this.vm.devices_disk_file[index].active = true
        this.selectedDeviceTitle = 'Disk ' + (index + 1)
      } else if (this.selectedDeviceType == 'disk-block') {
        this.resetSelectedDevices()
        this.vm.devices_disk_block[index].active = true
        this.selectedDeviceTitle = 'Disk (Block)' + (index + 1)
      } else if (this.selectedDeviceType == 'disk-iscsi') {
        this.resetSelectedDevices()
        this.vm.devices_disk_iscsi[index].active = true
        this.selectedDeviceTitle = 'Disk (iSCSI) ' + (index + 1)
      } else if (this.selectedDeviceType == 'pci') {
        this.resetSelectedDevices()
        this.vm.devices_pci[index].active = true
        this.selectedDeviceTitle = 'PCI Device ' + (index + 1)
      } else if (this.selectedDeviceType == 'network') {
        this.resetSelectedDevices()
        this.vm.devices_network[index].active = true
        this.selectedDeviceTitle = 'Network Interface ' + (index + 1)
      }
    },
    deviceDeleteInit() {
      this.$refs.confirmDialog.show(
        'Delete Device',
        ['Are you sure you want to delete this device?'],
        this.deleteDevice,
        () => {},
      )
    },
    deleteDevice() {
      // Remove device from local VM object
      if (this.selectedDeviceType == 'network') {
        const index = this.vm.devices_network.findIndex(d => d.id === this.selectedDevice.id)
        if (index > -1) this.vm.devices_network.splice(index, 1)
      } else if (this.selectedDeviceType == 'disk-file') {
        const index = this.vm.devices_disk_file.findIndex(d => d.id === this.selectedDevice.id)
        if (index > -1) this.vm.devices_disk_file.splice(index, 1)
      } else if (this.selectedDeviceType == 'disk-block') {
        const index = this.vm.devices_disk_block.findIndex(d => d.id === this.selectedDevice.id)
        if (index > -1) this.vm.devices_disk_block.splice(index, 1)
      } else if (this.selectedDeviceType == 'disk-iscsi') {
        const index = this.vm.devices_disk_iscsi.findIndex(d => d.id === this.selectedDevice.id)
        if (index > -1) this.vm.devices_disk_iscsi.splice(index, 1)
      } else if (this.selectedDeviceType == 'pci') {
        const index = this.vm.devices_pci.findIndex(d => d.id === this.selectedDevice.id)
        if (index > -1) this.vm.devices_pci.splice(index, 1)
      }

      // Save the changes
      this.generalApply()
    },
    deviceAdd() {
      this.$refs.addDevice.show(this.vmid)
    },
    generalApply() {
      const api = useApi()
      // Remove 'active' properties added by UI and 'status' from the VM object
      const vmToSend = JSON.parse(JSON.stringify(this.vm))
      delete vmToSend.status

      // Remove UI-only properties from devices
      vmToSend.devices_network?.forEach(d => delete d.active)
      vmToSend.devices_disk_file?.forEach(d => delete d.active)
      vmToSend.devices_disk_block?.forEach(d => delete d.active)
      vmToSend.devices_disk_iscsi?.forEach(d => delete d.active)
      vmToSend.devices_pci?.forEach(d => delete d.active)

      api.vm
        .update(this.vmid, vmToSend)
        .then(() => {
          this.getdata()
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error?.detail || error.message)
        })
    },
    calculateCpu() {
      return
    },
    //   calculateCpu() {
    //     this.vcpu =
    //       this.cpu_topology_sockets *
    //       this.cpu_topology_dies *
    //       this.cpu_topology_cores *
    //       this.cpu_topology_threads;
    //     this.current_vcpu = this.vcpu;
    //   },
  },
}
</script>
