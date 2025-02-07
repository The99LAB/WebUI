<template>
  <q-dialog v-model="layout">
    <q-card style="min-width: 30vw">
      <q-card-section>
        <div class="row">
          <div class="text-h6">Edit {{ networkInterface.name }}</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        <q-form>
          <div class="row">
            <div class="col">
              <q-select
                v-model="networkInterface.ipv4_method"
                :options="ipv4_methods"
                label="IPv4 Method"
                filled
              />
              <q-input
                v-model="networkInterface.ipv4_address"
                label="IPv4 address"
                v-if="networkInterface.ipv4_method == 'manual'"
              />
              <q-input
                v-model="networkInterface.ipv4_prefix"
                label="IPv4 prefix"
                v-if="networkInterface.ipv4_method == 'manual'"
              />
              <q-input
                v-model="networkInterface.ipv4_gateway"
                label="IPv4 gateway"
                v-if="networkInterface.ipv4_method == 'manual'"
              />
            </div>
          </div>
        </q-form>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Finish" @click="updateNetwork" />
      </q-card-actions>
    </q-card>
  </q-dialog>
  <errorDialog ref="errorDialog" />
</template>

<script>
import { ref } from 'vue'
import errorDialog from 'src/components/ErrorDialog.vue'

export default {
  data() {
    return {
      hostName: '',
      networkInterface: null,
      layout: ref(false),
      ipv4_methods: ['manual', 'auto'],
    }
  },
  components: {
    errorDialog,
  },
  emits: ['network-edit-finished'],
  methods: {
    show(networkInterface) {
      this.networkInterface = JSON.parse(JSON.stringify(networkInterface))
      this.layout = true
    },
    updateNetwork() {
      // $api send an update request to the backend with the new networkInterface data
      // the data is json
      // /api/networks/

      this.$api
        .put(`/system/networks/`, this.networkInterface)
        .then(() => {
          this.layout = false
          this.$emit('network-edit-finished')
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error)
        })
    },
  },
  mounted() {},
}
</script>
