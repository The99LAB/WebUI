<template>
  <q-page padding>
    <q-table
      title="Template Repositories"
      :rows="templateRepos"
      :columns="templateTableColums"
      row-key="id"
      selection="single"
      :pagination="templateTablePagination"
      v-model:selected="templateRepoSelected"
      :loading="templateTableLoading"
      hide-selected-banner
    >
      <template v-slot:top-right>
          <q-btn
            color="primary"
            icon="mdi-plus"
            round
            flat
            @click="templateAddRepoDialog = true"
            :disable="templateRepoSelected.length != 0"
          >
            <q-tooltip :offset="[5,5]">
              Add template repository
            </q-tooltip>
          </q-btn>
          <q-btn
            color="primary"
            round
            flat
            icon="mdi-delete"
            @click="
              $refs.confirmDialog.show(
                'Are you sure?',
                ['Are you sure you want to delete this template repository?'],
                templateRepoDelete,
              )
            "
            :disable="!templateRepoSelected.length"
          >
            <q-tooltip :offset="[5,5]">
              Delete template repository
            </q-tooltip>
          </q-btn>
          <q-btn
            color="primary"
            round
            flat
            icon="mdi-pencil"
            @click="templateRepoEditDialog = true"
            :disable="!templateRepoSelected.length"
          >
            <q-tooltip :offset="[5,5]">
              Edit template repository
            </q-tooltip>
          </q-btn>

      </template>
    </q-table>
    <ConfirmDialog ref="confirmDialog" />
    <q-dialog v-model="templateRepoEditDialog">
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Edit Template Repository</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <q-form @submit="templateRepoEdit" class="q-gutter-xs">
            <q-input
              v-model="templateRepoSelected[0].name"
              label="Name *"
              style="width: 35em"
              lazy-rules="ondemand"
              :rules="templateRepoNameRule"
            />
            <q-input
              v-model="templateRepoSelected[0].url"
              label="URL *"
              style="width: 35em"
              lazy-rules="ondemand"
              :rules="templateRepoUrlRule"
            />
            <q-input
              v-model="templateRepoSelected[0].branch"
              label="Branch *"
              style="width: 35em"
              lazy-rules="ondemand"
              :rules="templateRepoBranchRule"
            />
            <div class="row">
              <q-space />
              <q-btn label="Submit" type="submit" flat color="primary" />
            </div>
          </q-form>
        </q-card-section>
      </q-card>
      <q-inner-loading :showing="editDialogLoading" />
    </q-dialog>
    <q-dialog v-model="templateAddRepoDialog">
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Add Template Repository</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="md" inset />
        <q-card-section>
          <q-form @submit="templateRepoAdd" class="q-gutter-md">
            <q-input
              filled
              v-model="templateAddRepoData.name"
              label="Name *"
              hint="Name of the template repository"
              lazy-rules="ondemand"
              :rules="templateRepoNameRule"
            />
            <q-separator spaced="lg" color="transparent" />
            <q-input
              filled
              v-model="templateAddRepoData.url"
              label="URL *"
              hint="URL of the template repository"
              lazy-rules="ondemand"
              :rules="templateRepoUrlRule"
            />
            <q-separator spaced="lg" color="transparent" />
            <q-input
              filled
              v-model="templateAddRepoData.branch"
              label="Branch *"
              hint="Branch of the template repository"
              lazy-rules="ondemand"
              :rules="templateRepoBranchRule"
            />
            <div class="row">
              <q-space />
              <q-btn label="Submit" type="submit" flat color="primary" />
            </div>
          </q-form>
        </q-card-section>
        <q-inner-loading :showing="templateAddRepoDialogLoading" />
      </q-card>
      <q-inner-loading :showing="editDialogLoading" />
    </q-dialog>
    <q-inner-loading :showing="loadingVisible" />
    <ErrorDialog ref="errorDialog" />
  </q-page>
</template>

<script>
import ConfirmDialog from "src/components/ConfirmDialog.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      templateRepos: [],
      templateTableColums: [
        {
          name: "name",
          label: "Name",
          field: "name",
          align: "left",
          sortable: true,
        },
        {
          name: "url",
          label: "URL",
          field: "url",
          align: "left",
          sortable: true,
        },
        {
          name: "branch",
          label: "Branch",
          field: "branch",
          align: "left",
          sortable: true,
        },
      ],
      templateTablePagination: {
        sortBy: "id",
        rowsPerPage: 15,
      },
      templateRepoSelected: [],
      templateRepoEditDialog: false,
      loadingVisible: false,
      editDialogLoading: false,
      templateTableLoading: false,
      templateAddRepoData: {
        name: null,
        url: null,
        branch: "master",
      },
      templateAddRepoDialog: false,
      templateAddRepoDialogLoading: false,
      templateRepoNameRule: [
        (val) => (val && val.length > 0) || "Please type something",
      ],
      templateRepoUrlRule: [
        (val) => (val && val.length > 0) || "Please type something",
        (val) => (val && val.startsWith("http")) || "Please type a valid URL",
      ],
      templateRepoBranchRule: [
        (val) => (val && val.length > 0) || "Please type something",
      ],
    };
  },
  components: {
    ConfirmDialog,
    ErrorDialog,
  },
  methods: {
    getTemplateRepos() {
      this.templateTableLoading = true;
      this.$api
        .get("docker-manager/template-locations")
        .then((response) => {
          this.templateRepos = response.data;
          this.templateTableLoading = false;
        })
        .catch((error) => {
          let errormsg;
          if (error.response === undefined) {
            errormsg = "Error fetching template locations";
          } else {
            errormsg = error.response.data.message;
          }
          this.$refs.errorDialog.show("Error fetching template locations", [
            errormsg,
          ]);
        });
    },
    templateRepoAdd() {
      this.templateAddRepoDialogLoading = true;
      this.$api
        .post("docker-manager/template-locations", this.templateAddRepoData)
        .then((response) => {
          this.templateAddRepoDialogLoading = false;
          this.templateAddRepoDialog = false;
          this.getTemplateRepos();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error adding template repository", [
            error.response.data.message,
          ]);
          this.templateAddRepoDialogLoading = false;
          this.templateAddRepoDialog = false;
        });
    },
    templateRepoDelete() {
      this.templateTableLoading = true;
      this.$api
        .delete("docker-manager/template-locations", {
          data: {
            id: this.templateRepoSelected[0].id,
          },
        })
        .then((response) => {
          this.getTemplateRepos();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error deleting template repository", [
            error.response.data.message,
          ]);
        });
    },
    templateRepoEdit() {
      this.editDialogLoading = true;
      this.$api
        .put("docker-manager/template-locations", this.templateRepoSelected[0])
        .then((response) => {
          this.editDialogLoading = false;
          this.templateRepoEditDialog = false;
          this.getTemplateRepos();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error editing template repository", [
            error.response.data.message,
          ]);
          this.editDialogLoading = false;
          this.templateRepoEditDialog = false;
        });
    },
  },
  mounted() {
    this.getTemplateRepos();
  },
};
</script>
