<template>
    <q-page padding>
        <q-card>
            <q-card-section>
                <div class="text-h6">Download ISO</div>
            </q-card-section>
            <q-separator dark inset />
            <q-card-section>
                <q-input v-model="url" label="URL" />
            </q-card-section>
            <q-card-section>
                <q-input v-model="fileName" label="File Name" />
            </q-card-section>
            <q-card-section>
                <StoragePoolList ref="storagePool"/>
            </q-card-section>
            <q-card-section>
                <q-btn color="primary" label="Download" @click="downloadIso()"/>
            </q-card-section>
            <q-card-section>
                <q-linear-progress rounded v-show="showProgressBar" :value="progress" class="q-mt-md" animation-speed="100" size="25px">
                    <div class="absolute-full flex flex-center">
                        <q-badge color="transparent" text-color="primary" :label="(progress * 100).toFixed(0) + '%'" />
                    </div>
                </q-linear-progress>
            </q-card-section>
        </q-card>
        <ErrorDialog ref="errorDialog" />
    </q-page>
</template>

<script>
import StoragePoolList from 'src/components/StoragePoolList.vue'
import ErrorDialog from 'src/components/ErrorDialog.vue'
import { ref } from 'vue'

export default {
    data() {
      return {
        url: "https://geo.mirror.pkgbuild.com/iso/2023.02.01/archlinux-x86_64.iso",
        fileName: "archlinux-x86_64.iso",
        showProgressBar: false,
        progress: 0,
      }
    },
    components: {
        StoragePoolList,
        ErrorDialog,
    },
    methods: {
        downloadIso(){
            this.$socket.emit("download_iso", { url: this.url, fileName: this.fileName, storagePool: this.$refs.storagePool.getSelectedPool() })
        },
    },
    mounted() {
        console.log("DownloadIsoPage mounted")
        this.$socket.on("downloadIsoError", (msg) => {
                this.$refs.errorDialog.show("Error Downloading ISO", ["Error: " + msg])
            })
        this.$socket.on("downloadIsoProgress", (msg) => {
            this.showProgressBar = true
            this.progress = msg/100
        })
        this.$socket.on("downloadIsoComplete", (msg) => {
            this.showProgressBar = false
            this.progress = 0
            this.$refs.errorDialog.show("ISO Download Complete", msg)
        })
    },
    unmounted() {
        console.log("DownloadIsoPage unmounted")
        this.$socket.off("downloadIsoError")
        this.$socket.off("downloadIsoProgress")
        this.$socket.off("downloadIsoComplete")
    },
  }
</script>