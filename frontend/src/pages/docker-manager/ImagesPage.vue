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
        <div class="q-gutter-sm">
          <q-btn
            color="primary"
            icon="mdi-delete"
            label="Delete"
            @click="imageDelete()"
            :disable="selectedImage.length == 0"
          />
          <q-btn
          color="primary"
          icon="mdi-download"
          label="Pull Image"
          @click="pullImageDialog = true"
          />
        </div>
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
          <q-input v-model="pullImageName" label="Image name" autofocus hint="repository:tag" style="width: 25em;"/>
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Pull" @click="imagePull" />
        </q-card-actions>
        <q-inner-loading :showing="pullImageLoading" />
      </q-card>
    </q-dialog>
    <errorDialog ref="errorDialog" />
  </q-page>
</template>

<script>
import { ref } from "vue";
import errorDialog from "src/components/ErrorDialog.vue";

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
