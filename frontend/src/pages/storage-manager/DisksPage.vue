<template>
  <q-page padding>
    <q-table
      :rows="disksTableData"
      :columns="disksTableColumns"
      :pagination="disksTablePagination"
      row-key="name"
      selection="single"
      v-model:selected="disksTableSelectedRows"
      title="Disks"
      :loading="disksTableLoading"
    >
      <template v-slot:top-right>
        <q-btn
          icon="mdi-harddisk-plus"
          flat
          round
          color="primary"
          @click="createPartitionDialog = true"
          :disable="
            disksTableSelectedRows.length == 0 ||
            disksTableSelectedRows.some(
              (item) =>
                item.disktype != 'individual' || item.partitions.length > 0,
            )
          "
        >
          <q-tooltip
            :offset="[0, 5]"
            v-if="
              disksTableSelectedRows.some(
                (item) => item.disktype != 'individual',
              )
            "
          >
            Cannot create a partition on this disk because it is a
            {{ diskTypes[disksTableSelectedRows[0].disktype] }}.
          </q-tooltip>
          <q-tooltip
            :offset="[0, 5]"
            v-else-if="
              disksTableSelectedRows.some((item) => item.partitions.length > 0)
            "
          >
            Cannot create a partition on this disk.<br />This disk already has a
            partition.
          </q-tooltip>
          <q-tooltip :offset="[0, 5]" v-else>Create Partition</q-tooltip>
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-eraser"
          @click="
            $refs.confirmDialog.show(
              'Wipe Disk',
              [
                'Are you sure you want to wipe this disk?',
                'This action cannot be undone.',
              ],
              () => this.diskWipe(),
            )
          "
          :disable="
            disksTableSelectedRows.length == 0 ||
            disksTableSelectedRows.some(
              (item) => item.disktype != 'individual',
            ) ||
            disksTableSelectedRows.some((item) =>
              item.partitions.some((partition) => partition.mount != ''),
            )
          "
        >
          <q-tooltip
            :offset="[0, 5]"
            v-if="
              disksTableSelectedRows.some((item) =>
                item.partitions.some((partition) => partition.mount != ''),
              )
            "
          >
            Cannot wipe this disk because not all partitions are unmounted.
          </q-tooltip>
          <q-tooltip
            :offset="[0, 5]"
            v-else-if="
              disksTableSelectedRows.some(
                (item) => item.disktype != 'individual',
              )
            "
          >
            Cannot wipe this disk because it is a
            {{ diskTypes[disksTableSelectedRows[0].disktype] }}.
          </q-tooltip>
          <q-tooltip :offset="[0, 5]" v-else>Wipe disk</q-tooltip>
        </q-btn>
      </template>
      <template v-slot:loading>
        <q-inner-loading showing />
      </template>
      <template v-slot:header-cell-partitions>
        <q-th class="text-left"
          >Partitions
          <q-btn
            icon="mdi-delete"
            flat
            round
            color="primary"
            size="sm"
            dense
            :disable="
              partitionTableSelected.length == 0 ||
              disksTableData.find(
                (item) => item.path == partitionTableSelected[0].parent,
              ).disktype == 'system' ||
              partitionTableSelected[0].mount != ''
            "
            @click="
              this.$refs.confirmDialog.show(
                'Delete Partition',
                [
                  'Are you sure you want to delete this partition?',
                  'This action cannot be undone.',
                ],
                () => this.partitionDelete(),
              )
            "
          >
            <q-tooltip
              :offset="[0, 2]"
              v-if="
                partitionTableSelected.length != 0 &&
                disksTableData.find(
                  (item) => item.path == partitionTableSelected[0].parent,
                ).disktype == 'system'
              "
              >Cannot delete partitions on the system disk</q-tooltip
            >
            <q-tooltip
              :offset="[0, 2]"
              v-if="
                partitionTableSelected.length != 0 &&
                partitionTableSelected[0].mount != ''
              "
              >Delete: Unmount this partition first</q-tooltip
            >
            <q-tooltip :offset="[0, 2]" v-else>Delete Partition</q-tooltip>
          </q-btn>
          <q-btn
            icon="mdi-play"
            flat
            round
            color="primary"
            size="sm"
            dense
            v-if="
              partitionTableSelected.length != 0 &&
              partitionTableSelected[0].mount == '' &&
              disksTableData.find(
                (item) => item.path == partitionTableSelected[0].parent,
              ).disktype != 'system'
            "
            @click="partitionMount"
          >
            <q-tooltip :offset="[0, 2]">Mount Partition</q-tooltip>
          </q-btn>
          <q-btn
            icon="mdi-stop"
            flat
            round
            color="primary"
            size="sm"
            dense
            v-if="
              partitionTableSelected.length != 0 &&
              partitionTableSelected[0].mount != '' &&
              disksTableData.find(
                (item) => item.path == partitionTableSelected[0].parent,
              ).disktype != 'system'
            "
            @click="partitionUnmount"
          >
            <q-tooltip :offset="[0, 2]">Unmount Partition</q-tooltip>
          </q-btn>
        </q-th>
      </template>
      <template v-slot:body="props">
        <q-tr :props="props" @click="props.selected" no-hover>
          <q-td>
            <q-checkbox
              v-model="props.selected"
              color="primary"
              :disable="props.row.disktype == 'raid_member'"
            >
              <q-tooltip
                :offset="[0, 0]"
                v-if="props.row.disktype == 'raid_member'"
                anchor="center right"
                self="center left"
                >Remove this disk from the RAID array first</q-tooltip
              >
            </q-checkbox>
          </q-td>
          <q-td
            key="name"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.name }}
          </q-td>
          <q-td
            key="model"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.model }}
          </q-td>
          <q-td
            key="type"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ diskTypes[props.row.disktype] }}
          </q-td>
          <q-td
            key="capacity"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.size }}
          </q-td>
          <q-td
            key="partitions"
            :props="props"
            class="text-weight-regular text-body2"
          >
            <span
              class="row items-center"
              v-if="props.row.has_partitiontable == false"
            >
              <p class="q-my-none text-body2">
                This disk has no partitioning scheme.
              </p>
              <q-icon class="q-ml-xs" name="mdi-help-circle-outline" size="sm">
                <q-tooltip :offset="[0, 2]">
                  If you want to use this disk, create a partition on it first.
                  <br />
                  That will also create a partitioning scheme.
                </q-tooltip>
              </q-icon>
            </span>
            <span
              class="row items-center"
              v-else-if="props.row.disktype == 'raid_member'"
            >
              <p class="q-my-none text-body2">
                This disk is part of a RAID array.
              </p>
              <q-icon class="q-ml-xs" name="mdi-help-circle-outline" size="sm">
                <q-tooltip :offset="[0, 2]"
                  >You cannot see the partitions of a disk which is part of a
                  RAID array.</q-tooltip
                >
              </q-icon>
            </span>
            <span
              class="row items-center"
              v-else-if="props.row.partitions.length == 0"
            >
              <p class="q-my-none text-body2">This disk has no partitions.</p>
              <q-icon class="q-ml-xs" name="mdi-help-circle-outline" size="sm">
                <q-tooltip :offset="[0, 2]">
                  If you want to use this disk, you need to create a partition
                  first.
                  <br />
                  Or you can create a RAID array with this disk.
                </q-tooltip>
              </q-icon>
            </span>
            <q-table
              class="q-ma-sm"
              :rows="props.row.partitions"
              :columns="partitionTableColumns"
              row-key="name"
              hide-bottom
              selection="single"
              v-model:selected="partitionTableSelected"
              v-else
            >
              <template v-slot:body-cell-mount="props">
                <q-td :props="props">
                  <q-chip
                    class="q-mx-none"
                    style="cursor: pointer"
                    :label="
                      props.row.mount == '' ? 'unmounted' : props.row.mount
                    "
                    :color="props.row.mount == '' ? 'red' : 'primary'"
                  />
                </q-td>
              </template>
              <template v-slot:body-cell-used="props">
                <q-td :props="props" v-if="props.row.used != null">
                  {{ props.row.used }} / {{ props.row.size }}
                </q-td>
                <q-td :props="props" v-else>
                  {{ props.row.size }}
                </q-td>
              </template>
            </q-table>
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <q-dialog v-model="mountPartitionDialog" persistent>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Mount Partition</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="sm" inset />
        <q-card-section>
          <q-form @submit="partitionMountSubmit">
            <q-input
              filled
              v-model="mountPartitionDialogMountpoint"
              label="Mountpoint"
              lazy-rules
              :rules="[(val) => !!val || 'Mountpoint is required']"
            />
            <div class="row justify-end">
              <q-btn flat label="Mount" type="submit" />
            </div>
          </q-form>
        </q-card-section>
        <q-inner-loading :showing="mountPartitionLoading" />
      </q-card>
    </q-dialog>
    <q-dialog v-model="createPartitionDialog" persistent>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Create Partition</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="sm" inset />
        <q-card-section>
          <q-form @submit="partitionCreate" class="q-gutter-md">
            <q-select
              filled
              v-model="disksTableSelectedRows[0]"
              label="Device"
              option-label="name"
              readonly
            />
            <q-select
              filled
              v-model="createPartitionFsType"
              label="Filesystem type"
              lazy-rules
              :rules="[(val) => !!val || 'Filesystem type is required']"
              :options="createPartitionFsTypeOptions"
            />
            <div class="row justify-end">
              <q-btn flat label="Create" type="submit" />
            </div>
          </q-form>
        </q-card-section>
        <q-inner-loading :showing="createPartitionDialogLoading" />
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
      disksTableData: [],
      disksTableColumns: [
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "model",
          label: "Model",
          field: "model",
          align: "left",
          sortable: true,
        },
        {
          name: "type",
          label: "Type",
          field: "type",
          align: "left",
        },
        {
          name: "capacity",
          label: "Capacity",
          field: "size",
          align: "left",
        },
        {
          name: "partitions",
          label: "Partitions",
          field: "partitions",
          align: "left",
        },
      ],
      disksTablePagination: {
        rowsPerPage: 15,
        sortBy: "name",
      },
      disksTableSelectedRows: [],
      disksTableLoading: true,
      partitionTableColumns: [
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "fstype",
          label: "Filesystem",
          field: "fstype",
          align: "left",
          sortable: true,
        },
        {
          name: "used",
          label: "Capacity",
          field: "used",
          align: "left",
        },
        {
          name: "mount",
          label: "Mountpoint",
          field: "mount",
          align: "left",
        },
      ],
      partitionTableSelected: [],
      mountPartitionDialog: false,
      mountPartitionDialogMountpoint: "",
      mountPartitionLoading: false,
      createPartitionDialog: false,
      createPartitionFsType: "",
      createPartitionFsTypeOptions: ["ext4", "xfs"],
      createPartitionDialogLoading: false,
      diskTypes: {
        system: "System Disk",
        individual: "Individual Disk",
        raid_member: "RAID Member",
      },
    };
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
  },
  methods: {
    fetchData() {
      this.disksTableLoading = true;
      this.$api
        .get("storage/disks")
        .then((response) => {
          this.disksTableData = response.data;
          this.disksTableLoading = false;
          this.disksTableSelectedRows = [];
          this.partitionTableSelected = [];
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Failed to fetch disks", [errormsg]);
        });
    },
    partitionDelete() {
      this.$api
        .post("storage/disks/partition/delete", {
          disk: this.partitionTableSelected[0].parent,
          partition: this.partitionTableSelected[0].number,
        })
        .then((response) => {
          this.fetchData();
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Failed to delete partition", [errormsg]);
        });
    },
    partitionMount() {
      this.mountPartitionDialog = true;
      this.mountPartitionDialogMountpoint =
        "/mnt/" +
        this.disksTableData
          .find((item) => item.path == this.partitionTableSelected[0].parent)
          .model.replaceAll(" ", "_");
    },
    partitionMountSubmit() {
      this.mountPartitionLoading = true;
      this.$api
        .post("storage/disks/partition/mount", {
          partition: this.partitionTableSelected[0].uuid,
          mountpoint: this.mountPartitionDialogMountpoint,
        })
        .then((response) => {
          this.mountPartitionLoading = false;
          this.mountPartitionDialog = false;
          this.fetchData();
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error mounting partition", [errormsg]);
          this.mountPartitionLoading = false;
        });
    },
    partitionUnmount() {
      this.$api
        .post("storage/disks/partition/unmount", {
          partition: this.partitionTableSelected[0].uuid,
        })
        .then((response) => {
          this.fetchData();
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Failed to unmount partition", [
            errormsg,
          ]);
        });
    },
    partitionCreate() {
      this.createPartitionDialogLoading = true;
      this.$api
        .post("storage/disks/partition/create", {
          diskpath: this.disksTableSelectedRows[0].path,
          fstype: this.createPartitionFsType,
        })
        .then((response) => {
          this.createPartitionDialogLoading = false;
          this.createPartitionDialog = false;
          this.fetchData();
        })
        .catch((error) => {
          this.createPartitionDialogLoading = false;
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Failed to create partition", [errormsg]);
        });
    },
    diskWipe() {
      this.$api
        .post("storage/disks/disk/wipe", {
          diskpath: this.disksTableSelectedRows[0].path,
        })
        .then((response) => {
          this.fetchData();
        })
        .catch((error) => {
          const errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Failed to wipe disk", [errormsg]);
        });
    },
  },
  mounted() {
    this.fetchData();
  },
};
</script>
