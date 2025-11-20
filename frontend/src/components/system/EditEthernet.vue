<template>
  <q-dialog v-model="layout">
    <q-card style="min-width: 30vw">
      <q-card-section>
        <div class="row">
          <div class="text-h6">Edit Ethernet Interface '{{ networkInterface.name }}'</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        <div class="q-gutter-y-sm">
          <q-input
            v-model="networkInterface.name"
            label="Interface Name"
            filled
            readonly
          />
          <q-input
            v-model="networkInterface.ipv4_dns"
            label="IPv4 DNS (comma separated)"
          />
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
  emits: ['ethernet-edit-finished'],
  methods: {
    show(networkInterface) {
      this.networkInterface = JSON.parse(JSON.stringify(networkInterface))
      this.layout = true
    },
    updateNetwork() {
      if (this.networkInterface.ipv4_method === 'auto') {
        this.networkInterface.ipv4_address = null
        this.networkInterface.ipv4_prefix = null
        this.networkInterface.ipv4_gateway = null
      }

      this.$api
        .put(`/system/networks/ethernets`, this.networkInterface)
        .then(() => {
          this.layout = false
          this.$emit('ethernet-edit-finished')
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error)
        })
    },
  },
  mounted() {},
}
</script>
