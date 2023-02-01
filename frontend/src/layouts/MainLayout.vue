<template>
  <q-layout view="hHh LpR fFf">
    <q-header class="bg-primary text-white">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="toggleLeftDrawer" />
        <q-toolbar-title>
          Server3
        </q-toolbar-title>
        <q-btn dense flat round icon="power_settings_new" @click="showPowerMenu()" />
        <q-btn dense flat round icon="logout" />
      </q-toolbar>
    </q-header>

    <q-drawer show-if-above v-model="leftDrawerOpen" side="left" bordered>
      <q-list>
        <q-item clickable tag="a" to="/dashboard">
          <q-item-section avatar>
            <q-icon name="mdi-monitor-dashboard" />
          </q-item-section>

          <q-item-section>
            <q-item-label>Dashboard</q-item-label>
          </q-item-section>
        </q-item>
        <q-item-label header>
          Virtual Machines
        </q-item-label>
        <q-item clickable tag="a" to="/vm-manager">
          <q-item-section avatar>
            <q-icon name="mdi-cube" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Vm Manager</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/storage-pools">
          <q-item-section avatar>
            <q-icon name="mdi-server" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Storage Pools</q-item-label>
          </q-item-section>
        </q-item>
        <q-item-label header>
          Host Management
        </q-item-label>
        <q-expansion-item :content-inset-level="0.2" expand-separator icon="mdi-tools" label="Tools" clickable tag="a"
          to="/tools">
          <q-item clickable tag="a" to="/tools/system-info">
            <q-item-section avatar>
              <q-icon name="mdi-monitor" />
            </q-item-section>
            <q-item-section>
              <q-item-label>System Information</q-item-label>
            </q-item-section>
          </q-item>
          <q-item clickable tag="a" to="/tools/system-devices">
            <q-item-section avatar>
              <q-icon name="mdi-harddisk" />
            </q-item-section>
            <q-item-section>
              <q-item-label>System Devices</q-item-label>
            </q-item-section>
          </q-item>
          <q-item clickable tag="a" to="/tools/about">
            <q-item-section avatar>
              <q-icon name="mdi-information" />
            </q-item-section>
            <q-item-section>
              <q-item-label>About</q-item-label>
            </q-item-section>
          </q-item>
        </q-expansion-item>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
      <PowerMenu ref="powerMenu" />
      <ErrorDialog ref="errorDialog" />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from 'vue'
import PowerMenu from 'src/components/PowerMenu.vue'
import ErrorDialog from 'src/components/ErrorDialog.vue'

export default defineComponent({
  name: 'MainLayout',

  components: {
    PowerMenu,
    ErrorDialog
  },

  methods: {
    showPowerMenu() {
      this.$refs.powerMenu.show()
    }
  },
  setup() {
    const leftDrawerOpen = ref(false)

    return {
      leftDrawerOpen,
      toggleLeftDrawer() {
        leftDrawerOpen.value = !leftDrawerOpen.value
      }
    }
  },
  mounted() {
    console.log("MainLayout mounted")
    this.$socket.on("connect_error", (msg) => {
      this.$refs.errorDialog.show("Connection Error", ["Could not connect to the backend server.", msg])
    })
  }
})
</script>
