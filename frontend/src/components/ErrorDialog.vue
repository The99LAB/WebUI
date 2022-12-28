<template>
    <q-dialog v-model="alert">
      <q-card>
        <q-card-section>
          <div class="text-h6">{{title}}</div>
        </q-card-section>

        <q-card-section class="q-pt-none" v-for="item in content" :key="item">
            {{item}}
        </q-card-section>

        <q-card-actions allign="right">
          <q-btn flat label="OK" color="primary" v-close-popup />
        </q-card-actions>
      </q-card>
    </q-dialog>
</template>

<script>
import { ref } from 'vue'

export default {
    data() {
        return {
            alert: ref(false)
        }
    },
    methods : {
        // Usage: showAlert("Title", ["Content line 1", "Contnent line 2"])
        showAlert(title, content) {
            this.title = title
            this.content = content
            this.alert = true
        }
    }
}
</script>