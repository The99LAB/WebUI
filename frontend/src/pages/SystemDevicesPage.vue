<template>
  <q-page>

    <div class="text-h6 text-center">System Devices</div>
    <q-table title="PCIe devices" :rows="rows" :columns="columns" row-key="name" separator="none" hide-pagination>
      <template #body="props">
        <q-tr :props="props">
          <q-td key="iommu" :props="props">
            <q-btn flat round :icon="props.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              @click="props.expand = !props.expand" no-caps :label=props.row.iommu
              class="text-weight-regular text-body2" />
          </q-td>
          <q-td key="driver" :props="props" class="text-weight-regular text-body2">
            {{ props.row.driver }}
          </q-td>
          <q-td key="name" :props="props" class="text-weight-regular text-body2">
            {{ props.row.name }}
          </q-td>
        </q-tr>
        <q-tr v-show="props.expand" :props="props">
          <q-td colspan="100%">
            <div>
              <div class="row text-body2 justify-start">
                <div class="col-1 text-start q-mr-sm text-weight-bold">
                  <p>Location</p>
                  <p>Vendor ID</p>
                  <p>Device ID</p>
                  <p>Unbinded</p>
                </div>
                <div class="col-1 text-weight-regular">
                  <p>{{ props.row.location }}</p>
                  <p>{{ props.row.vendorId }}</p>
                  <p>{{ props.row.deviceId }}</p>
                  <p>{{ props.row.unbind }}</p>
                </div>
              </div>
            </div>
          </q-td>
        </q-tr>
      </template>
    </q-table>
  </q-page>
</template>
<script>
import { ref } from 'vue'
const rows = [
  { iommu: "0", unbind: "No", location: "0:00.0", vendorId: "8086", deviceId: "3C0F", driver: "vfio-pci", name: "Intel Corporation 8th Gen Core Processor Host Bridge/DRAM Registers (rev 07)" }
]

const columns = [
  { label: 'IOMMU Group', field: 'iommu', name: 'iommu', align: 'left' },
  { label: 'Driver', field: 'driver', name: 'driver', align: 'left' },
  { label: 'Name', field: 'name', name: 'name', align: 'left' },
]

export default {
  setup() {
    return {
      rows,
      columns,
    }
  },
}
</script>
