<template>
  <q-dialog v-model="dialogVisible">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add disk</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none" style="width: 35em">
        <q-select
          v-model="deviceType"
          :options="deviceTypeOptions"
          label="Device Type"
          @update:model-value="volumePath = null"
        >
          <template v-slot:option="scope">
            <q-item v-bind="scope.itemProps">
              <q-item-section>
                <q-item-label>{{ scope.opt.label }}</q-item-label>
                <q-item-label caption>
                  {{ scope.opt.comment }}
                </q-item-label>
              </q-item-section>
            </q-item>
          </template>
        </q-select>

        <q-input
          v-if="deviceType.value == 'createvdisk'"
          label="vDisk size"
          v-model="diskSize"
          type="number"
          min="1"
        >
          <template v-slot:after>
            <q-select v-model="diskSizeUnit" :options="diskUnitOptions" />
          </template>
        </q-input>

        <DirectoryList
          v-model="volumePath"
          v-if="deviceType.value == 'existingvdisk' || deviceType.value == 'cdrom'"
          selectiontype="file"
          label="vDisk Path"
        >
          <template v-slot:after>
            <q-icon name="mdi-help-circle-outline">
              <q-tooltip :offset="[5, 5]">
                <div v-if="deviceType.value == 'existingvdisk'">
                  Select the vdisk file to add to the VM.
                  Usual file extensions are qcow2 and raw.
                </div>
                <div v-else-if="deviceType.value == 'cdrom'">
                  Select the iso file to add to the VM.
                </div>
              </q-tooltip>
            </q-icon>
          </template>
        </DirectoryList>
        <DirectoryList
          v-model="vdiskDirectory"
          v-if="deviceType.value == 'createvdisk'"
          selectiontype="dir"
          label="vDisk Path"
        >
          <template v-slot:after>
            <q-icon name="mdi-help-circle-outline">
              <q-tooltip :offset="[5, 5]">
                Select the directory where the vdisk file will be created.
              </q-tooltip>
            </q-icon>
          </template>
        </DirectoryList>
        <q-select
          v-if="deviceType.value == 'createvdisk'"
          v-model="diskDriverType"
          :options="diskDriverTypeOptions"
          label="vDisk Type"
        >
          <template v-slot:after>
            <q-icon name="mdi-help-circle-outline">
              <q-tooltip :offset="[5, 5]">
                Select the driver type for the disk.
                <br>
                RAW is the fastest, but does not support snapshots.
                <br>
                QCOW2 is slower, but supports snapshots.
              </q-tooltip>
            </q-icon>
          </template>
        </q-select>
        <q-input
          v-model="sourceDevice"
          label="Source Device"
          v-if="deviceType.value == 'block'"
        >
          <template v-slot:after>
            <q-icon name="mdi-help-circle-outline">
              <q-tooltip :offset="[5, 5]">
                Select the block device to add to the VM.
                <br>
                This can be a physical device like a HDD or SSD. It can also be a partition of a physical device.
                <br>
                For example: /dev/sda or /dev/sda1
              </q-tooltip>
            </q-icon>
          </template>
        </q-input>
        <q-select
          v-model="diskBus"
          :options="diskBusOptions"
          label="Bus"
        > 
          <template v-slot:after>
            <q-icon name="mdi-help-circle-outline">
              <q-tooltip :offset="[5, 5]">
                Select the bus type for the disk.
                <br>
                This is how the disk will be seen in the vm, for example as a SATA or USB disk.
              </q-tooltip>
            </q-icon>
          </template>
        </q-select>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Finish" @click="addDisk()" />
      </q-card-actions>
    </q-card>
    <q-inner-loading :showing="dialogLoading"/>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
</template>

<script>
import DirectoryList from "src/components/DirectoryList.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      dialogVisible: false,
      dialogLoading: false,
      deviceTypeOptions: [
        {
          label: "New vdisk",
          value: "createvdisk",
          comment: "Create a new vdisk file. (qcow2, raw)"
        },
        {
          label: "Existing vdisk",
          value: "existingvdisk",
          comment: "Add an existing vdisk file. (qcow2, raw)"
        },
        {
          label: "CD-ROM",
          value: "cdrom",
          comment: "Add a CD-ROM device. (iso, raw)"
        },
        {
          label: "Block device",
          value: "block",
          comment: "A block device is a physical device like a HDD or SSD. It can also be a partition of a physical device."
        }
      ],
      deviceType: {
          label: "New vdisk",
          value: "createvdisk",
          comment: "Create a new vdisk. (qcow2, raw)"
      },
      sourceDevice: "/dev/sda",
      volumePath: null,
      vdiskDirectory: null,
      diskDriverTypeOptions: ["raw", "qcow2"],
      diskDriverType: "raw",
      diskBusOptions: ["sata", "scsi", "virtio", "usb"],
      diskBus: "sata",
      uuid: null,
      diskSize: 40,
      diskSizeUnit: "GB",
      diskUnitOptions: ["MB", "GB", "TB"],
    };
  },
  emits: ["disk-add-finished"],
  components: {
    DirectoryList,
    ErrorDialog,
  },
  methods: {
    show(uuid) {
      this.dialogVisible = true;
      this.uuid = uuid
    },
    addDisk() {
      if (this.deviceType == 'createvdisk' || this.deviceType == 'existingvdisk' || this.deviceType == 'cdrom'){
        if (this.volumePath == null) {
          this.$refs.errorDialog.show("Error adding disk", [
            "Please select a vdisk path of file",
          ]);
          return;
        }
      }

      this.dialogLoading = true;
      this.$api
      .post("/vm-manager/" + this.uuid + "/edit-disk-add", {
        deviceType: this.deviceType.value,
        sourceDevice: this.sourceDevice,
        volumePath: this.volumePath,
        vdiskDirectory: this.vdiskDirectory,
        diskDriverType: this.diskDriverType,
        diskBus: this.diskBus,
        diskSize: this.diskSize,
        diskSizeUnit: this.diskSizeUnit,
      })
      .then((response) => {
        this.$emit("disk-add-finished");
        this.dialogLoading = false;
        this.dialogVisible = false;
      })
      .catch((error) => {
        const errormsg = error.response ? error.response.data.detail : error;
        this.$refs.errorDialog.show("Error creating disk", [errormsg]);
        this.dialogLoading = false;
      });
    },
  },
};
</script>
