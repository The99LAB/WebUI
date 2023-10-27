<template>
  <q-page padding>
    <q-select
      class="q-mb-md"
      style="width: 250px"
      v-model="templateRepoSelected"
      :options="templateRepos"
      label="Template Repositories"
      filled
      multiple
      option-label="name"
      @update:model-value="templatesFetch"
    >
      <template v-slot:option="scope">
        <q-item v-bind="scope.itemProps">
          <q-item-section>
            <q-item-label>{{ scope.opt.name }}</q-item-label>
          </q-item-section>
        </q-item>
      </template>
    </q-select>
    <div class="row justify-center text-center q-gutter-md">
      <q-card
        v-for="template in templates"
        :key="template.id"
        class="template-card"
      >
        <q-img
          class="template-img"
          spinner-color="primary"
          :src="`data:image/png;base64,${template.image}`"
        />
        <q-card-section>
          <div class="text-h6">{{ template.name }}</div>
          <div class="row items-center justify-center q-mb-sm">
            <q-icon name="mdi-source-repository" />
            <p class="q-ma-none">
              {{
                templateRepos.find(
                  (repo) => repo.id === template.template_repository_id,
                ).name
              }}
            </p>
            <q-tooltip :offset="[0, 0]">Template Repository</q-tooltip>
          </div>
          <p class="ellipsis-3-lines">
            {{ template.description }}
          </p>
        </q-card-section>
        <q-card-actions>
          <div class="absolute-bottom-right">
            <q-btn
              unelevated
              label="Info"
              icon="mdi-information-outline"
              @click="templateInfo(template.id)"
            />
            <q-btn
              unelevated
              label="Install"
              :icon="installIcon"
              @click="templateInstall(template.id)"
            />
          </div>
        </q-card-actions>
      </q-card>
    </div>
    <q-dialog v-model="templateInfoDialog">
      <q-card>
        <q-card-section class="row">
          <q-img
            :src="`data:image/png;base64,${templateInfoDialogData.image}`"
            spinner-color="primary"
            class="dialog-img q-mr-md"
          />
          <div class="col q-ml-md">
            <div class="text-h6">{{ templateInfoDialogData.name }}</div>
            <div class="text-subtitle2">
              Template Repository:
              {{
                templateRepos.find(
                  (repo) =>
                    repo.id === templateInfoDialogData.template_repository_id,
                ).name
              }}
            </div>
            <div class="text-subtitle2">
              Maintainer: {{ templateInfoDialogData.maintainer }}
            </div>
            <q-separator spaced="sm" inset color="transparent" />
            <div class="row q-gutter-md">
              <q-btn
                v-if="templateInfoDialogData.url['docker-hub']"
                color="primary"
                icon="mdi-docker"
                label="Docker Hub"
                :href="templateInfoDialogData.url['docker-hub']"
                target="_blank"
              />
              <q-btn
                v-if="templateInfoDialogData.url['external']"
                color="primary"
                icon="mdi-open-in-new"
                label="Project Page"
                :href="templateInfoDialogData.url['external']"
                target="_blank"
              />
              <q-btn
                color="primary"
                :icon="installIcon"
                label="Install"
                @click="templateInstall(templateInfoDialogData.id)"
              />
            </div>
          </div>
        </q-card-section>
        <q-card-section>
          {{ templateInfoDialogData.description }}
        </q-card-section>
      </q-card>
    </q-dialog>
    <q-inner-loading :showing="templateLoading" />
    <container-template-install ref="templateInstallDialog" />
    <error-dialog ref="errorDialog" />
  </q-page>
</template>

<style>
.template-card {
  width: 350px;
  height: 400px;
}
.template-img {
  max-width: 200px;
  max-height: 200px;
  margin-top: 5px;
}

.dialog-img {
  max-width: 100px;
  max-height: 100px;
}
</style>

<script>
import { ref } from "vue";
import ContainerTemplateInstall from "src/components/ContainerTemplateInstall.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      templates: [],
      templateDrawer: true,
      templateInfoDialog: false,
      templateInfoDialogData: {},
      templateLoading: true,
      installIcon: "mdi-monitor-arrow-down",
      templateRepos: [],
      templateRepoSelected: ref(null),
    };
  },
  components: {
    ContainerTemplateInstall,
    ErrorDialog,
  },
  methods: {
    templatesFetch() {
      this.templateLoading = true;
      let templateRepoIds = [];
      for (let i = 0; i < this.templateRepoSelected.length; i++) {
        templateRepoIds.push(this.templateRepoSelected[i].id);
      }
      this.$api
        .get("docker-manager/templates")
        .then((response) => {
          // Filter the templates based on the selected template repositories
          this.templates = response.data.filter((template) =>
            templateRepoIds.includes(template.template_repository_id),
          );
          this.templateLoading = false;
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error fetching templates", [errormsg]);
        });
    },
    templateLocationsFetch() {
      this.templateLoading = true;
      this.$api
        .get("docker-manager/template-locations")
        .then((response) => {
          this.templateRepos = response.data;
          this.templateRepoSelected = [this.templateRepos[0]];
          this.templatesFetch();
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error fetching template locations", [
            errormsg,
          ]);
        });
    },
    templateInfo(templateId) {
      // Get the template details from 'templates' and display them in a dialog
      let template = this.templates.find(
        (template) => template.id === templateId,
      );
      this.templateInfoDialogData = template;
      this.templateInfoDialog = true;
    },
    templateInstall(templateId) {
      this.templateInfoDialog = false;
      this.$refs.templateInstallDialog.showDialog(templateId, "new");
    },
  },
  mounted() {
    // Check if "/mnt/sharedfolders/docker_data" exists using system/file-manager/validate-path
    // if not, the user will be prompted to create it
    this.$api.post("system/file-manager/validate-path", {
      path: "/mnt/sharedfolders/docker_data",
    })
    .then((response) => {
      this.templateLocationsFetch();
    })
    .catch((error) => {
      this.$refs.errorDialog.show("Shared folder docker_data not found", ["Please create the shared folder docker_data before installing templates."]);
      this.templateLoading = false;
    });
  },
};
</script>
