<template>
  <q-dialog v-model="layout">
    <q-card style="min-width: 30vw">
      <q-card-section>
        <div class="row">
          <div class="text-h6">Edit Bridge Interface '{{ bridgeInterface.bridge_name }}'</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </div>
      </q-card-section>
      <q-card-section class="q-pt-none">
        <div class="q-gutter-y-sm">
          <q-input
            v-model="bridgeInterface.bridge_name"
            label="Bridge Name"
            filled
            readonly
          />
          <q-input
            v-model="bridgeInterface.interface_name"
            label="Interface Name"
            filled
            readonly
          />
          <q-select
            v-model="bridgeInterface.ipv4_method"
            :options="ipv4_methods"
            label="IPv4 Method"
            filled
          />
          <q-input
              v-model="bridgeInterface.ipv4_address"
              label="IPv4 address"
              v-if="bridgeInterface.ipv4_method == 'manual'"
            />
            <q-input
              v-model="bridgeInterface.ipv4_prefix"
              label="IPv4 prefix"
              v-if="bridgeInterface.ipv4_method == 'manual'"
            />
            <q-input
              v-model="bridgeInterface.ipv4_gateway"
              label="IPv4 gateway"
              v-if="bridgeInterface.ipv4_method == 'manual'"
            />
        </div>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Finish" @click="updateBridge" />
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
      bridgeInterface: null,
      layout: ref(false),
      ipv4_methods: ['manual', 'auto'],
    }
  },
  components: {
    errorDialog,
  },
  emits: ['bridge-edit-finished'],
  methods: {
    show(bridgeInterface) {
      this.bridgeInterface = JSON.parse(JSON.stringify(bridgeInterface))
      this.layout = true
    },
    updateBridge() {
      console.log(this.bridgeInterface)
      this.$api
        .put(`/system/networks/bridges`, this.bridgeInterface)
        .then(() => {
          this.layout = false
          this.$emit('bridge-edit-finished')
        })
        .catch((error) => {
          this.$refs.errorDialog.show(error)
        })
    },
  },
  mounted() {},
}
</script>
