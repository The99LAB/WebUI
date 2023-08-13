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
            :label="notifications.length"
            v-if="notifications.length != 0"
          />
          <ToolTip content="Notifications" />
        </q-btn>
        <q-btn dense flat round icon="mdi-power">
          <ToolTip content="Power" />
          <q-menu v-model="showPowerMenu">
            <q-list style="min-width: 10em">
              <q-item clickable>
                <q-item-section>
                  <q-btn
                    flat
                    round
                    dense
                    icon="mdi-power"
                    label="Shutdown"
                    @click="powerAction('shutdown')"
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
                    @click="powerAction('reboot')"
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
        <q-separator spaced="xs" color="transparent" />
        <q-item clickable tag="a" to="/dashboard">
          <q-item-section avatar>
            <q-icon name="bi-speedometer" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Dashboard</q-item-label>
          </q-item-section>
        </q-item>
        <q-item-label header class="q-pb-none q-pt-md"
          >Virtual Machines</q-item-label
        >
        <q-item clickable tag="a" to="/vm-manager/vms">
          <q-item-section avatar>
            <q-icon name="ion-cube" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Virtual Machines</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/vm-manager/hotplug-usb">
          <q-item-section avatar>
            <q-icon name="mdi-usb" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Hotplug USB</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/vm-manager/storage-pools">
          <q-item-section avatar>
            <q-icon name="mdi-server" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Storage Pools</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/vm-manager/backups">
          <q-item-section avatar>
            <q-icon name="mdi-backup-restore" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Backups</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/vm-manager/download-iso">
          <q-item-section avatar>
            <q-icon name="mdi-disc" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Download ISO</q-item-label>
          </q-item-section>
        </q-item>
        <q-item-label header class="q-pb-none q-pt-md">Docker</q-item-label>
        <q-item clickable tag="a" to="/docker-manager/containers">
          <q-item-section avatar>
            <q-icon name="bi-boxes" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Containers</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/docker-manager/images">
          <q-item-section avatar>
            <q-icon name="fa-solid fa-clone" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Images</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/docker-manager/networks">
          <q-item-section avatar>
            <q-icon name="mdi-lan" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Networks</q-item-label>
          </q-item-section>
        </q-item>
        <q-expansion-item
          expand-separator
          icon="bi-files"
          label="Templates"
          to="/docker-manager/templates"
          :content-inset-level="0.2"
        >
          <q-item clickable tag="a" to="/docker-manager/templates/settings">
            <q-item-section avatar>
              <q-icon name="mdi-cog" />
            </q-item-section>
            <q-item-section>
              <q-item-label>Settings</q-item-label>
            </q-item-section>
          </q-item>
        </q-expansion-item>
        <q-item-label header class="q-pb-none q-pt-md">Storage</q-item-label>
        <q-item clickable tag="a" to="/storage-manager/disks">
          <q-item-section avatar>
            <q-icon name="bi-hdd" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Disks</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/storage-manager/raid-manager">
          <q-item-section avatar>
            <q-icon name="mdi-database-outline" />
          </q-item-section>
          <q-item-section>
            <q-item-label>RAID Management</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/storage-manager/sharedfolders">
          <q-item-section avatar>
            <q-icon name="mdi-share-variant-outline" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Shared Folders</q-item-label>
          </q-item-section>
        </q-item>
        <q-item-label header class="q-pb-none q-pt-md">System</q-item-label>
        <q-item clickable tag="a" to="/system/system-info">
          <q-item-section avatar>
            <q-icon name="mdi-monitor" />
          </q-item-section>
          <q-item-section>
            <q-item-label>System Information</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/system/system-devices">
          <q-item-section avatar>
            <q-icon name="bi-gpu-card" />
          </q-item-section>
          <q-item-section>
            <q-item-label>System Devices</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/system/users">
          <q-item-section avatar>
            <q-icon name="mdi-account" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Users</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/system/terminal">
          <q-item-section avatar>
            <q-icon name="mdi-console" />
          </q-item-section>
          <q-item-section>
            <q-item-label>Terminal</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/system/filemanager">
          <q-item-section avatar>
            <q-icon name="mdi-folder-multiple-outline" />
          </q-item-section>
          <q-item-section>
            <q-item-label>File Manager</q-item-label>
          </q-item-section>
        </q-item>
        <q-item clickable tag="a" to="/system/settings">
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
            {{ notifications.length }}
          </div>
        </q-item-label>
        <q-item v-for="n in notifications" :key="n.id" clickable>
          <q-item-section avatar>
            <q-icon
              :name="notificationIcon[n.type]"
              :color="notificationColor[n.type]"
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
              />
              <q-space />{{ n.timestamp }}</q-item-label
            >
          </q-item-section>
        </q-item>
        <div class="row justify-center" v-if="notifications.length != 0">
          <q-btn
            @click="NotificationDelete(-1)"
            flat
            text-color="primary"
            size="sm"
            label="Dismiss All"
          />
        </div>
      </q-list>
    </q-drawer>

    <q-page-container>
      <router-view />
      <ErrorDialog ref="errorDialog" />
      <ConfirmDialog ref="confirmDialog" />
      <WsReconnectDialog
        ref="wsReconnectDialog"
        @ws-reconnect="connectNotificationsWebsocket"
      />
    </q-page-container>
  </q-layout>
</template>

<script>
import { Notify } from "quasar";
import { defineComponent, ref } from "vue";
import ErrorDialog from "src/components/ErrorDialog.vue";
import WsReconnectDialog from "src/components/WsReconnectDialog.vue";
import ToolTip from "src/components/ToolTip.vue";
import { useHostnameStore } from "stores/hostname";
import { storeToRefs } from "pinia";
import ConfirmDialog from "src/components/ConfirmDialog.vue";

export default defineComponent({
  name: "MainLayout",
  data() {
    return {
      leftDrawerOpen: ref(false),
      rightDrawerOpen: ref(false),
      notifications: [],
      showPowerMenu: ref(false),
      notificationIcon: {
        error: "mdi-alert-circle",
        warning: "mdi-alert-circle",
        success: "mdi-check-circle",
        info: "mdi-information",
      },
      notificationColor: {
        error: "red",
        warning: "orange",
        success: "green",
        info: "white",
      },
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
    ErrorDialog,
    WsReconnectDialog,
    ToolTip,
    ConfirmDialog,
  },
  methods: {
    logout() {
      localStorage.setItem("jwt-token", "");
      this.$router.push({ path: "/login" });
    },
    NotificationDelete(id) {
      if (id == -1) {
        this.notifications = [];
      } else {
        this.notifications = this.notifications.filter((n) => n.id != id);
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
        if (data.type == "notifications_init") {
          this.notifications = data.data;
        } else if (data.type == "notifications") {
          let newNotifications = data.data;
          for (let i = 0; i < newNotifications.length; i++) {
            this.notifications.push(newNotifications[i]);
            Notify.create({
              progress: true,
              message: newNotifications[i].title,
              caption: newNotifications[i].message,
              position: "bottom",
              icon: this.notificationIcon[newNotifications[i].type],
              timeout: 2000,
              color: this.notificationColor[newNotifications[i].type],
              textColor: "black",
            });
          }
        } else if (data.type == "auth_error") {
          localStorage.setItem("jwt-token", "");
          this.$router.push({ path: "/login" });
        }
      };

      this.ws.onclose = (event) => {
        this.$refs.wsReconnectDialog.show();
      };
    },
    powerAction(action) {
      if (action == "shutdown") {
        this.$refs.confirmDialog.show(
          "Shutdown",
          ["Are you sure you want to shutdown?"],
          this.shutdown,
        );
      } else if (action == "reboot") {
        this.$refs.confirmDialog.show(
          "Reboot",
          ["Are you sure you want to reboot?"],
          this.reboot,
        );
      }
      this.showPowerMenu = false;
    },
    shutdown() {
      this.$api
        .post("host/power/shutdown")
        .then((response) => {
          this.$router.push({ name: "shutdown" });
        })
        .catch((error) => {
          let errormsg = "";
          if (error.response == undefined) {
            errormsg = "Could not connect to server.";
          } else {
            errormsg = error.response.data.detail;
          }
          this.$refs.errorDialog.show("Shutdown error", [errormsg]);
        });
    },
    reboot() {
      this.$api
        .post("host/power/reboot")
        .then((response) => {
          this.$router.push({ name: "reboot" });
        })
        .catch((error) => {
          let errormsg = "";
          if (error.response == undefined) {
            errormsg = "Could not connect to server.";
          } else {
            errormsg = error.response.data.detail;
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
