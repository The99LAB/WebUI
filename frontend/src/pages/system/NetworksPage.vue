<template>
  <q-page padding>
    <q-table
      title="Networks"
      :rows="networks"
      :columns="columns"
      row-key="id"
      selection="single"
      v-model:selected="selectedNetwork"
      :loading="tableLoading"
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
          :disable="selectedNetwork.length === 0"
          @click="$refs.editNetwork.show(selectedNetwork[0])"
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
  <EditNetwork ref="editNetwork" @network-edit-finished="getData" />
</template>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";
import EditNetwork from "src/components/system/EditNetwork.vue";
import ToolTip from "src/components/ToolTip.vue";

export default {
  data() {
    return {
      networks: [],
      columns: [
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "ipv4_method",
          label: "IPv4 Method",
          field: "ipv4_method",
          align: "left",
          sortable: true,
        },
        {
          name: "ipv4_address",
          label: "IPv4 Address",
          field: "ipv4_address_prefix",
          align: "left",
          sortable: true,
        },
        {
          name: "ipv4_gateway",
          label: "IPv4 Gateway",
          field: "ipv4_gateway",
          align: "left",
          sortable: true,
        },
      ],
      selectedNetwork: [],
      tableLoading: false,
    };
  },
  components: {
    ErrorDialog,
    EditNetwork,
    ToolTip,
  },
  methods: {
    getData() {
      this.selectedNetwork = [];
      this.tableLoading = true;
      this.$api
        .get("/system/networks")
        .then((response) => {
          this.networks = response.data.map((network) => {
            return {
              ...network,
              ipv4_address_prefix: `${network.ipv4_address}/${network.ipv4_prefix}`,
            };
          });
          this.tableLoading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error loading networks", [
            error.response.data.detail,
          ]);
        });
    },
  },
  mounted() {
    this.getData();
  },
};
</script>
