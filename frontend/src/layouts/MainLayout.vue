<template>
  <q-layout view="hHh LpR fFf">
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />

        <q-toolbar-title>
          <q-avatar>
            <img src="https://cdn.quasar.dev/logo-v2/svg/logo-mono-white.svg">
          </q-avatar>
          Title
        </q-toolbar-title>
      </q-toolbar>
    </q-header>

    <q-drawer show-if-above v-model="leftDrawerOpen" side="left" bordered>
      <q-list>
        <!-- <q-item-label header>
          Essential Links
        </q-item-label> -->

        <q-item clickable tag="a" to="/dashboard">
          <q-item-section avatar>
            <q-icon name="mdi-monitor-dashboard" />
          </q-item-section>

          <q-item-section>
            <q-item-label>Dashboard</q-item-label>
            <!-- <q-item-label caption>Caption</q-item-label> -->
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/vm-manager">
          <q-item-section avatar>
            <q-icon name="mdi-cube" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Vm Manager</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue'

export default defineComponent({
  name: 'MainLayout',

  components: {
  },

  setup() {
    const leftDrawerOpen = ref(false)

    return {
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value
      }
    }
  }
})
</script>
