<template>
  <q-page>
    <div class="row">
      <div class="col-5 col-md">
        <div class="q-pa-md" align="center">
          <q-card class="cursor-pointer" @click="this.$router.push('/tools/system-info')">
            <q-card-section>
              <q-icon name="mdi-monitor" size="xl" />
            </q-card-section>
            <q-separator />
            <q-card-section class="text-subtitle2  text-center">
              System Information
            </q-card-section>
          </q-card>
        </div>
      </div>
      <div class="col-5 col-md">
        <div class="q-pa-md" align="center">
          <q-card class="cursor-pointer" @click="this.$router.push('/tools/system-devices')">
            <q-card-section>
              <q-icon name="mdi-harddisk" size="xl" />
            </q-card-section>
            <q-separator />
            <q-card-section class="text-subtitle2  text-center">
              System Devices
            </q-card-section>
          </q-card>
        </div>
      </div>
      <div class="col-5 col-md">
        <div class="q-pa-md" align="center">
          <q-card class="cursor-pointer" @click="this.$router.push('/tools/about')">
            <q-card-section>
              <q-icon name="mdi-information" size="xl" />
            </q-card-section>
            <q-separator />
            <q-card-section class="text-subtitle2  text-center">
              About
            </q-card-section>
          </q-card>
        </div>
      </div>
    </div>
  </q-page>
</template>

<script>
import { ref } from 'vue'

export default {
  data() {
    return {

    }
  },
  components: {
  },
  methods: {
  },
}
</script>
