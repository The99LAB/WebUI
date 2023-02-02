<template>
    <q-select label="Storage pool" v-model="selectedStoragePool" :options="storagePoolList" option-label="name">
        <template v-slot:option="scope">
          <q-item v-bind="scope.itemProps">
            <q-item-section>
              <q-item-label>{{ scope.opt.name }}</q-item-label>
              <q-item-label caption>{{ scope.opt.allocation }} / {{ scope.opt.capacity }}</q-item-label>
            </q-item-section>
          </q-item>
        </template>
    </q-select>
</template>

<script>
export default {
    data() {
        return {
            storagePoolList: [],
            selectedStoragePool: "default",
        }
    },
    methods: {
        updatePoolList() {
            this.$api.get("/storage-pools")
                .then(response => {
                    this.storagePoolList = response.data
                    this.selectedStoragePool = this.storagePoolList[0]
                })
                .catch(error => {
                })
        },
        getSelectedPool() {
            return this.selectedStoragePool["uuid"]
        }
    },
    mounted() {
        this.updatePoolList()
    }
}
</script>