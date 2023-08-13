<template>
  <q-page padding>
    <q-table
      :rows="data"
      :columns="columns"
      :pagination="pagination"
      selection="single"
      row-key="path"
      v-model:selected="selectedRows"
      :loading="tableLoading"
      hide-selected-banner
    >
      <template v-slot:loading>
        <q-inner-loading showing />
      </template>
      <template v-slot:top-right>
        <q-btn
          round
          flat
          color="primary"
          icon="mdi-plus"
          @click="arrayCreateDialogOpen"
        >
          <q-tooltip :offset="[0, 2]">New Array</q-tooltip>
        </q-btn>
        <q-btn
          round
          flat
          color="primary"
          icon="mdi-delete"
          :disable="selectedRows.length == 0"
          @click="
            $refs.confirmDialog.show(
              'Delete Array',
              ['Are you sure you want to delete ' + selectedRows[0].name + '?'],
              arrayDelete,
            )
          "
        >
          <q-tooltip :offset="[0, 2]">Delete Array</q-tooltip>
        </q-btn>
      </template>
      <template v-slot:body-cell-active="props">
        <q-td :props="props">
          <q-chip
            class="q-mx-none"
            v-if="props.row.operation == null"
            :label="props.row.active ? 'Active' : 'Inactive'"
            :color="props.row.active ? 'green' : 'red'"
          />
          <q-chip
            class="q-mx-none"
            v-else
            :label="
              props.row.operation +
              ' ' +
              props.row.operation_progress +
              ' (' +
              props.row.operation_finish +
              ')'
            "
            color="primary"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-level="props">
        <q-td :props="props">
          <q-chip
            class="q-mx-none"
            :label="raidLabels[props.row.personality].label"
            color="primary"
          />
        </q-td>
      </template>
      <template v-slot:body-cell-devices="props">
        <q-td :props="props">
          <span
            v-for="disk in props.row.disks"
            :key="disk"
            class="row items-center"
          >
            <q-icon
              class="q-pa-none q-mr-xs"
              name="mdi-circle"
              color="primary"
            />
            {{ disk }}
          </span>
        </q-td>
      </template>
      <template v-slot:body-cell-mountpoint="props">
        <q-td :props="props">
          <q-chip
            class="q-mx-none"
            style="cursor: pointer"
            :label="props.row.mountpoint ? props.row.mountpoint : 'Not mounted'"
            :color="props.row.mountpoint ? 'primary' : 'red'"
          />
        </q-td>
      </template>
    </q-table>
    <q-dialog v-model="createArrayDialog" persistent>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Create Array</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="sm" inset />
        <q-card-section>
          <q-form
            @submit="arrayCreate"
            class="q-gutter-md"
            style="width: 25em"
            ref="arrayCreateForm"
          >
            <q-select
              filled
              v-model="createArrayLevel"
              label="RAID Level"
              lazy-rules
              :rules="[(val) => !!val || 'RAID level is required']"
              @update:model-value="$refs.arrayCreateForm.reset()"
              :options="createArrayLevelOptions"
            >
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section>
                    <q-item-label>{{
                      raidLabels[scope.opt].label
                    }}</q-item-label>
                  </q-item-section>
                </q-item>
              </template>
              <template v-slot:selected-item="scope">
                <q-item v-bind="scope.itemProps" class="q-pl-none">
                  <q-item-section>
                    <q-item-label>{{
                      raidLabels[scope.opt].label
                    }}</q-item-label>
                  </q-item-section>
                </q-item>
              </template>
            </q-select>
            <q-separator color="transparent" spaced="md" />
            <q-select
              filled
              v-model="createArrayDevices"
              :options="createArrayDeviceOptions"
              label="Devices"
              option-label="model"
              option-value="path"
              multiple
              lazy-rules="ondemand"
              :rules="[
                (val) =>
                  val.length >= raidLabels[createArrayLevel].minDevices ||
                  'At least ' +
                    raidLabels[createArrayLevel].minDevices +
                    ' devices are required',
              ]"
            >
              <template v-slot:option="scope">
                <q-item v-bind="scope.itemProps">
                  <q-item-section>
                    <q-item-label
                      >{{ scope.opt.name }} -
                      {{ scope.opt.model }}</q-item-label
                    >
                    <q-item-label caption
                      >size: {{ scope.opt.size }}</q-item-label
                    >
                  </q-item-section>
                </q-item>
              </template>
              <template v-slot:selected-item="scope">
                <q-item v-bind="scope.itemProps" class="q-pl-none">
                  <q-item-section>
                    <q-item-label
                      >{{ scope.opt.name }} -
                      {{ scope.opt.model }}</q-item-label
                    >
                  </q-item-section>
                </q-item>
              </template>
            </q-select>
            <q-separator color="transparent" spaced="md" />
            <q-select
              filled
              v-model="createArrayFilesystem"
              label="Filesystem"
              lazy-rules
              :rules="[(val) => !!val || 'Filesystem is required']"
              :options="createArrayFilesystemOptions"
            />
            <div class="row justify-end">
              <q-btn flat label="Create" type="submit" />
            </div>
          </q-form>
        </q-card-section>
        <q-inner-loading :showing="createArrayLoading" />
      </q-card>
    </q-dialog>
    <ErrorDialog ref="errorDialog" />
    <ConfirmDialog ref="confirmDialog" />
  </q-page>
</template>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";

export default {
  data() {
    return {
      data: [],
      columns: [
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "active",
          label: "Status",
          field: "active",
          align: "left",
          sortable: true,
        },
        {
          name: "level",
          label: "Level",
          field: "level",
          align: "left",
        },
        {
          name: "devices",
          label: "Devices",
          field: "devices",
          align: "left",
        },
        {
          name: "capacity",
          label: "Capacity",
          field: "size",
          align: "left",
        },
        {
          name: "mountpoint",
          label: "Mountpoint",
          field: "mountpoint",
          align: "left",
        },
      ],
      raidLabels: {
        raid0: {
          label: "RAID0 (Stripe)",
          minDevices: 2,
        },
        raid1: {
          label: "RAID1 (Mirrored)",
          minDevices: 2,
        },
        raid5: {
          label: "RAID5",
          minDevices: 3,
        },
        raid6: {
          label: "RAID6",
          minDevices: 4,
        },
        raid10: {
          label: "RAID10",
          minDevices: 4,
        },
      },
      pagination: {
        rowsPerPage: 15,
        sortBy: "name",
      },
      selectedRows: [],
      tableLoading: true,
      createArrayDialog: false,
      createArrayDevices: [],
      createArrayDeviceOptions: [],
      createArrayLevel: "raid1",
      createArrayLevelOptions: ["raid0", "raid1", "raid5", "raid6", "raid10"],
      createArrayFilesystem: "ext4",
      createArrayFilesystemOptions: ["ext4", "xfs"],
      createArrayLoading: false,
      fetchTimeout: null,
    };
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
  },
  methods: {
    fetchData() {
      this.tableLoading = true;
      this.$api
        .get("storage/raid-manager")
        .then((response) => {
          this.data = response.data;
          this.tableLoading = false;
          this.fetchTimeout = setTimeout(this.fetchData, 5000);
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error fetching data", [error]);
        });
    },
    arrayCreateDialogOpen() {
      this.createArrayDialog = true;
      this.createArrayLoading = true;
      this.$api
        .get("storage/disks")
        .then((response) => {
          this.createArrayDeviceOptions = response.data.filter(
            (item) =>
              item.disktype == "individual" && item.partitions.length == 0,
          );
          this.createArrayLoading = false;
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error loading disks", [errormsg]);
        });
    },
    arrayCreate() {
      const level = this.createArrayLevel.replace("raid", "");
      const devices = this.createArrayDevices.map((item) => item.path);
      const filesystem = this.createArrayFilesystem;
      this.createArrayLoading = true;
      this.$api
        .post("storage/raid-manager/create", {
          level: level,
          devices: devices,
          filesystem: filesystem,
        })
        .then((response) => {
          this.createArrayLoading = false;
          this.createArrayDialog = false;
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error creating array", [errormsg]);
        });
    },
    arrayDelete() {
      this.$api
        .post("storage/raid-manager/delete", {
          path: this.selectedRows[0].path,
        })
        .then((response) => {
          this.selectedRows = [];
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error deleting array", [errormsg]);
        });
    },
  },
  mounted() {
    this.fetchData();
  },
  unmounted() {
    clearTimeout(this.fetchTimeout);
  },
};
</script>
