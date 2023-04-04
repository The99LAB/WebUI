<template>
    <q-dialog v-model="alert">
      <q-card>
        <q-card-section class="row items-center q-pb-none">
          <div class="text-h6">WebSocket closed. Reconnect?</div>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-card-section>
        <q-separator color="transparent" spaced="lg" inset />
        <q-card-section class="q-pt-none q-px-xl">
            <q-btn label="Reconnect" @click="reconnect()" />
        </q-card-section>
        <q-card-actions align="right">
          <q-btn flat label="Finish" @click="addDisk()" />
        </q-card-actions>
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
  