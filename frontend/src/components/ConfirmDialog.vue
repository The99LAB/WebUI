<template>
  <q-dialog v-model="layout">
    <q-card>
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">{{ title }}</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section class="q-pt-none" v-for="item in content" :key="item">
        {{ item }}
      </q-card-section>
      <q-card-actions align="right">
        <q-btn flat label="Yes" @click="confirmYes" />
        <q-btn flat label="No" @click="confirmNo()" />
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<script>
import { ref } from "vue";

export default {
  data() {
    return {
      title: "",
      content: [],
      layout: ref(false),
      confirmAction: () => {},
      cancelAction: () => {},
    };
  },
  methods: {
    show(
      title = "Are you sure?",
      content = ["Are you sure you want to do this?"],
      confirmAction = () => {},
      cancelAction = () => {},
    ) {
      this.confirmAction = confirmAction;
      this.cancelAction = cancelAction;
      this.title = title;
      this.content = content;
      this.layout = true;
    },
    confirmYes() {
      this.confirmAction();
      this.layout = false;
    },
    confirmNo() {
      this.cancelAction();
      this.layout = false;
    },
  },
};
</script>
