<template>
  <q-page padding>
    <q-table
      :loading="pciTableLoading"
      :rows="pcieTableRows"
      :columns="pcieTableColumns"
      title="PCIe Devices"
      row-key="uuid"
      separator="none"
      :pagination="pcieTablePaginationOptions"
    >
      <template #body="props">
        <q-tr :props="props">
          <q-td
            key="iommuGroup"
            :props="props"
            class="text-weight-regular text-body2"
            @click="props.row.expand = !props.row.expand"
            style="cursor: pointer; user-select: none"
          >
            <q-icon
              :name="props.row.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              size="sm"
            />
            {{ props.row.iommuGroup }}
          </q-td>
          <q-td
            key="driver"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.driver }}
          </q-td>
          <q-td
            key="productName"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.productName }}
          </q-td>
        </q-tr>
        <q-tr v-show="props.row.expand" :props="props">
          <q-td colspan="100%" no-hover>
            <div class="q-gutter-sm q-ml-xs">
              <div class="row">
                <p class="text-body2 text-weight-bold q-mr-sm q-my-none">
                  Location:
                </p>
                <p class="text-body2 q-my-none">{{ props.row.path }}</p>
              </div>
              <div class="row">
                <p class="text-body2 text-weight-bold q-mr-sm q-my-none">
                  Domain:
                </p>
                <p class="text-body2 q-my-none">{{ props.row.domain }}</p>
              </div>
              <div class="row">
                <p class="text-body2 text-weight-bold q-mr-sm q-my-none">
                  Bus:
                </p>
                <p class="text-body2 q-my-none">{{ props.row.bus }}</p>
              </div>
              <div class="row">
                <p class="text-body2 text-weight-bold q-mr-sm q-my-none">
                  Slot:
                </p>
                <p class="text-body2 q-my-none">{{ props.row.slot }}</p>
              </div>
              <div class="row">
                <p class="text-body2 text-weight-bold q-mr-sm q-my-none">
                  Function:
                </p>
                <p class="text-body2 q-my-none">{{ props.row.function }}</p>
              </div>
              <div class="row">
                <p class="text-body2 text-weight-bold q-mr-sm q-my-none">
                  Vendor ID:
                </p>
                <p class="text-body2 q-my-none">{{ props.row.vendorid }}</p>
              </div>
              <div class="row">
                <p class="text-body2 text-weight-bold q-mr-sm q-my-none">
                  Product ID:
                </p>
                <p class="text-body2 q-my-none">{{ props.row.productid }}</p>
              </div>
            </div>
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <q-separator color="transparent" spaced="lg" inset />
    <q-table
      :loading="scsiTableLoading"
      title="SCSI Devices"
      :rows="scsiTableRows"
      :columns="scsiTableColumns"
      row-key="path"
      separator="none"
      :pagination="scsiTablePaginationOptions"
    />
    <q-separator color="transparent" spaced="lg" inset />
    <q-table
      :loading="usbTableLoading"
      title="USB Devices"
      :rows="usbTableRows"
      :columns="usbTableColumns"
      row-key="name"
      separator="none"
      :pagination="usbTablePaginationOptions"
    />
  </q-page>
</template>

<script>
import { ref } from "vue";

const pcieTableRows = [];

const pcieTableColumns = [
  {
    label: "IOMMU Group",
    field: "iommuGroup",
    name: "iommuGroup",
    align: "left",
  },
  { label: "Driver", field: "driver", name: "driver", align: "left" },
  { label: "Name", field: "productName", name: "productName", align: "left" },
];

const scsiTableRows = [];

const scsiTableColumns = [
  { label: "Name", field: "model", name: "model", align: "left" },
  { label: "Type", field: "type", name: "type", align: "left" },
  { label: "Path", field: "path", name: "path", align: "left" },
  { label: "Size", field: "capacity", name: "capacity", align: "left" },
];

const usbTableRows = [];

const usbTableColumns = [
  { label: "Name", field: "name", name: "name", align: "left" },
  { label: "Path", field: "path", name: "path", align: "left" },
  { label: "Id", field: "id", name: "id", align: "left" },
];

export default {
  data() {
    const pciTableLoading = ref(true);
    const scsiTableLoading = ref(true);
    const usbTableLoading = ref(true);

    return {
      pcieTableRows,
      pcieTableColumns,
      pcieTablePaginationOptions: {
        sortBy: "iommuGroup",
      },
      scsiTableRows,
      scsiTableColumns,
      scsiTablePaginationOptions: {
        sortBy: "path",
      },
      usbTableRows,
      usbTableColumns,
      usbTablePaginationOptions: {
        sortBy: "path",
      },
      pciTableLoading,
      scsiTableLoading,
      usbTableLoading,
    };
  },
  components: {},
  methods: {
    updatePcieDevices() {
      this.$api
        .get("/host/system-devices/pcie")
        .then((response) => {
          this.pcieTableRows = response.data;
          this.pciTableLoading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error.response.data.detail);
        });
    },
    updateScsiDevices() {
      this.$api
        .get("/host/system-devices/scsi")
        .then((response) => {
          this.scsiTableRows = response.data;
          this.scsiTableLoading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error.response.data.detail);
        });
    },
    updateUsbDevices() {
      this.$api
        .get("/host/system-devices/usb")
        .then((response) => {
          this.usbTableRows = response.data;
          this.usbTableLoading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error.response.data.detail);
        });
    },
  },
  mounted() {
    this.updatePcieDevices();
    this.updateScsiDevices();
    this.updateUsbDevices();
  },
  beforeUnmount() {},
};
</script>
