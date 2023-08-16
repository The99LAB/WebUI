<template>
  <q-page padding>
    <q-table
      title="Images"
      :rows="dockerImages"
      :columns="dockerImagesColumns"
      row-key="uuid"
      :pagination="dockerImagesPagination"
      selection="multiple"
      v-model:selected="selectedImage"
      :loading="dockerImagesLoading"
      hide-selected-banner
    >
      <template v-slot:top-right>
          <q-btn
            color="primary"
            icon="mdi-delete"
            round
            flat
            @click="$refs.confirmDialog.show('Delete Image(s)', ['Are you sure you want to delete the selected image(s)?'], imageDelete)"
            :disable="selectedImage.length == 0"
          >
            <q-tooltip :offset="[5,5]">Delete Image</q-tooltip>
          </q-btn>
          <q-btn
            color="primary"
            icon="mdi-download"
            round
            flat
            @click="pullImageDialog = true"
          >
            <q-tooltip :offset="[5,5]">Pull Image</q-tooltip>
          </q-btn>
      </template>
    </q-table>
    <q-dialog v-model="pullImageDialog" persistent>
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">Pull Image</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-card-section>
          <q-form @submit="imagePull">
            <q-input
              v-model="pullImageName"
              label="Image name"
              autofocus
              hint="repository:tag"
              style="width: 25em"
              :rules="[val => !!val || 'Image name is required']"
            />
            <div class="row justify-end">
              <q-btn
                type="submit"
                label="Pull"
                flat
              />
            </div>
          </q-form>
        </q-card-section>
        <q-inner-loading :showing="pullImageLoading" />
      </q-card>
    </q-dialog>
    <errorDialog ref="errorDialog" />
    <ConfirmDialog ref="confirmDialog" />
  </q-page>
</template>

<script>
import { ref } from "vue";
import errorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";

export default {
  data() {
    return {
      dockerImagesColumns: [
        {
          label: "Repository",
          field: "repo",
          name: "repo",
          align: "left",
          sortable: true,
        },
        {
          label: "Tag",
          field: "tag",
          name: "tag",
          align: "left",
          sortable: true,
        },
        {
          label: "Image ID",
          field: "id",
          name: "id",
          align: "left",
          sortable: true,
        },
        {
          label: "Created",
          field: "created",
          name: "created",
          align: "left",
          sortable: true,
        },
        {
          label: "Size",
          field: "size",
          name: "size",
          align: "left",
          sortable: true,
        },
      ],
      dockerImages: [],
      dockerImagesPagination: {
        sortBy: "repository",
        rowsPerPage: 15,
      },
      selectedImage: ref([]),
      pullImageDialog: false,
      pullImageName: "",
      pullImageLoading: false,
      dockerImagesLoading: false,
    };
  },
  components: {
    errorDialog,
    ConfirmDialog,
  },
  methods: {
    getDockerImages() {
      this.dockerImagesLoading = true;
      this.$api
        .get("docker-manager/images")
        .then((response) => {
          this.dockerImages = response.data;
          this.dockerImagesLoading = false;
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error fetching docker images", [
            errormsg,
          ]);
        });
    },
    imageDelete() {
      // create a list of the images. Each item has an id and tag
      let images = [];
      for (let i = 0; i < this.selectedImage.length; i++) {
        images.push({
          name: this.selectedImage[i].repo,
          tag: this.selectedImage[i].tag,
        });
      }
      // clear the selected images
      this.selectedImage = [];
      this.$api
        .post("docker-manager/images/delete", { images: images })
        .then((response) => {
          this.getDockerImages();
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error deleting docker image", [
            errormsg,
          ]);
        });
    },
    imagePull() {
      this.pullImageLoading = true;
      this.$api
        .post("docker-manager/images/pull", { image: this.pullImageName })
        .then((response) => {
          this.getDockerImages();
          this.pullImageLoading = false;
          this.pullImageDialog = false;
        })
        .catch((error) => {
          let errormsg = error.response ? error.response.data.detail : error;
          this.$refs.errorDialog.show("Error pulling docker image", [errormsg]);
          this.pullImageLoading = false;
        });
    },
  },
  mounted() {
    this.getDockerImages();
  },
};
</script>
