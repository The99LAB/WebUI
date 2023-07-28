<template>
  <q-dialog v-model="layout" maximized>
    <q-layout
      view="hHh lpR fFf"
      container
      :class="{ 'bg-dark': $q.dark.isActive, 'bg-white': !$q.dark.isActive }"
    >
      <q-header bordered>
        <q-toolbar>
          <q-toolbar-title>Edit Container</q-toolbar-title>
          <q-btn
            icon="close"
            flat
            round
            dense
            v-close-popup
            @click="tab = 'general'"
          />
        </q-toolbar>
        <q-tabs allign="left" v-model="tab">
          <q-tab name="general" label="General" />
          <q-tab name="volumes" label="Volumes" />
          <q-tab name="network" label="Network" />
          <q-tab name="environment" label="Environment" />
        </q-tabs>
        <q-separator color="transparent" />
      </q-header>
      <q-page-container>
        <q-page padding>
          <q-tab-panels v-model="tab">
            <q-tab-panel name="general">
              <q-input label="Name" v-model="containerName" />
              <q-input label="Id" v-model="containerId" disable />
              <q-input label="Image" v-model="containerImage" />
              <q-btn
                color="primary"
                icon="check"
                label="Change image"
                @click="applyImage"
              />
            </q-tab-panel>
            <q-tab-panel name="volumes">
              <q-table
                title="Volumes"
                :rows="containerMounts"
                :columns="containerVolumesColumns"
                row-key="Destination"
                hide-pagination
              >
                <template #body="props">
                  <q-tr :props="props">
                    <q-td key="Destination" :props="props">
                      {{ props.row.Destination }}
                      <q-popup-edit
                        v-model="props.row.Destination"
                        v-slot="scope"
                      >
                        <q-input
                          v-model="props.row.Destination"
                          dense
                          autofocus
                          @keyup.enter="scope.set"
                        />
                      </q-popup-edit>
                    </q-td>
                    <q-td key="Type" :props="props">
                      {{ props.row.Type }}
                      <q-popup-edit v-model="props.row.Type">
                        <q-select
                          v-model="props.row.Type"
                          :options="['bind', 'volume']"
                          label="Type"
                          borderless
                          rounded
                        />
                      </q-popup-edit>
                    </q-td>
                    <q-td key="Source" :props="props">
                      {{ props.row.Source }}
                      <q-popup-edit v-model="props.row.Source" v-slot="scope">
                        <q-input
                          v-model="props.row.Source"
                          dense
                          autofocus
                          @keyup.enter="scope.set"
                        />
                      </q-popup-edit>
                    </q-td>
                    <q-td key="RW" :props="props">
                      {{ props.row.RW }}
                      <q-popup-edit v-model="props.row.RW">
                        <q-toggle v-model="props.row.RW" />
                      </q-popup-edit>
                    </q-td>
                  </q-tr>
                </template>
              </q-table>
            </q-tab-panel>
          </q-tab-panels>
        </q-page>
        <q-footer reveal bordered>
          <q-toolbar>
            <q-space />
            <q-btn
              flat
              label="Apply"
              @click="applyEdits()"
              v-if="tab == 'general' || tab == 'volumes'"
            />
          </q-toolbar>
        </q-footer>
      </q-page-container>
    </q-layout>
  </q-dialog>
  <ErrorDialog ref="errorDialog" />
  <ConfirmDialog ref="confirmDialog" />
</template>

<script>
import { ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import ConfirmDialog from "src/components/ConfirmDialog.vue";

export default {
  data() {
    return {
      containerId: null,
      containerName: null,
      containerImage: null,
      containerMounts: null,
      layout: ref(false),
      tab: ref("general"),
      general_name: null,
      containerVolumesColumns: [
        {
          label: "Destination",
          field: "Destination",
          name: "Destination",
          align: "left",
        },
        { label: "Type", field: "Type", name: "Type", align: "left" },
        { label: "Source", field: "Source", name: "Source", align: "left" },
        { label: "Writable", field: "RW", name: "RW", align: "left" },
      ],
    };
  },
  components: {
    ErrorDialog,
    ConfirmDialog,
  },
  methods: {
    show(id) {
      this.containerId = id;
      console.log("this.containerId", this.containerId);
      this.refreshData();
      this.layout = true;
    },
    refreshData() {
      console.log("containerId", this.containerId);

      this.$api
        .get("docker-manager/container/" + this.containerId)
        .then((response) => {
          console.log("container response", response.data);
          this.containerName = response.data.name;
          this.containerImage = response.data.image;
          this.containerMounts = response.data.mounts;
        })
        .catch((error) => {
          console.log("error container", error);
        });
    },
    applyImage() {
      let value = "plexinc/pms-docker:1.32.5.7328-2632c9d3a";
      console.log(
        "Updating container with id",
        this.containerId,
        "with image",
        value,
      );
      this.$api
        .post("docker-manager/container/" + this.containerId + "/image", {
          image: value,
        })
        .then((response) => {
          console.log("response", response.data);
          this.refreshData();
        })
        .catch((error) => {
          console.log("error", error);
        });
    },
    applyEdits() {
      if (this.tab == "volumes") {
        console.log("containerMounts", this.containerMounts);
        this.$api
          .post(
            "docker-manager/container/" + this.containerId + "/volumes",
            this.containerMounts,
          )
          .then((response) => {
            console.log("response", response.data);
            this.refreshData();
          })
          .catch((error) => {
            console.log("error", error);
          });
      }
    },
    containerVolumeUpdate(type, value) {
      console.log(
        "Updating container with id",
        this.containerId,
        "with",
        type,
        "to",
        value,
      );
    },
  },
};
</script>
