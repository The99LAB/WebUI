<template>
  <q-page padding>
    <q-table
      title="Settings"
      :rows="rows"
      :columns="columns"
      row-key="name"
      selection="single"
      v-model:selected="selected"
    />
  </q-page>
</template>

<script>
import { ref } from "vue";

const rows = [
  { name: "Hostname", value: "raspberrypi" },
  { name: "IP Address", value: "" },
];

const columns = [
  { name: "name", label: "Name", field: "name", align: "left", sortable: true },
  {
    name: "value",
    label: "Value",
    field: "value",
    align: "left",
    sortable: true,
  },
];

export default {
  data() {
    return {
      selected: ref([]),
      rows,
      columns,
    };
  },
};
</script>
