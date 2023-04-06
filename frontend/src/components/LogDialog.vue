<template>
  <q-dialog v-model="alert">
    <q-layout
      view="hHh lpR fFf"
      container
      :class="{ 'bg-dark': $q.dark.isActive, 'bg-white': !$q.dark.isActive }"
    >
      <q-header bordered>
        <q-toolbar>
          <q-toolbar-title>{{ title }}</q-toolbar-title>
          <q-space />
          <q-btn icon="close" flat round dense v-close-popup />
        </q-toolbar>
      </q-header>
      <q-separator color="transparent" spaced />
      <q-page-container>
        <q-page padding>
          <p v-for="item in content" :key="item">
            {{ item }}
          </p>
        </q-page>
      </q-page-container>
    </q-layout>
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
  methods: {
    // Usage: show("Title", ["Content line 1", "Contnent line 2"])
    show(title, content) {
      this.title = title;
      this.content = content;
      this.alert = true;
    },
    hide() {
      this.alert = false;
    },
  },
};
</script>
