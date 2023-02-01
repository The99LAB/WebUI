<template>
    <q-select label="Storage pool" v-model="selectedStoragePool" :options="storagePoolList" />

</template>

<script>
import { ref } from 'vue'
selectedStoragePool = ref(null)
storagePoolList = ref(["default", "default2"])

export default {
    data() {
        return {
        }
    },
    components: {

    },
    methods: {
        updatePoolList() {
            console.log("Updating pool list")

            this.$api.post("/storage-pools", formData)
                .then(
            )
                .catch(error => {
                })
        },
        getSelectedPool() {
            return this.selectedStoragePool
        }
    }
}
</script>