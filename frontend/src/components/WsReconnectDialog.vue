<template>
    <q-dialog v-model="alert">
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">WebSocket closed</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="lg" inset />
        <q-card-section class="q-pt-none q-px-xl">
          <div class="row justify-center">
            <p>Do you want to reconnect?</p>
          </div>
          <div class="row justify-center">
            <q-btn
              flat
              class="q-ma-sm"
              color="primary"
              icon="mdi-refresh"
              label="Reconnect"
              @click="reconnect"
            />
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
</template>

<script>
import { ref } from "vue";

export default {
data() {
    return {
    alert: ref(false),
    };
},
emits: ["ws-reconnect"],
methods: {
    show() {
        this.alert = true;
    },
    reconnect() {
    this.$emit("ws-reconnect");
    this.alert = false;
    },
},
};
</script>
  