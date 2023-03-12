<template>
  <q-page padding>
    <div class="row">
      <q-space />
      <q-btn
        class="q-ma-sm"
        color="primary"
        icon="mdi-plus"
        label="Create config"
      />
    </div>
    <q-table
      :loading="backupTableLoading"
      :rows="rows"
      :columns="columns"
      row-key="config"
      separator="none"
      no-data-label="Failed to get data from backend or no configs defined"
      hide-pagination
    >
      <template #body="props">
        <q-tr :props="props">
          <q-td key="config" :props="props">
            <q-btn
              flat
              round
              :icon="props.row.expand ? 'mdi-menu-down' : 'mdi-menu-right'"
              @click="props.row.expand = !props.row.expand"
              no-caps
              :label="props.row.config"
              class="text-weight-regular text-body2"
            />
          </q-td>
          <q-td
            key="backups"
            :props="props"
            class="text-weight-regular text-body2"
          >
            {{ props.row.backups }}
          </q-td>
        </q-tr>

        <q-tr v-show="props.row.expand" :props="props">
          <q-td colspan="100%">
            <div class="row">
              <q-tabs v-model="props.row.tab">
                <q-tab name="overview" label="Overview" />
                <!-- <q-tab name="backups" label="Backups" /> -->
              </q-tabs>
            </div>
            <q-tab-panels v-model="props.row.tab">
              <q-tab-panel name="overview">
                <div class="row q-ma-sm">
                  <q-btn
                    class="q-mr-sm"
                    color="primary"
                    icon="mdi-delete"
                    label="Delete"
                  />
                </div>
                <div class="row q-ma-sm">
                  <p class="text-body2 text-weight-bold q-mr-sm">
                    Destination:
                  </p>
                  <p class="text-body2">{{ props.row.destination }}</p>
                </div>
              </q-tab-panel>
            </q-tab-panels>
          </q-td>
        </q-tr>
      </template>
    </q-table>
    <ErrorDialog ref="errorDialog"></ErrorDialog>
  </q-page>
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

const rows = [
  {
    config: "Arch",
    backups: "0",
    destination: "/mnt/KVMBackups",
    tab: "overview",
  },
];

const columns = [
  { label: "Config", field: "config", name: "config", align: "left" },
  { label: "Backups", field: "backups", name: "backups", align: "left" },
];

export default {
  data() {
    return {
      rows,
      columns,
      backupTableLoading: ref(false),
      backupTablePagination: {
        sortBy: "name",
        rowsPerPage: 0,
      },
    };
  },
  components: {
    ErrorDialog,
  },
  methods: {},
};
</script>
