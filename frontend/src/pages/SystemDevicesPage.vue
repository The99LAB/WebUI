<template>
  <q-page padding>
    <q-table :rows="pcieTableRows" :columns="pcieTableColumns" title="PCIe Devices" row-key="uuid" separator="none"
      :pagination="pcieTablepaginationOptions">
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
    <q-table title="SCSI Devices" :rows="scsiTableRows" :columns="scsiTablecolumns" row-key="path"
      :pagination="scsiTablepaginationOptions" />
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

const scsiTablecolumns = [
  { label: 'Name', field: 'model', name: 'model', align: 'left' },
  { label: 'Type', field: 'type', name: 'type', align: 'left' },
  { label: 'Path', field: 'path', name: 'path', align: 'left' },
  { label: 'Size', field: 'capacity', name: 'capacity', align: 'left' }
]

export default {
  data() {
    return {
      pcieTableRows,
      pcieTableColumns,
      pcieTablepaginationOptions: {
        sortBy: 'iommuGroup',
      },
      scsiTableRows,
      scsiTablecolumns,
      scsiTablePaginationOptions: {
        sortBy: 'path',
      }
    }
  },
  components: {
  },
  methods: {
    updatePcieDevices() {
      this.$api.get("/host/system-devices/pcie").then((response) => {
        this.pcieTableRows = response.data
      }).catch((error) => {
        this.$refs.errorDialog.show(error.response.data)
      })
    },
    updateScsiDevices() {
      this.$api.get("/host/system-devices/scsi").then((response) => {
        console.log("abcd")
        console.log(response.data)
        this.scsiTableRows = response.data
      }).catch((error) => {
        this.$refs.errorDialog.show(error.response.data)
      })
    },

  },
  mounted() {
    this.updatePcieDevices()
    this.updateScsiDevices()
  },
  beforeUnmount() {
  }
}
</script>
