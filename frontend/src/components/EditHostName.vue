<template>
    <q-dialog v-model="layout">
        <q-card>
            <q-card-section>
                <div class="row">
                    <div class="text-h6">Edit Host Name</div>
                    <q-space />
                    <q-btn icon="close" flat round dense v-close-popup />
                </div>
            </q-card-section>
            <q-card-section class="q-pt-none">
                <q-form>
                    <div class="row">
                        <div class="col">
                            <q-input label="Name" v-model="hostName" />
                        </div>
                    </div>
                </q-form>
            </q-card-section>
            <q-card-actions align="right">
                <q-btn flat label="Finish" @click="editHostName()" />
            </q-card-actions>
        </q-card>
    </q-dialog>
</template>

<script>
import { ref } from 'vue'

export default {
    data() {
        return {
            hostName: "",
            layout: ref(false),
        }
    },
    emits: ["hostname-edit-finished"],
    components: {
    },
    methods: {
        show() {
            this.layout = true

        },
        getHostName() {
            this.$api.get("/host/system-info/hostname")
                .then(response => {
                    this.hostName = response.data.hostname
                })
                .catch(error => {
                    console.log("Error getting hostname: " + error.response.data)
                })
        },
        editHostName() {
            console.log("Editing Host Name...")
            const formData = new FormData()
            formData.append("hostname", this.volumeFormat)
            this.$api.post("/host/system-info/hostname", formData)
                .then(
                    this.layout = false,
                    this.$emit("hostname-edit-finished"),
                )
                .catch(error => {
                    console.log("Error editing hostname: " + error.response.data)
                })
        },
    },
    mounted() {
        // this.getHostName()
    }
}
</script>