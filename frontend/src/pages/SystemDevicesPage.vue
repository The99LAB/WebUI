<template>
  <q-page padding>
    <q-table :loading="pciTableLoading" :rows="pcieTableRows" :columns="pcieTableColumns" title="PCIe Devices" row-key="uuid" separator="none"
      :pagination="pcieTablePaginationOptions">
      <template #body="props">
        <q-tr :props="props">
          <q-td key="iommuGroup" :props="props">
            <q-btn flat round :icon="props.row.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              @click="props.row.expand = !props.row.expand" no-caps :label=props.row.iommuGroup
              class="text-weight-regular text-body2" />
          </q-td>
          <q-td key="driver" :props="props" class="text-weight-regular text-body2">
            {{ props.row.driver }}
          </q-td>
          <q-td key="productName" :props="props" class="text-weight-regular text-body2">
            {{ props.row.productName }}
          </q-td>
        </q-tr>
        <q-tr v-show="props.row.expand" :props="props">
          <q-td colspan="100%">
            <div class="row q-ma-sm text-body2">
              <p class="text-weight-bold q-mr-sm">Loaction:</p>
              <p>{{ props.row.path }}</p>
            </div>
            <div class="row q-ma-sm text-body2">
              <p class="text-weight-bold q-mr-sm">Vendor ID:</p>
              <p>{{ props.row.vendorid }}</p>
            </div>
            <div class="row q-ma-sm text-body2">
              <p class="text-weight-bold q-mr-sm">Product ID:</p>
              <p>{{ props.row.productid }}</p>
            </div>
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <q-separator spaced="lg" inset />
    <q-table :loading="scsiTableLoading" title="SCSI Devices" :rows="scsiTableRows" :columns="scsiTableColumns" row-key="path" separator="none" :pagination="scsiTablePaginationOptions"/>
    <q-separator spaced="lg" inset />
    <q-table :loading="usbTableLoading" title="USB Devices" :rows="usbTableRows" :columns="usbTableColumns" row-key="name" separator="none" :pagination="usbTablePaginationOptions"/>
  </q-page>
</template>

<script>
import { ref } from 'vue'

const pcieTableRows = []

const pcieTableColumns = [
  { label: 'IOMMU Group', field: 'iommuGroup', name: 'iommuGroup', align: 'left' },
  { label: 'Driver', field: 'driver', name: 'driver', align: 'left' },
  { label: 'Name', field: 'productName', name: 'productName', align: 'left' }
]

const scsiTableRows = []

const scsiTableColumns = [
  { label: 'Name', field: 'model', name: 'model', align: 'left' },
  { label: 'Type', field: 'type', name: 'type', align: 'left' },
  { label: 'Path', field: 'path', name: 'path', align: 'left' },
  { label: 'Size', field: 'capacity', name: 'capacity', align: 'left' }
]

const usbTableRows = []

const usbTableColumns = [
  { label: 'Name', field: 'name', name: 'name', align: 'left' },
  { label: 'Path', field: 'path', name: 'path', align: 'left' },
  { label: 'Id', field: 'id', name: 'id', align: 'left' }
]

export default {
  data() {

    const pciTableLoading = ref(true)
    const scsiTableLoading = ref(true)
    const usbTableLoading = ref(true)

    return {
      pcieTableRows,
      pcieTableColumns,
      pcieTablePaginationOptions: {
        sortBy: 'iommuGroup',
      },
      scsiTableRows,
      scsiTableColumns,
      scsiTablePaginationOptions: {
        sortBy: 'path',
      },
      usbTableRows,
      usbTableColumns,
      usbTablePaginationOptions: {
        sortBy: 'path',
      },
      pciTableLoading,
      scsiTableLoading,
      usbTableLoading
    }
  },
  components: {
  },
  methods: {
    updatePcieDevices() {
      this.$api.get("/host/system-devices/pcie").then((response) => {
        this.pcieTableRows = response.data
        this.pciTableLoading = false
      }).catch((error) => {
        this.$refs.errorDialog.show(error.response.data)
      })
    },
    updateScsiDevices() {
      this.$api.get("/host/system-devices/scsi").then((response) => {
        this.scsiTableRows = response.data
        this.scsiTableLoading = false
      }).catch((error) => {
        this.$refs.errorDialog.show(error.response.data)
      })
    },
    updateUsbDevices() {
      this.$api.get("/host/system-devices/usb").then((response) => {
        this.usbTableRows = response.data
        this.usbTableLoading = false
      }).catch((error) => {
        this.$refs.errorDialog.show(error.response.data)
      })
    },

  },
  mounted() {
    this.updatePcieDevices()
    this.updateScsiDevices()
    this.updateUsbDevices()
  },
  beforeUnmount() {
  }
}
</script>
