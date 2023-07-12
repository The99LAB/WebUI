<template>
    <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page padding class="row justify-center items-center">
        <q-card>
          <q-card-section class="text-center">
            System is shutting down{{ dotsText }}
          </q-card-section>
          <q-card-section>
            <img
              class="q-px-md"
              src="/src/assets/Server99-logo-full.png"
              alt="Logo"
              style="width: 25em"
            />
          </q-card-section>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
</template>
<script>
import { ref } from 'vue'

export default {
    data() {
        return {
            dots: 0,
            dotsText: ref(''),
        }
    },
    mounted () {
        this.dots = setInterval(() => {
            if (this.dots < 3) {
                this.dots++
            } else {
                this.dots = 0
            }
            this.dotsText = '.'.repeat(this.dots)
        }, 500)
    },
}
</script>
