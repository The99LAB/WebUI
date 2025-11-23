<template>
  <q-page padding>
    <q-table
      title="VM Network Bridges"
      :rows="networkBridgesData"
      :columns="networkBridgesColumns"
      row-key="id"
      selection="single"
      :loading="networkBridgesLoading"
      v-model:selected="networkBridgesSelected"
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
            :disable="networkBridgesSelected.length === 0"
            @click="openNetworkBridgeEdit"
          >
            <ToolTip content="Edit" />
          </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-plus"
          @click="openAddBridge"
        >
          <ToolTip content="Add" />
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-play-circle"
          @click="applyBridgeNetworks"
        >
          <ToolTip content="Apply" />
        </q-btn>
        <q-btn
          flat
          round
          color="negative"
          icon="mdi-delete"
          :disable="networkBridgesSelected.length === 0"
          @click="removeBridgeNetwork"
        >
          <ToolTip content="Delete" />
        </q-btn>
      </template>
      <template v-slot:body-selection="props">
        <q-checkbox v-model="props.selected" />
      </template>
    </q-table>
    <q-separator color="transparent" spaced="lg" inset />
    <q-table
      title="VM Network Custom"
      :rows="networkCustomData"
      :columns="networkCustomColumns"
      row-key="id"
      selection="single"
      :loading="networkCustomLoading"
      v-model:selected="networkCustomSelected"
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
          :disable="networkCustomSelected.length === 0"
          @click="openNetworkCustomEdit"
        >
          <ToolTip content="View" />
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-plus"
          @click="openAddCustom"
        >
          <ToolTip content="Add" />
        </q-btn>
        <q-btn
          flat
          round
          color="negative"
          icon="mdi-delete"
          :disable="networkCustomSelected.length === 0"
          @click="removeCustomNetwork"
        >
          <ToolTip content="Delete" />
        </q-btn>
      </template>
      <template v-slot:body-selection="props">
        <q-checkbox v-model="props.selected" />
      </template>
    </q-table>
  </q-page>
  <q-dialog v-model="networkBridgeEditDialog">
    <q-card style="min-width: 70vw">
      <q-card-section class="row items-center q-pb-none">
        <div v-if="editedBridge && editedBridge.id" class="text-h6">Edit bridge network '{{ editedBridge.name }}'</div>
        <div v-else class="text-h6">Create bridge network</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="networkBridgeEditDialog = false" />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none">
        <q-form @submit.prevent="saveNetworkBridge">
          <div class="row q-col-gutter-md">
            <div class="col-12">
              <q-input filled v-model="editedBridge.name" label="Name" />
            </div>
            <div class="col-12">
              <q-input filled v-model="editedBridge.bridge_name" label="Bridge Name" />
            </div>
            <div class="col-12">
              <q-input filled v-model="editedBridge.description" label="Description" type="textarea" autogrow />
            </div>
            <div class="col-12">
              <q-checkbox v-model="editedBridge.autostart" label="Autostart" />
            </div>
          </div>
        </q-form>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" @click="networkBridgeEditDialog = false" />
        <q-btn flat label="Save" color="primary" @click="saveNetworkBridge" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <q-dialog v-model="networkCustomEditDialog">
    <q-card style="min-width: 70vw">
      <q-card-section class="row items-center q-pb-none">
        <div v-if="editedCustom && editedCustom.id" class="text-h6">Edit custom network '{{ editedCustom.name }}'</div>
        <div v-else class="text-h6">Create custom network</div>
        <q-space />
        <q-btn icon="close" flat round dense @click="networkCustomEditDialog = false" />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none">
        <q-form @submit.prevent="saveNetworkBridge">
          <div class="row q-col-gutter-md">
            <div class="col-12">
              <q-input filled v-model="editedCustom.name" label="Name" />
            </div>
            <div class="col-12">
              <q-input filled v-model="editedCustom.description" label="Description" type="textarea" autogrow />
            </div>
            <div class="col-12">
              <q-checkbox v-model="editedCustom.autostart" label="Autostart" />
            </div>
            <div class="col-12">
              <q-input filled v-model="editedCustom.xml_content" label="XML" type="textarea" autogrow />
            </div>
          </div>
        </q-form>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Cancel" color="primary" @click="networkCustomEditDialog = false" />
        <q-btn flat label="Save" color="primary" @click="saveNetworkCustom" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
  <ConfirmDialog ref="confirmDialog" />
  <ToolTip ref="toolTip" />
  <q-dialog v-model="applyResultDialog">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Apply Result</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup @click="applyResultDialog = false" />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none">
        <div v-if="applyResult">
          <div>Checked: {{ applyResult.checked }}</div>
          <div>Removed: {{ applyResult.removed }}</div>
          <div>Defined: {{ applyResult.defined }}</div>
          <div>Started: {{ applyResult.started }}</div>
          <div v-if="applyResult.errors && applyResult.errors.length">
            <div class="q-mt-sm text-subtitle2">Errors:</div>
            <ul>
              <li v-for="(err, idx) in applyResult.errors" :key="idx">{{ err }}</li>
            </ul>
          </div>
        </div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Close" color="primary" @click="applyResultDialog = false" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import ErrorDialog from 'src/components/ErrorDialog.vue'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import ToolTip from 'src/components/ToolTip.vue'
import { useApi } from 'src/composables/useApi'

export default {
  data() {
    return {
      networkBridgeEditDialog: false,
      editedBridge: {},
      networkBridgesData: [],
      networkBridgesColumns: [
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
          name: 'description',
          label: 'Description',
          field: 'description',
          align: 'left',
          sortable: true,
        },
        {
          name: 'bridge_name',
          label: 'Bridge Name',
          field: 'bridge_name',
          align: 'left',
          sortable: true,
        },
        {
          name: 'active',
          label: 'Active',
          field: 'active',
          align: 'left',
          sortable: true,
        },
        {
          name: 'autostart',
          label: 'Autostart',
          field: 'autostart',
          align: 'left',
          sortable: true,
        }
      ],
      networkBridgesLoading: false,
      networkBridgesSelected: [],
      applyResultDialog: false,
      applyResult: null,

      networkCustomEditDialog: false,
      editedCustom: {},
      networkCustomData: [],
      networkCustomColumns: [
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
          name: 'description',
          label: 'Description',
          field: 'description',
          align: 'left',
          sortable: true,
        },
        {
          name: 'active',
          label: 'Active',
          field: 'active',
          align: 'left',
          sortable: true,
        },
        {
          name: 'autostart',
          label: 'Autostart',
          field: 'autostart',
          align: 'left',
          sortable: true,
        }
      ],
      networkCustomLoading: false,
      networkCustomSelected: [],
    }
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
    ToolTip,
  },
  methods: {
    openNetworkBridgeEdit() {
      if (!this.networkBridgesSelected || this.networkBridgesSelected.length === 0) return
      const sel = this.networkBridgesSelected[0]
      const api = useApi()
      api.vm
        .getBridgeNetwork(sel.id)
        .then((data) => {
          // create editable copy
          this.editedBridge = JSON.parse(JSON.stringify(data))
          // ensure boolean for checkbox
          if (typeof this.editedBridge.autostart === 'string') {
            this.editedBridge.autostart = this.editedBridge.autostart === 'true'
          }
          this.networkBridgeEditDialog = true
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading bridge', [error?.detail || error.message])
        })
    },

    openAddBridge() {
      this.editedBridge = {
        name: '',
        bridge_name: '',
        description: '',
        autostart: false,
      }
      this.networkBridgeEditDialog = true
    },

    openNetworkCustomEdit() {
      if (!this.networkCustomSelected || this.networkCustomSelected.length === 0) return
      const sel = this.networkCustomSelected[0]
      const api = useApi()
      api.vm
        .getCustomNetwork(sel.id)
        .then((data) => {
          // create editable copy
          this.editedCustom = JSON.parse(JSON.stringify(data))
          // ensure boolean for checkbox
          if (typeof this.editedCustom.autostart === 'string') {
            this.editedCustom.autostart = this.editedCustom.autostart === 'true'
          }
          this.networkCustomEditDialog = true
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading bridge', [error?.detail || error.message])
        })
    },

    openAddCustom() {
      this.editedCustom = {
        name: '',
        xml_content: '',
        description: '',
        autostart: false,
      }
      this.networkCustomEditDialog = true
    },

    saveNetworkBridge() {
      if (!this.editedBridge) return
      const api = useApi()
      if (this.editedBridge.id) {
        api.vm
          .updateBridgeNetwork(this.editedBridge.id, this.editedBridge)
          .then(() => {
            this.networkBridgeEditDialog = false
            this.getData()
          })
          .catch((error) => {
            this.$refs.errorDialog.show('Error saving bridge network', [error?.detail || error.message])
          })
      } else {
        api.vm
          .createBridgeNetwork(this.editedBridge)
          .then(() => {
            this.networkBridgeEditDialog = false
            this.getData()
          })
          .catch((error) => {
            this.$refs.errorDialog.show('Error creating bridge network', [error?.detail || error.message])
          })
      }
    },

    saveNetworkCustom() {
      if (!this.editedCustom) return
      const api = useApi()
      if (this.editedCustom.id) {
        api.vm
          .updateCustomNetwork(this.editedCustom.id, this.editedCustom)
          .then(() => {
            this.networkCustomEditDialog = false
            this.getData()
          })
          .catch((error) => {
            this.$refs.errorDialog.show('Error saving custom network', [error?.detail || error.message])
          })
      } else {
        api.vm
          .createCustomNetwork(this.editedCustom)
          .then(() => {
            this.networkCustomEditDialog = false
            this.getData()
          })
          .catch((error) => {
            this.$refs.errorDialog.show('Error creating custom network', [error?.detail || error.message])
          })
      }
    },

    removeBridgeNetwork() {
      if (!this.networkBridgesSelected || this.networkBridgesSelected.length === 0) return
      const sel = this.networkBridgesSelected[0]
      this.$refs.confirmDialog.show(
        'Delete bridge network',
        ['Are you sure you want to delete the selected bridge network?'],
        () => {
          const api = useApi()
          api.vm
            .deleteBridgeNetwork(sel.id)
            .then(() => {
              this.getData()
            })
            .catch((error) => {
              this.$refs.errorDialog.show('Error deleting bridge network', [error?.detail || error.message])
            })
        },
      )
    },

    removeCustomNetwork() {
      if (!this.networkCustomSelected || this.networkCustomSelected.length === 0) return
      const sel = this.networkCustomSelected[0]
      this.$refs.confirmDialog.show(
        'Delete custom network',
        ['Are you sure you want to delete the selected custom network?'],
        () => {
          const api = useApi()
          api.vm
            .deleteCustomNetwork(sel.id)
            .then(() => {
              this.getData()
            })
            .catch((error) => {
              this.$refs.errorDialog.show('Error deleting custom network', [error?.detail || error.message])
            })
        },
      )
    },

    getData() {
      this.networkBridgesSelected = []
      this.networkCustomSelected = []
      this.networkBridgesLoading = true
      this.networkCustomLoading = true

      const api = useApi()
      api.vm
        .getBridgeNetworks()
        .then((data) => {
          this.networkBridgesData = data
          this.networkBridgesLoading = false
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading VM templates', [error?.detail || error.message])
          this.networkBridgesLoading = false
        })

      api.vm
        .getCustomNetworks()
        .then((data) => {
          this.networkCustomData = data
          this.networkCustomLoading = false
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading VM templates', [error?.detail || error.message])
          this.networkCustomLoading = false
        })
    },

    applyBridgeNetworks() {
      this.$refs.confirmDialog.show(
        'Apply bridge networks',
        ['This will remove any existing libvirt definitions for the bridges and (re)define and start networks configured in the database. Continue?'],
        () => {
          const api = useApi()
          api.vm
            .applyBridgeNetworks()
            .then((res) => {
              this.applyResult = res
              this.applyResultDialog = true
              // refresh data after applying
              this.getData()
            })
            .catch((error) => {
              this.$refs.errorDialog.show('Error applying bridge networks', [error?.detail || error.message])
            })
        },
        () => {}
      )
    },

  },
  mounted() {
    this.getData()
  },
}
</script>
