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
            v-model="ipv4_dns_string"
            label="IPv4 DNS (comma separated)"
            filled
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
            filled
            v-if="networkInterface.ipv4_method == 'manual'"
          />
          <q-input
            v-model="networkInterface.ipv4_prefix"
            label="IPv4 prefix"
            filled
            v-if="networkInterface.ipv4_method == 'manual'"
          />
          <q-input
            v-model="networkInterface.ipv4_gateway"
            label="IPv4 gateway"
            filled
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
import { useApi } from 'src/composables/useApi'

export default {
  data() {
    return {
      hostName: '',
      networkInterface: null,
      layout: ref(false),
      ipv4_methods: ['manual', 'auto'],
      ipv4_dns_string: '',
    }
  },
  components: {
    errorDialog,
  },
  emits: ['ethernet-edit-finished'],
  methods: {
    show(networkInterface) {
      this.networkInterface = JSON.parse(JSON.stringify(networkInterface))
      // Convert ipv4_dns array to comma-separated string
      if (Array.isArray(this.networkInterface.ipv4_dns)) {
        this.ipv4_dns_string = this.networkInterface.ipv4_dns.join(',')
      } else if (this.networkInterface.ipv4_dns) {
        this.ipv4_dns_string = this.networkInterface.ipv4_dns
      } else {
        this.ipv4_dns_string = ''
      }
      // Convert ipv4_prefix to string if it exists
      if (this.networkInterface.ipv4_prefix !== null && this.networkInterface.ipv4_prefix !== undefined) {
        this.networkInterface.ipv4_prefix = String(this.networkInterface.ipv4_prefix)
      }
      this.layout = true
    },
    async updateNetwork() {
      if (this.networkInterface.ipv4_method === 'auto') {
        this.networkInterface.ipv4_address = null
        this.networkInterface.ipv4_prefix = null
        this.networkInterface.ipv4_gateway = null
      }
      // Convert ipv4_prefix from string to number
      if (this.networkInterface.ipv4_prefix !== null && this.networkInterface.ipv4_prefix !== undefined && this.networkInterface.ipv4_prefix !== '') {
        this.networkInterface.ipv4_prefix = parseInt(this.networkInterface.ipv4_prefix)
      }
      // Convert comma-separated DNS string to array and verify
      if (this.ipv4_dns_string && this.ipv4_dns_string.trim()) {
        const dns_list = this.ipv4_dns_string.split(',')
        const validated_dns = []
        for (let i = 0; i < dns_list.length; i++) {
          const dns = dns_list[i].trim()
          if (dns) {
            const ip_regex = /^(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$/
            if (!ip_regex.test(dns)) {
              this.$refs.errorDialog.show(`Invalid DNS IP address: ${dns}`)
              return
            }
            validated_dns.push(dns)
          }
        }
        this.networkInterface.ipv4_dns = validated_dns
      } else {
        this.networkInterface.ipv4_dns = null
      }

      const api = useApi()

      try {
        await api.networks.updateEthernet(this.networkInterface)
        this.layout = false
        this.$emit('ethernet-edit-finished')
      } catch (error) {
        this.$refs.errorDialog.show(error?.detail || error.message)
      }
    },
  },
  mounted() {},
}
</script>
