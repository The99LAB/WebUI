<template>
    <q-select label="Network" v-model="selectedNetwork" :options="networkList" option-label="name">
        <template v-slot:option="scope">
          <q-item v-bind="scope.itemProps">
            <q-item-section>
              <q-item-label>{{ scope.opt.name }}</q-item-label>
              <q-item-label caption>Active: {{ scope.opt.active }}</q-item-label>
            </q-item-section>
          </q-item>
        </template>
    </q-select>
</template>

<script>
export default {
    data() {
        return {
            networkList: [],
            selectedNetwork: "default",
        }
    },
    methods: {
        updateNetworkList() {
            console.log("Updating network list")
            this.$api.get("/networks")
                .then(response => {
                    this.networkList = response.data
                    console.log("Network list: ", response.data)
                    this.selectedNetwork = this.networkList[0]
                })
                .catch(error => {
                })
        },
        getSelectedNetwork() {
            return this.selectedNetwork["uuid"]
        }
    },
    mounted() {
        this.updateNetworkList()
    }
}
</script>