<template>
  <q-page padding>
    <q-table
      title="Ethernet Interfaces"
      :rows="ethernets"
      :columns="ethernet_columns"
      row-key="id"
      selection="single"
      v-model:selected="ethernetSelected"
      :loading="ethernetTableLoading"
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
          icon="edit"
          :disable="ethernetSelected.length === 0"
          @click="$refs.editEthernet.show(ethernetSelected[0])"
        >
          <ToolTip content="Edit" />
        </q-btn>
      </template>
      <template v-slot:body-selection="props">
        <q-checkbox v-model="props.selected" />
      </template>
    </q-table>
    <q-separator color="transparent" spaced="lg" inset />
    <q-table
      title="Bridge Interfaces"
      :rows="bridges"
      :columns="bridges_columns"
      row-key="id"
      selection="single"
      v-model:selected="bridgeSelected"
      :loading="bridgesTableLoading"
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
          icon="edit"
          :disable="bridgeSelected.length === 0"
          @click="$refs.editBridge.show(bridgeSelected[0])"
        >
          <ToolTip content="Edit" />
        </q-btn>
      </template>
      <template v-slot:body-selection="props">
        <q-checkbox v-model="props.selected" />
      </template>
    </q-table>
  </q-page>
  <ErrorDialog ref="errorDialog" />
  <EditEthernet ref="editEthernet" @ethernet-edit-finished="getData" />
  <EditBridge ref="editBridge" @bridge-edit-finished="getData" />
</template>

<script>
import ErrorDialog from 'src/components/ErrorDialog.vue'
import EditEthernet from 'src/components/system/EditEthernet.vue'
import EditBridge from 'src/components/system/EditBridge.vue'
import ToolTip from 'src/components/ToolTip.vue'
import { useApi } from 'src/composables/useApi'

export default {
  data() {
    return {
      pagination: {
        rowsPerPage: 0,
        sortBy: 'id',
        descending: false,
      },
      ethernets: [],
      bridges: [],
      ethernet_columns: [
        {
          name: 'name',
          label: 'Name',
          field: 'name',
          align: 'left',
          sortable: true,
        },
        {
          name: 'ipv4_method',
          label: 'IPv4 Method',
          field: 'ipv4_method',
          align: 'left',
          sortable: true,
        },
        {
          name: 'ipv4_address',
          label: 'IPv4 Address',
          field: 'ipv4_address_prefix',
          align: 'left',
          sortable: true,
        },
        {
          name: 'ipv4_gateway',
          label: 'IPv4 Gateway',
          field: 'ipv4_gateway',
          align: 'left',
          sortable: true,
        },
        {
          name: 'ipv4_dns',
          label: 'IPv4 DNS',
          field: 'ipv4_dns',
          align: 'left',
          sortable: true,
        }
      ],
      bridges_columns: [
        {
          name: 'name',
          label: 'Name',
          field: 'bridge_name',
          align: 'left',
          sortable: true,
        },
        {
          name: 'ethernet',
          label: 'Ethernet',
          field: 'interface_name',
          align: 'left',
          sortable: true,
        },
        {
          name: 'ipv4_method',
          label: 'IPv4 Method',
          field: 'ipv4_method',
          align: 'left',
          sortable: true,
        },
        {
          name: 'ipv4_address',
          label: 'IPv4 Address',
          field: 'ipv4_address_prefix',
          align: 'left',
          sortable: true,
        },
        {
          name: 'ipv4_gateway',
          label: 'IPv4 Gateway',
          field: 'ipv4_gateway',
          align: 'left',
          sortable: true,
        },
        {
          name: 'ipv4_dns',
          label: 'IPv4 DNS',
          field: 'ipv4_dns',
          align: 'left',
          sortable: true,
        }
      ],
      ethernetSelected: [],
      ethernetTableLoading: false,
      bridgeSelected: [],
      bridgesTableLoading: false,
    }
  },
  components: {
    ErrorDialog,
    EditEthernet,
    EditBridge,
    ToolTip,
  },
  methods: {
    async getData() {
      this.ethernetSelected = []
      this.bridgeSelected = []
      this.ethernetTableLoading = true
      this.bridgesTableLoading = true

      const api = useApi()

      try {
        const ethernetData = await api.networks.getEthernets()
        this.ethernets = ethernetData.map((network) => {
          return {
            ...network,
            ipv4_method: network.ipv4_method || 'N/A',
            ipv4_address: network.ipv4_address || 'N/A',
            ipv4_prefix: network.ipv4_prefix || 'N/A',
            ipv4_gateway: network.ipv4_gateway || 'N/A',
            ipv4_dns: Array.isArray(network.ipv4_dns) ? network.ipv4_dns.join(',') : (network.ipv4_dns || 'N/A'),
            ipv4_address_prefix:
              network.ipv4_address && network.ipv4_prefix
                ? `${network.ipv4_address}/${network.ipv4_prefix}`
                : 'N/A',
          }
        })
        this.ethernetTableLoading = false
      } catch (error) {
        this.$refs.errorDialog.show('Error loading ethernets', [error?.detail || error.message])
        this.ethernetTableLoading = false
      }

      try {
        const bridgeData = await api.networks.getBridges()
        this.bridges = bridgeData.map((bridge) => {
          return {
            ...bridge,
            ipv4_method: bridge.ipv4_method || 'N/A',
            ipv4_address: bridge.ipv4_address || 'N/A',
            ipv4_prefix: bridge.ipv4_prefix || 'N/A',
            ipv4_gateway: bridge.ipv4_gateway || 'N/A',
            ipv4_dns: Array.isArray(bridge.ipv4_dns) ? bridge.ipv4_dns.join(',') : (bridge.ipv4_dns || 'N/A'),
            ipv4_address_prefix:
              bridge.ipv4_address && bridge.ipv4_prefix
                ? `${bridge.ipv4_address}/${bridge.ipv4_prefix}`
                : 'N/A',
          }
        })
        this.bridgesTableLoading = false
      } catch (error) {
        this.$refs.errorDialog.show('Error loading bridges', [error?.detail || error.message])
        this.bridgesTableLoading = false
      }
    },
  },
  mounted() {
    this.getData()
  },
}
</script>
