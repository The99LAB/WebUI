<template>
  <q-page padding>
    <q-table
      title="VM Overview"
      :rows="data"
      :columns="columns"
      row-key="id"
      selection="single"
      :loading="tableLoading"
      v-model:selected="selectedVm"
      hide-selected-banner
      :pagination="pagination"
      hide-bottom
    >
      <template v-slot:top-right>
        <q-btn flat round color="primary" icon="refresh" @click="getData">
          <ToolTip content="Refresh" />
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-pencil"
          v-if="selectedVm.length !== 0 && selectedVm[0].status !== 'Running'"
          @click="editVm"
        >
          <ToolTip content="Edit" />
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-play"
          v-if="selectedVm.length !== 0 && selectedVm[0].status !== 'Running'"
          @click="startVm"
        >
          <ToolTip content="Start" />
        </q-btn>
        <q-btn
          flat
          round
          color="negative"
          icon="mdi-stop"
          v-if="selectedVm.length !== 0 && selectedVm[0].status == 'Running'"
          @click="shutdownVm"
        >
          <ToolTip content="Shutdown" />
        </q-btn>
        <q-btn
          flat
          round
          color="negative"
          icon="mdi-bomb"
          v-if="selectedVm.length !== 0 && selectedVm[0].status == 'Running'"
          @click="forcestopVm"
        >
          <ToolTip content="Force Stop" />
        </q-btn>
        <q-btn
          flat
          round
          color="negative"
          icon="mdi-restart"
          v-if="selectedVm.length !== 0 && selectedVm[0].status == 'Running'"
          @click="resetVm"
        >
          <ToolTip content="Reset" />
        </q-btn>
        <q-btn
          flat
          round
          color="negative"
          icon="mdi-delete"
          :disable="selectedVm.length === 0"
          @click="removeVm"
        >
          <ToolTip content="Remove" />
        </q-btn>
      </template>
      <template v-slot:body-selection="props">
        <q-checkbox v-model="props.selected" />
      </template>
      <template v-slot:body-cell-memory_min="props">
        <q-td>
          {{ convertMemory(props.row.memory_min) }}
        </q-td>
      </template>
      <template v-slot:body-cell-memory_max="props">
        <q-td>
          {{ convertMemory(props.row.memory_max) }}
        </q-td>
      </template>
    </q-table>
  </q-page>
  <ErrorDialog ref="errorDialog" />
  <ConfirmDialog ref="confirmDialog" />
  <ToolTip ref="toolTip" />
  <EditVmDialog ref="editVmDialog" @finished="getData"/>
</template>

<script>
import ErrorDialog from 'src/components/ErrorDialog.vue'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import ToolTip from 'src/components/ToolTip.vue'
import EditVmDialog from 'src/components/vm/EditVmDialog.vue'
import { convertsize } from 'src/utils/convertsize'
import { useApi } from 'src/composables/useApi'

export default {
  data() {
    return {
      data: [],
      columns: [
        {
          name: 'id',
          label: 'ID',
          field: 'id',
          align: 'left',
          sortable: true,
        },
        {
          name: 'name',
          label: 'Name',
          field: 'name',
          align: 'left',
          sortable: true,
        },
        {
          name: 'state',
          label: 'State',
          field: 'status',
          align: 'left',
          sortable: true,
        },
        {
          name: 'autostart',
          label: 'Autostart',
          field: 'autostart',
          align: 'left',
          sortable: true,
        },
        {
          name: 'vcpu',
          label: 'vCPU',
          field: 'vcpu',
          align: 'left',
          sortable: true,
        },
        {
          name: 'memory_min',
          label: 'Memory Min',
          field: 'memory_min',
          align: 'left',
          sortable: true,
        },
        {
          name: 'memory_max',
          label: 'Memory Max',
          field: 'memory_max',
          align: 'left',
          sortable: true,
        },
      ],
      tableLoading: false,
      selectedVm: [],
      pagination: {
        rowsPerPage: 0,
        sortBy: 'id',
        descending: false,

      },
    }
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
    ToolTip,
    EditVmDialog,
  },
  computed: {
    convertMemory() {
      return (value) => {
        return convertsize(value, 'B', null, 'int_str_space')
      }
    },
  },
  methods: {
    getData() {
      this.tableLoading = true
      var selectedvmid = this.selectedVm.length > 0 ? this.selectedVm[0].id : null
      this.selectedVm = []

      const api = useApi()
      api.vm
        .getAll()
        .then((data) => {
          this.data = data
          console.log(this.data)
          this.tableLoading = false
          if (selectedvmid) {
            this.selectedVm = this.data.filter((vm) => vm.id === selectedvmid)
          }
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading VMs', [error?.detail || error.message])
          this.tableLoading = false
        })
    },
    editVm() {
      this.$refs.editVmDialog.show(this.selectedVm[0].id)
    },
    startVm() {
      const api = useApi()
      api.vm
        .start(this.selectedVm[0].id)
        .then(() => {
          this.getData()
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error starting VM', [error?.detail || error.message])
        })
    },
    shutdownVm() {
      const api = useApi()
      api.vm
        .shutdown(this.selectedVm[0].id)
        .then(() => {
          this.getData()
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error shutting down VM', [error?.detail || error.message])
        })
    },
    forcestopVm() {
      const api = useApi()
      api.vm
        .forcestop(this.selectedVm[0].id)
        .then(() => {
          this.getData()
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error stopping VM', [error?.detail || error.message])
        })
    },
    resetVm() {
      const api = useApi()
      api.vm
        .reset(this.selectedVm[0].id)
        .then(() => {
          this.getData()
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error resetting VM', [error?.detail || error.message])
        })
    },
    removeVm() {
      this.$refs.confirmDialog.show(
        'Remove VM',
        ['Are you sure you want to remove the selected VM?'],
        () => {
          const api = useApi()
          api.vm
            .delete(this.selectedVm[0].id)
            .then(() => {
              this.getData()
            })
            .catch((error) => {
              this.$refs.errorDialog.show('Error removing VM', [error?.detail || error.message])
            })
        },
      )
    },
  },
  mounted() {
    this.getData()
  },
}
</script>
