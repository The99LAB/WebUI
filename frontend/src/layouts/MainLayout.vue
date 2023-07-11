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
        >
          <ToolTip content="Toggle" />
        </q-btn>
        <q-toolbar-title>
          {{ hostname }}
        </q-toolbar-title>
        <q-btn
          dense
          flat
          round
          icon="notifications"
          @click="rightDrawerOpen = !rightDrawerOpen"
        >
          <q-badge
            floating
            color="red"
            rounded
            :label="notificationCount"
            v-if="notificationCount != 0"
          />
          <ToolTip content="Notifications" />
        </q-btn>
        <q-btn dense flat round icon="mdi-power">
          <ToolTip content="Power" />
          <q-menu>
            <q-list style="min-width: 10em">
              <q-item clickable>
                <q-item-section>
                  <q-btn
                    flat
                    round
                    dense
                    icon="mdi-power"
                    label="Shutdown"
                    @click="shutdown()"
                    class="disable-focus-helper"
                  />
                </q-item-section>
              </q-item>
              <q-separator />
              <q-item clickable>
                <q-item-section>
                  <q-btn
                    flat
                    round
                    dense
                    icon="mdi-refresh"
                    label="Reboot"
                    @click="reboot()"
                    class="disable-focus-helper"
                  />
                </q-item-section>
              </q-item>
            </q-list>
          </q-menu>
        </q-btn>
        <q-btn
          dense
          flat
          round
          :icon="
            $q.dark.isActive ? 'mdi-lightbulb' : 'mdi-moon-waning-crescent'
          "
          @click="this.$q.dark.toggle()"
        >
          <ToolTip
            :content="
              $q.dark.isActive ? 'Enable light mode' : 'Enable dark mode'
            "
          />
        </q-btn>
        <q-btn dense flat round icon="logout" @click="logout()">
          <ToolTip content="Logout" />
        </q-btn>
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

    <q-drawer v-model="rightDrawerOpen" side="right" overlay bordered>
      <q-list>
        <q-item-label header>
          <div class="row">
            Notifications
            <q-space />
            {{ notificationCount }}
          </div>
        </q-item-label>
        <q-item v-for="n in notifications" :key="n.id" clickable>
          <q-item-section avatar>
            <q-icon
              :name="
                n.type == 'error'
                  ? 'mdi-alert-circle'
                  : n.type == 'warning'
                  ? 'mdi-alert-circle'
                  : n.type == 'success'
                  ? 'mdi-check-circle'
                  : n.type == 'info'
                  ? 'mdi-information'
                  : 'mdi-help'
              "
              :color="
                n.type == 'error'
                  ? 'red'
                  : n.type == 'warning'
                  ? 'orange'
                  : n.type == 'success'
                  ? 'green'
                  : 'white'
              "
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ n.title }}</q-item-label>
            <q-item-label caption>{{ n.message }}</q-item-label>
            <q-item-label caption class="row"
              ><q-btn
                @click="NotificationDelete(n.id)"
                flat
                text-color="primary"
                size="sm"
                padding="none"
                label="Dismiss"
              ></q-btn>
              <q-space />{{ n.timestamp }}</q-item-label
            >
          </q-item-section>
        </q-item>
        <div class="row justify-center" v-if="notificationCount != 0">
          <q-btn
            @click="NotificationDelete(-1)"
            flat
            text-color="primary"
            size="sm"
            label="Dismiss All"
          ></q-btn>
        </div>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
      <PowerMenu ref="powerMenu" />
      <ErrorDialog ref="errorDialog" />
      <WsReconnectDialog
        ref="wsReconnectDialog"
        @ws-reconnect="connectNotificationsWebsocket"
      />
    </q-page-container>
  </q-layout>
</template>

<script>
import { defineComponent, ref } from "vue";
import PowerMenu from "src/components/PowerMenu.vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import WsReconnectDialog from "src/components/WsReconnectDialog.vue";
import ToolTip from "src/components/ToolTip.vue";
import { useHostnameStore } from "stores/hostname";
import { storeToRefs } from "pinia";

export default defineComponent({
  name: "MainLayout",
  data() {
    return {
      leftDrawerOpen: ref(false),
      rightDrawerOpen: ref(false),
      notificationCount: 0,
      notifications: [],
    };
  },
  setup() {
    const store = useHostnameStore();
    const { getHostname } = storeToRefs(store);
    return {
      hostname: getHostname,
    };
  },

  components: {
    PowerMenu,
    ErrorDialog,
    WsReconnectDialog,
    ToolTip,
  },
  methods: {
    showPowerMenu() {
      this.$refs.powerMenu.show();
    },
    logout() {
      localStorage.setItem("jwt-token", "");
      this.$router.push({ path: "/login" });
    },
    NotificationDelete(id) {
      if (id == -1) {
        this.notifications = [];
        this.notificationCount = 0;
      } else {
        this.notifications = this.notifications.filter((n) => n.id != id);
        this.notificationCount = this.notifications.length;
      }

      this.$api.delete("notifications/" + id).catch((error) => {
        this.$refs.errorDialog.show("Error deleting notification", [
          "Could not delete notification.",
          error.response.data.detail,
        ]);
      });
    },
    connectNotificationsWebsocket() {
      const jwt_token = localStorage.getItem("jwt-token");
      this.ws = new WebSocket(
        this.$WS_ENDPOINT + "/notifications?token=" + jwt_token,
      );

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type == "notifications") {
          this.notifications = data.data;
          this.notificationCount = this.notifications.length;
        } else if (data.type == "auth_error") {
          localStorage.setItem("jwt-token", "");
          this.$router.push({ path: "/login" });
        }
      };

      this.ws.onclose = (event) => {
        this.$refs.wsReconnectDialog.show();
      };
    },
    shutdown() {
      this.$api.post("host/power/shutdown").catch((error) => {
        let errormsg = "";
        if (error.response == undefined) {
          error = "Could not connect to server.";
        } else {
          error = error.response.data.detail;
        }
        this.$refs.errorDialog.show("Shutdown error", [errormsg]);
      });
    },
    reboot() {
      this.$api.post("host/power/reboot").catch((error) => {
        let errormsg = "";
        if (error.response == undefined) {
          error = "Could not connect to server.";
        } else {
          error = error.response.data.detail;
        }
        this.$refs.errorDialog.show("Reboot error", [errormsg]);
      });
    },
  },
  created() {
    this.connectNotificationsWebsocket();
  },
  unmounted() {
    this.ws.onclose = () => {};
    this.ws.close();
  },
});
</script>
<style lang="scss">
.disable-focus-helper {
  .q-focus-helper {
    opacity: 0 !important;
  }
}
</style>
