<template>
  <q-dialog v-model="layout">
    <q-card style="min-width: 60vw">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add Device</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section v-if="optionLayout">
        <q-list bordered>
          <q-item
            clickable
            v-ripple
            :active="option === 'disk-file'"
            @click="option = 'disk-file'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon color="primary" name="mdi-harddisk" />
            </q-item-section>
            <q-item-section>Disk (file)</q-item-section>
          </q-item>
          <q-item
            clickable
            v-ripple
            :active="option === 'disk-block'"
            @click="option = 'disk-block'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon color="primary" name="mdi-harddisk" />
            </q-item-section>
            <q-item-section>Disk (Block)</q-item-section>
          </q-item>
          <q-item
            clickable
            v-ripple
            :active="option === 'disk-iscsi'"
            @click="option = 'disk-iscsi'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon color="primary" name="mdi-harddisk" />
            </q-item-section>
            <q-item-section>Disk (iSCSI)</q-item-section>
          </q-item>
          <q-item
            clickable
            v-ripple
            :active="option === 'pci'"
            @click="option = 'pci'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon color="primary" name="bi-pci-card" />
            </q-item-section>
            <q-item-section>PCI Device</q-item-section>
          </q-item>
          <q-item
            clickable
            v-ripple
            :active="option === 'network'"
            @click="option = 'network'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon color="primary" name="mdi-ethernet" />
            </q-item-section>
            <q-item-section>Network Interface</q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
      <q-card-section v-if="diskfileLayout">
        <q-input filled v-model="diskFileName" label="Disk Name" class="q-pb-md" />
        <q-select
          class="q-pb-md"
          v-model="diskFileBusType"
          :options="diskBusTypes"
          label="Disk Bus"
          filled
        />
        <q-select
          class="q-pb-md"
          v-model="diskFileDeviceType"
          :options="diskDeviceTypes"
          label="Device Type"
          filled
        />
        <DirectoryList
          v-model="diskFileSource"
          label="Disk Source"
          selectiontype="file"
        ></DirectoryList>
      </q-card-section>
      <q-card-section v-if="diskblockLayout">
        <q-input filled v-model="diskBlockName" label="Disk Name" class="q-pb-md" />
        <q-select
          class="q-pb-md"
          v-model="diskBlockBusType"
          :options="diskBusTypes"
          label="Disk Bus"
          filled
        />
        <q-select
          class="q-pb-md"
          v-model="diskBlockDeviceType"
          :options="diskDeviceTypes"
          label="Device Type"
          filled
        />
        <q-input
          filled
          v-model="diskBlockSource"
          label="Block Device Path (e.g., /dev/sdb)"
          hint="Enter the path to the physical disk device"
        />
      </q-card-section>
      <q-card-section v-if="diskiscsiLayout">
        <q-input filled v-model="diskIscsiName" label="Disk Name" class="q-pb-md" />
        <q-select
          class="q-pb-md"
          v-model="diskIscsiBusType"
          :options="diskBusTypes"
          label="Disk Bus"
          filled
        />
        <q-select
          class="q-pb-md"
          v-model="diskIscsiDeviceType"
          :options="diskDeviceTypes"
          label="Device Type"
          filled
        />
        <q-input
          filled
          v-model="diskIscsiIqn"
          label="iSCSI Name (IQN)"
          hint="e.g., iqn.2013-07.com.example:iscsi-nopool/2"
          class="q-pb-md"
        />
        <q-input
          filled
          v-model="diskIscsiHost"
          label="iSCSI Host"
          hint="e.g., example.com or 192.168.1.100"
          class="q-pb-md"
        />
        <q-input
          filled
          v-model="diskIscsiPort"
          type="number"
          label="iSCSI Port"
          hint="Default: 3260"
        />
      </q-card-section>
      <q-card-section v-if="pciLayout">
        <q-input filled v-model="pciName" label="Device Name" class="q-pb-md" />
        <HostPcieDevicesList ref="hostPcieDevicesList" />
        <q-checkbox left-label v-model="pciCustomRom" label="Use Custom ROM" class="q-mt-md" />
        <q-input
          v-if="pciCustomRom"
          filled
          v-model="pciRomFile"
          label="ROM File Path"
          hint="e.g., /path/to/custom.rom"
          class="q-mt-md"
        />
      </q-card-section>
      <q-card-section v-if="networkLayout" class="q-py-none">
        <q-input filled v-model="networkName" label="Network Name" class="q-pb-md" />
        <q-select
          class="q-pb-md"
          v-model="networkSource"
          :options="libvirtNetworks"
          label="Network Source"
          filled
        />
        <q-select
          class="q-py-md"
          v-model="networkInterfaceType"
          :options="networkInterfaceTypes"
          label="Network Interface Type"
          filled
        />
        <q-checkbox left-label v-model="networkCustomMac" label="Custom MAC Address" />
        <q-input
          filled
          v-model="networkCustomMacAddress"
          label="Mac address"
          v-if="networkCustomMac"
        />
      </q-card-section>
      <q-card-actions align="right">
        <q-btn icon="mdi-arrow-right" color="primary" flat @click="optionChose" v-if="optionLayout">
          <ToolTip content="Next" />
        </q-btn>
        <q-btn color="primary" icon="check" flat @click="networkCreate" v-if="networkLayout">
          <ToolTip content="Create" />
        </q-btn>
        <q-btn color="primary" icon="check" flat @click="diskCreate" v-if="diskfileLayout">
          <ToolTip content="Create" />
        </q-btn>
        <q-btn color="primary" icon="check" flat @click="diskBlockCreate" v-if="diskblockLayout">
          <ToolTip content="Create" />
        </q-btn>
        <q-btn color="primary" icon="check" flat @click="diskIscsiCreate" v-if="diskiscsiLayout">
          <ToolTip content="Create" />
        </q-btn>
        <q-btn color="primary" icon="check" flat @click="pciCreate" v-if="pciLayout">
          <ToolTip content="Create" />
        </q-btn>
      </q-card-actions>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
</template>

<style lang="scss">
.my-menu-link {
  color: white;
  background: $secondary;
}
</style>

<script>
import ToolTip from '../ToolTip.vue'
import DirectoryList from '../host-manager/DirectoryList.vue'
import HostPcieDevicesList from '../host-manager/HostPcieDevicesList.vue'
import ErrorDialog from '../ErrorDialog.vue'
import { useApi } from 'src/composables/useApi'

export default {
  data() {
    return {
      layout: false,
      vmid: null,
      option: 'disk-file',
      optionLayout: true,
      diskfileLayout: false,
      diskblockLayout: false,
      diskiscsiLayout: false,
      pciLayout: false,
      networkLayout: false,
      networkInterfaceTypes: [
        { label: 'VirtIO', value: 'virtio' },
        { label: 'e1000', value: 'e1000' },
        { label: 'rtl8139', value: 'rtl8139' },
      ],
      networkInterfaceType: 'virtio',
      networkSource: '',
      networkName: '',
      networkCustomMac: false,
      networkCustomMacAddress: '52:54:00:a8:7e:c9',
      libvirtNetworks: [{ label: 'default', value: 'default' }],
      diskFileName: '',
      diskFileBusType: 'virtio',
      diskFileDeviceType: 'disk',
      diskFileSource: null,
      diskBusTypes: [
        { label: 'VirtIO', value: 'virtio' },
        { label: 'SATA', value: 'sata' },
        { label: 'SCSI', value: 'scsi' },
        { label: 'USB', value: 'usb' },
      ],
      diskDeviceTypes: [
        { label: 'Disk', value: 'disk' },
        { label: 'CDROM', value: 'cdrom' },
      ],
      diskBlockName: '',
      diskBlockBusType: 'virtio',
      diskBlockDeviceType: 'disk',
      diskBlockSource: '',
      diskIscsiName: '',
      diskIscsiBusType: 'virtio',
      diskIscsiDeviceType: 'disk',
      diskIscsiIqn: '',
      diskIscsiHost: '',
      diskIscsiPort: 3260,
      pciName: '',
      pciCustomRom: false,
      pciRomFile: '',
    }
  },
  emits: ['finished'],
  components: {
    ToolTip,
    DirectoryList,
    HostPcieDevicesList,
    ErrorDialog,
  },
  methods: {
    show(vmid) {
      this.layout = true
      this.vmid = vmid
      this.optionLayout = true
      this.diskfileLayout = false
      this.diskblockLayout = false
      this.diskiscsiLayout = false
      this.pciLayout = false
      this.networkLayout = false
      this.networkName = ''
    },
    optionChose() {
      if (this.option === 'disk-file') {
        this.optionLayout = false
        this.diskfileLayout = true
        this.diskFileBusType = this.diskBusTypes[0]
        this.diskFileDeviceType = this.diskDeviceTypes[0]
        this.diskFileName = ''
        this.diskFileSource = null
      } else if (this.option === 'disk-block') {
        this.optionLayout = false
        this.diskblockLayout = true
        this.diskBlockBusType = this.diskBusTypes[0]
        this.diskBlockDeviceType = this.diskDeviceTypes[0]
        this.diskBlockName = ''
        this.diskBlockSource = ''
      } else if (this.option === 'disk-iscsi') {
        this.optionLayout = false
        this.diskiscsiLayout = true
        this.diskIscsiBusType = this.diskBusTypes[0]
        this.diskIscsiDeviceType = this.diskDeviceTypes[0]
        this.diskIscsiName = ''
        this.diskIscsiIqn = ''
        this.diskIscsiHost = ''
        this.diskIscsiPort = 3260
      } else if (this.option === 'pci') {
        this.optionLayout = false
        this.pciLayout = true
        this.pciName = ''
        this.pciCustomRom = false
        this.pciRomFile = ''
      } else if (this.option === 'network') {
        this.optionLayout = false
        this.networkLayout = true
        this.networkGetList()
        this.networkInterfaceType = this.networkInterfaceTypes[0]
        this.networkName = ''
      }
    },
    networkGetList() {
      const api = useApi()
      api.vm.getNetworks()
        .then((data) => {
          this.libvirtNetworks = data.map(net => ({
            label: net.name,
            value: net.name,
            ...net
          }))
          if (this.libvirtNetworks.length > 0) {
            this.networkSource = this.libvirtNetworks[0]
          }
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading networks', [error?.detail || error.message])
        })
    },
    networkCreate() {
      if (this.networkName == '') {
        this.$refs.errorDialog.show('Error', ['Network name is required'])
        return
      }

      const api = useApi()

      // Fetch current VM state
      api.vm.get(this.vmid)
        .then((vm) => {
          // Add new network device
          const newDevice = {
            name: this.networkName,
            libvirt_name: this.networkSource.value,
            type: this.networkInterfaceType.value,
            mac: this.networkCustomMac ? this.networkCustomMacAddress : null,
          }

          const updatedVm = JSON.parse(JSON.stringify(vm))
          delete updatedVm.status
          updatedVm.devices_network.push(newDevice)

          // Update VM with new device
          return api.vm.update(this.vmid, updatedVm)
        })
        .then(() => {
          this.layout = false
          this.$emit('finished')
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error adding network device', [
            error?.detail || error.message,
          ])
        })
    },
    diskCreate() {
      if (this.diskFileSource == null) {
        this.$refs.errorDialog.show('Error', ['Disk source is required'])
        return
      }
      if (this.diskFileName == '') {
        this.$refs.errorDialog.show('Error', ['Disk name is required'])
        return
      }

      const api = useApi()

      // Fetch current VM state
      api.vm.get(this.vmid)
        .then((vm) => {
          // Add new disk file device
          const newDevice = {
            name: this.diskFileName,
            disk_bus: this.diskFileBusType.value,
            device_type: this.diskFileDeviceType.value,
            disk_source_file: this.diskFileSource,
          }

          const updatedVm = JSON.parse(JSON.stringify(vm))
          delete updatedVm.status
          updatedVm.devices_disk_file.push(newDevice)

          // Update VM with new device
          return api.vm.update(this.vmid, updatedVm)
        })
        .then(() => {
          this.layout = false
          this.$emit('finished')
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error adding disk device', [
            error?.detail || error.message,
          ])
        })
    },
    diskBlockCreate() {
      if (this.diskBlockSource == '') {
        this.$refs.errorDialog.show('Error', ['Block device path is required'])
        return
      }
      if (this.diskBlockName == '') {
        this.$refs.errorDialog.show('Error', ['Disk name is required'])
        return
      }

      const api = useApi()

      // Fetch current VM state
      api.vm.get(this.vmid)
        .then((vm) => {
          // Add new disk block device
          const newDevice = {
            name: this.diskBlockName,
            disk_bus: this.diskBlockBusType.value,
            device_type: this.diskBlockDeviceType.value,
            disk_source_dev: this.diskBlockSource,
          }

          const updatedVm = JSON.parse(JSON.stringify(vm))
          delete updatedVm.status
          updatedVm.devices_disk_block.push(newDevice)

          // Update VM with new device
          return api.vm.update(this.vmid, updatedVm)
        })
        .then(() => {
          this.layout = false
          this.$emit('finished')
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error adding block device', [
            error?.detail || error.message,
          ])
        })
    },
    diskIscsiCreate() {
      if (this.diskIscsiIqn == '') {
        this.$refs.errorDialog.show('Error', ['iSCSI IQN is required'])
        return
      }
      if (this.diskIscsiHost == '') {
        this.$refs.errorDialog.show('Error', ['iSCSI Host is required'])
        return
      }
      if (this.diskIscsiName == '') {
        this.$refs.errorDialog.show('Error', ['Disk name is required'])
        return
      }

      const api = useApi()

      // Fetch current VM state
      api.vm.get(this.vmid)
        .then((vm) => {
          // Add new iSCSI disk device
          const newDevice = {
            name: this.diskIscsiName,
            disk_bus: this.diskIscsiBusType.value,
            device_type: this.diskIscsiDeviceType.value,
            iscsi_name: this.diskIscsiIqn,
            iscsi_host: this.diskIscsiHost,
            iscsi_port: this.diskIscsiPort,
          }

          const updatedVm = JSON.parse(JSON.stringify(vm))
          delete updatedVm.status
          updatedVm.devices_disk_iscsi.push(newDevice)

          // Update VM with new device
          return api.vm.update(this.vmid, updatedVm)
        })
        .then(() => {
          this.layout = false
          this.$emit('finished')
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error adding iSCSI device', [
            error?.detail || error.message,
          ])
        })
    },
    pciCreate() {
      if (this.pciName == '') {
        this.$refs.errorDialog.show('Error', ['Device name is required'])
        return
      }
      const selectedPciDevice = this.$refs.hostPcieDevicesList.getSelectedPciDevice()
      if (!selectedPciDevice) {
        this.$refs.errorDialog.show('Error', ['Please select a PCI device'])
        return
      }

      const api = useApi()

      // Fetch current VM state
      api.vm.get(this.vmid)
        .then((vm) => {
          // Add new PCI device
          const newDevice = {
            pci_address: `${selectedPciDevice.domain}:${selectedPciDevice.bus}:${selectedPciDevice.slot}.${selectedPciDevice.function}`,
            rom_use: this.pciCustomRom,
            rom_file: this.pciCustomRom ? this.pciRomFile : null,
          }

          const updatedVm = JSON.parse(JSON.stringify(vm))
          delete updatedVm.status
          updatedVm.devices_pci.push(newDevice)

          // Update VM with new device
          return api.vm.update(this.vmid, updatedVm)
        })
        .then(() => {
          this.layout = false
          this.$emit('finished')
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error adding PCI device', [
            error?.detail || error.message,
          ])
        })
    },
  },
}
</script>
