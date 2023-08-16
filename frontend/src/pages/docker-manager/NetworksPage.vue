<template>
  <q-page padding>
    <q-table
      title="Networks"
      :rows="dockerNetworks"
      :columns="dockerNetworksColumns"
      row-key="id"
      :pagination="dockerNetworksPagination"
      :loading="dockerNetworksLoading"
      selection="single"
      v-model:selected="selectedNetwork"
      hide-selected-banner
    >
      <template v-slot:top-right>
        <q-btn
          color="primary"
          icon="mdi-delete"
          round
          flat
          @click="
            $refs.confirmDialog.show(
              'Delete Network',
              ['Are you sure you want to delete this network?'],
              networkDelete,
            )
          "
          :disable="selectedNetwork.length == 0"
        >
          <q-tooltip :offset="[5, 5]"> Delete Network </q-tooltip>
        </q-btn>
      </template>
    </q-table>
    <errorDialog ref="errorDialog" />
    <ConfirmDialog ref="confirmDialog" />
  </q-page>
</template>

<script>
import errorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";

export default {
  data() {
    return {
      dockerNetworksColumns: [
        {
          label: "Name",
          field: "name",
          name: "name",
          align: "left",
          sortable: true,
        },
        {
          label: "Network ID",
          field: "id",
          name: "id",
          align: "left",
          sortable: true,
        },
        {
          label: "Driver",
          field: "driver",
          name: "driver",
          align: "left",
          sortable: true,
        },
        {
          label: "Scope",
          field: "scope",
          name: "scope",
          align: "left",
          sortable: true,
        },
      ],
      dockerNetworks: [],
      dockerNetworksPagination: {
        sortBy: "name",
        rowsPerPage: 15,
      },
      selectedNetwork: [],
      dockerNetworksLoading: false,
    };
  },
  components: {
    errorDialog,
    ConfirmDialog,
  },
  methods: {
    getdockerNetworks() {
      this.dockerNetworksLoading = true;
      this.$api
        .get("docker-manager/networks")
        .then((response) => {
          this.dockerNetworks = response.data;
          this.dockerNetworksLoading = false;
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error fetching docker networks", [
            errormsg,
          ]);
        });
    },
    networkDelete() {
      this.dockerNetworksLoading = true;
      this.$api
        .delete("docker-manager/network" + this.selectedNetwork[0].id)
        .then((response) => {
          this.getdockerNetworks();
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error deleting docker network", [
            errormsg,
          ]);
        });
    },
  },
  mounted() {
    this.getdockerNetworks();
  },
};
</script>
