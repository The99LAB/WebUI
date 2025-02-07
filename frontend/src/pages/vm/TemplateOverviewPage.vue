<template>
  <q-page padding>
    <q-table
      title="VM Templates"
      :rows="data"
      :columns="columns"
      row-key="id"
      selection="single"
      :loading="tableLoading"
      v-model:selected="selectedTemplate"
    >
      <template v-slot:top-right>
        <q-btn flat round color="primary" icon="refresh" @click="getData">
          <ToolTip content="Refresh" />
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-eye"
          :disable="selectedTemplate.length === 0"
          @click="viewTemplate"
        >
          <ToolTip content="View" />
        </q-btn>
      </template>
      <template v-slot:body-selection="props">
        <q-checkbox v-model="props.selected" />
      </template>
    </q-table>
  </q-page>
  <q-dialog v-model="viewtemplate">
    <q-card style="min-width: 70vw">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">{{ selectedTemplate[0].name }}</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none">
        <div v-for="(value, key) in selectedTemplate[0]" :key="key">
          <strong>{{ key.replace(/_/g, " ").toUpperCase() }}:</strong>
          {{ value }}
        </div>
      </q-card-section>
      <q-card-section>
        <div><strong>XML Template:</strong></div>
        <q-input
          filled
          v-model="selectedTemplateXml"
          type="textarea"
          autogrow
          readonly
        />
      </q-card-section>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
  <ConfirmDialog ref="confirmDialog" />
  <ToolTip ref="toolTip" />
</template>

<script>
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";
import ToolTip from "src/components/ToolTip.vue";

export default {
  data() {
    return {
      data: [],
      columns: [
        {
          name: "id",
          label: "ID",
          field: "id",
          align: "left",
          sortable: true,
        },
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "description",
          label: "Description",
          field: "description",
          align: "left",
          sortable: false,
        },
      ],
      tableLoading: false,
      selectedTemplate: [],
      selectedTemplateXml: null,
      viewtemplate: false,
    };
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
    ToolTip,
  },
  methods: {
    getData() {
      this.selectedTemplate = [];
      this.tableLoading = true;
      this.$api
        .get("/vm/templates")
        .then((response) => {
          this.data = response.data;
          this.tableLoading = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error loading VM templates", [
            error.response.data.detail,
          ]);
          this.tableLoading = false;
        });
    },
    viewTemplate() {
      this.viewtemplate = true;
      this.selectedTemplateXml = null;
      this.$api
        .get("/vm/xml_templates/" + this.selectedTemplate[0].xml_template_id)
        .then((response) => {
          this.selectedTemplateXml = response.data.content;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error loading XML template", [
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
