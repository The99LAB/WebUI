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
      <q-card-section v-if="networkLayout" class="q-py-none">
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
import ErrorDialog from '../ErrorDialog.vue'

export default {
  data() {
    return {
      layout: false,
      vmid: null,
      option: 'disk-file',
      optionLayout: true,
      diskfileLayout: false,
      diskblockLayout: false,
      networkLayout: false,
      networkInterfaceTypes: [
        { label: 'VirtIO', value: 'virtio' },
        { label: 'e1000', value: 'e1000' },
        { label: 'rtl8139', value: 'rtl8139' },
      ],
      networkInterfaceType: 'virtio',
      networkSource: '',
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
    }
  },
  emits: ['finished'],
  components: {
    ToolTip,
    DirectoryList,
    ErrorDialog,
  },
  methods: {
    show(vmid) {
      this.layout = true
      this.vmid = vmid
      this.optionLayout = true
      this.diskfileLayout = false
      this.diskblockLayout = false
      this.networkLayout = false
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
      } else if (this.option === 'network') {
        this.optionLayout = false
        this.networkLayout = true
        this.networkGetList()
        this.networkInterfaceType = this.networkInterfaceTypes[0]
      }
    },
    networkGetList() {
      this.$api.get('/vm/networks').then((res) => {
        this.libvirtNetworks = res.data
        for (let i = 0; i < this.libvirtNetworks.length; i++) {
          this.libvirtNetworks[i].label = this.libvirtNetworks[i].name
          this.libvirtNetworks[i].value = this.libvirtNetworks[i].name
        }
        if (this.libvirtNetworks.length > 0) {
          this.networkSource = this.libvirtNetworks[0]
        }
      })
    },
    networkCreate() {
      this.$api
        .post('/vm/' + this.vmid + '/devices/network', {
          libvirt_name: this.networkSource.value,
          type: this.networkInterfaceType.value,
          mac: this.networkCustomMac ? this.networkCustomMacAddress : null,
        })
        .then(() => {
          this.layout = false
          this.$emit('finished')
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
      this.$api
        .post('/vm/' + this.vmid + '/devices/disk-file', {
          name: this.diskFileName,
          disk_bus: this.diskFileBusType.value,
          device_type: this.diskFileDeviceType.value,
          disk_source_file: this.diskFileSource,
        })
        .then(() => {
          this.layout = false
          this.$emit('finished')
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
      this.$api
        .post('/vm/' + this.vmid + '/devices/disk-block', {
          name: this.diskBlockName,
          disk_bus: this.diskBlockBusType.value,
          device_type: this.diskBlockDeviceType.value,
          disk_source_block: this.diskBlockSource,
        })
        .then(() => {
          this.layout = false
          this.$emit('finished')
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error creating block device', [
            error.response?.data?.detail || error.message,
          ])
        })
    },
  },
}
</script>
