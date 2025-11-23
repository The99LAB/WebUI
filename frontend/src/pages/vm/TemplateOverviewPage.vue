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
    <q-separator color="transparent" spaced="lg" inset />
    <q-table
      title="XML Templates"
      :rows="xmlData"
      :columns="xmlColumns"
      row-key="id"
      selection="single"
      :loading="xmlTableLoading"
      v-model:selected="selectedXmlTemplate"
    >
      <template v-slot:top-right>
        <q-btn flat round color="primary" icon="refresh" @click="getXmlTemplates">
          <ToolTip content="Refresh" />
        </q-btn>
        <q-btn
          flat
          round
          color="primary"
          icon="mdi-eye"
          :disable="selectedXmlTemplate.length === 0"
          @click="viewXmlTemplate"
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
          <strong>{{ key.replace(/_/g, ' ').toUpperCase() }}:</strong>
          {{ value }}
        </div>
      </q-card-section>
      <q-card-section>
        <div><strong>XML Template:</strong></div>
        <q-input filled v-model="selectedTemplateXml" type="textarea" autogrow readonly />
      </q-card-section>
    </q-card>
  </q-dialog>
  <q-dialog v-model="viewXmlDialog">
    <q-card style="min-width: 70vw">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">{{ selectedXmlTemplate[0]?.name }}</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none">
        <div v-if="selectedXmlTemplate[0]">
          <div v-for="(value, key) in selectedXmlTemplate[0]" :key="key">
            <strong>{{ key.replace(/_/g, ' ').toUpperCase() }}:</strong>
            {{ value }}
          </div>
        </div>
      </q-card-section>
      <q-card-section>
        <div><strong>XML Template:</strong></div>
        <q-input filled v-model="selectedXmlTemplateContent" type="textarea" autogrow readonly />
      </q-card-section>
    </q-card>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
  <ConfirmDialog ref="confirmDialog" />
  <ToolTip ref="toolTip" />
</template>

<script>
import ErrorDialog from 'src/components/ErrorDialog.vue'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import ToolTip from 'src/components/ToolTip.vue'
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
          name: 'description',
          label: 'Description',
          field: 'description',
          align: 'left',
          sortable: true,
        },
        {
          name: 'xml_template_id',
          label: 'XML Template ID',
          field: 'xml_template_id',
          align: 'left',
          sortable: true,
        }
      ],
        tableLoading: false,
        selectedTemplate: [],
        selectedTemplateXml: null,
        viewtemplate: false,

        /* XML templates table */
        xmlData: [],
        xmlColumns: [
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
          }
        ],
        xmlTableLoading: false,
        selectedXmlTemplate: [],
        selectedXmlTemplateContent: null,
        viewXmlDialog: false,
    }
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
    ToolTip,
  },
  methods: {
    getData() {
      this.selectedTemplate = []
      this.tableLoading = true

      const api = useApi()
      api.vm
        .getTemplatesBasic()
        .then((data) => {
          this.data = data
          this.tableLoading = false
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading VM templates', [error?.detail || error.message])
          this.tableLoading = false
        })
    },
    getXmlTemplates() {
      this.selectedXmlTemplate = []
      this.xmlTableLoading = true

      const api = useApi()
      api.vm
        .getXmlTemplates()
        .then((data) => {
          this.xmlData = data
          this.xmlTableLoading = false
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading XML templates', [error?.detail || error.message])
          this.xmlTableLoading = false
        })
    },
    viewXmlTemplate() {
      this.viewXmlDialog = true
      this.selectedXmlTemplateContent = null

      const api = useApi()
      // XML template objects typically expose `id`
      const xmlId = this.selectedXmlTemplate[0].id
      api.vm
        .getXmlTemplate(xmlId)
        .then((data) => {
          this.selectedXmlTemplateContent = data.content
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading XML template', [error?.detail || error.message])
        })
    },
    viewTemplate() {
      this.viewtemplate = true
      this.selectedTemplateXml = null

      const api = useApi()
      api.vm
        .getXmlTemplate(this.selectedTemplate[0].xml_template_id)
        .then((data) => {
          this.selectedTemplateXml = data.content
        })
        .catch((error) => {
          this.$refs.errorDialog.show('Error loading XML template', [error?.detail || error.message])
        })
    },
  },
  mounted() {
    this.getData()
    this.getXmlTemplates()
  },
}
</script>
