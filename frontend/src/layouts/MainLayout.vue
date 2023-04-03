<template>
  <q-layout view="hHh LpR fFf">
    <q-header class="bg-primary">
      <q-toolbar>
        <q-btn
          dense
          flat
          round
          icon="menu"
          @click="leftDrawerOpen = !leftDrawerOpen"
        />
        <q-toolbar-title>
          {{ hostname }}
        </q-toolbar-title>
        <q-btn
          dense
          flat
          round
          icon="power_settings_new"
          @click="showPowerMenu()"
        />
        <q-btn
          dense
          flat
          round
          :icon="
            $q.dark.isActive ? 'mdi-lightbulb' : 'mdi-moon-waning-crescent'
          "
          @click="this.$q.dark.toggle()"
        />
        <q-btn dense flat round icon="logout" @click="logout()" />
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
        <q-item-label header> Virtual Machines </q-item-label>
        <q-item clickable tag="a" to="/vm-manager">
          <q-item-section avatar>
            <q-icon name="mdi-cube" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Vm Manager</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/hotplug-usb">
          <q-item-section avatar>
            <q-icon name="mdi-usb" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Hotplug USB</q-item-label>
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
        <q-item clickable tag="a" to="/backup-manager">
          <q-item-section avatar>
            <q-icon name="mdi-backup-restore" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Backup Manager</q-item-label>
          </q-item-section>
        </q-item>
        <q-item-label header> Host Management </q-item-label>
        <q-expansion-item
          :content-inset-level="0.2"
          expand-separator
          icon="mdi-tools"
          label="Tools"
        >
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
          <q-item clickable tag="a" to="/tools/download-iso">
            <q-item-section avatar>
              <q-icon name="mdi-disc" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Download ISO</q-item-label>
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
          <q-item clickable tag="a" to="/tools/terminal">
            <q-item-section avatar>
              <q-icon name="mdi-console" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Terminal</q-item-label>
            </q-item-section>
          </q-item>
        </q-expansion-item>
        <q-item clickable tag="a" to="/settings">
          <q-item-section avatar>
            <q-icon name="mdi-cog" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Settings</q-item-label>
          </q-item-section>
        </q-item>
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
import { defineComponent, ref } from "vue";
import PowerMenu from "src/components/PowerMenu.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import { useMeta } from 'quasar'

export default defineComponent({
  name: "MainLayout",
  data() {
    return {
      leftDrawerOpen: ref(false),
      hostname: "",
    };
  },
  setup() {
    const title = ref("");
    const updateTitle = (newTitle) => {
      title.value = newTitle;
    };
    useMeta(() => {
      return {
        title: title.value,
      };
    });
    return {
      title,
      updateTitle,
    };
  },

  components: {
    PowerMenu,
    ErrorDialog,
  },
  methods: {
    generateTitle() {
      this.updateTitle(this.hostname + " - " + this.$route.meta.title)
    },
    showPowerMenu() {
      this.$refs.powerMenu.show();
    },
    getHostName() {
      this.$api
        .get("/host/system-info/hostname")
        .then((response) => {
          this.hostname = response.data.hostname;
          this.generateTitle();
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting hostname", [
            "Could not get hostname.",
            error.response.data,
          ]);
        });
    },
    logout() {
      localStorage.setItem("jwt-token", "");
      this.$router.push({ path: "/login" });
    },
  },
  created() {
    this.getHostName();
    this.$router.afterEach((to, from) => {
      this.generateTitle();
    });
  },
});
</script>
