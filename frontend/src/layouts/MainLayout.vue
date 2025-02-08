<template>
  <q-layout view="lHh LpR fFf">
    <q-header class="header-theme">
      <q-toolbar>
        <q-btn dense flat round icon="menu" @click="leftDrawerOpen = !leftDrawerOpen">
          <ToolTip content="Toggle" />
        </q-btn>
        <q-space />
        <q-btn dense flat round icon="notifications" @click="rightDrawerOpen = !rightDrawerOpen">
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
          :icon="$q.dark.isActive ? 'mdi-lightbulb' : 'mdi-moon-waning-crescent'"
          @click="this.$q.dark.toggle()"
        >
          <ToolTip :content="$q.dark.isActive ? 'Enable light mode' : 'Enable dark mode'" />
        </q-btn>
        <q-btn dense flat round icon="logout" @click="logout()">
          <ToolTip content="Logout" />
        </q-btn>
      </q-toolbar>
    </q-header>

    <q-drawer show-if-above v-model="leftDrawerOpen" side="left" bordered :width="200">
      <q-list>
        <q-item class="q-pa-md">
          <q-item-section top avatar>
            <q-img src="../assets/Server99-logo-base.png" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="text-body1">
              <q-tooltip anchor="bottom left" self="top left" :offset="[0, 5]"> User </q-tooltip>
              <q-icon name="mdi-account" />
              {{ username }}
            </q-item-label>
            <q-item-label class="text-body2">
              <q-tooltip anchor="bottom left" self="top left" :offset="[0, 5]">
                Hostname
              </q-tooltip>
              {{ hostname }}
            </q-item-label>
          </q-item-section>
        </q-item>
        <DashboardItem to="/dashboard" icon="bi-speedometer" name="Dashboard" />
        <q-item-label header class="q-pb-none q-pt-md">Virtual Machines OLD</q-item-label>
        <DashboardItem to="/vm-manager/vms" icon="ion-cube" name="Virtual Machines" />
        <DashboardItem to="/vm-manager/hotplug-usb" icon="mdi-usb" name="Hotplug USB" />
        <DashboardItem to="/vm-manager/backups" icon="mdi-backup-restore" name="Backups" />
        <DashboardItem to="/vm-manager/download-iso" icon="mdi-disc" name="Download ISO" />
        <q-item-label header class="q-pb-none q-pt-md">Virtual Machines New</q-item-label>
        <DashboardItem to="/vm/overview" icon="ion-cube" name="Virtual Machines" />
        <DashboardItem to="/vm/templates" icon="mdi-cube-outline" name="Templates" />
        <q-item-label header class="q-pb-none q-pt-md">Docker</q-item-label>
        <DashboardItem to="/docker-manager/containers" icon="bi-boxes" name="Containers" />
        <DashboardItem to="/docker-manager/images" icon="fa-solid fa-clone" name="Images" />
        <DashboardItem to="/docker-manager/networks" icon="mdi-lan" name="Networks" />
        <q-expansion-item>
          <template v-slot:header>
            <div class="row items-center">
              <div class="q-pr-md"><q-icon name="bi-files" size="sm" /></div>
              <div>Templates</div>
            </div>
          </template>
          <DashboardItem
            to="/docker-manager/templates/settings"
            class="q-ml-sm"
            icon="mdi-cog"
            name="Settings"
          />
        </q-expansion-item>
        <q-item-label header class="q-pb-none q-pt-md">Storage</q-item-label>
        <DashboardItem to="/storage-manager/disks" icon="bi-hdd" name="Disks" />
        <DashboardItem
          to="/storage-manager/raid-manager"
          icon="mdi-database-outline"
          name="RAID Management"
        />
        <DashboardItem
          to="/storage-manager/sharedfolders"
          icon="mdi-share-variant-outline"
          name="Shared Folders"
        />
        <q-item-label header class="q-pb-none q-pt-md">System</q-item-label>
        <DashboardItem to="/system/system-info" icon="mdi-monitor" name="System Information" />
        <DashboardItem to="/system/networks" icon="mdi-network" name="Networks" />
        <DashboardItem to="/system/system-devices" icon="bi-gpu-card" name="System Devices" />
        <DashboardItem to="/system/users" icon="mdi-account" name="Users" />
        <DashboardItem
          to="/system/filemanager"
          icon="mdi-folder-multiple-outline"
          name="File Manager"
        />
        <DashboardItem to="/system/settings" icon="mdi-cog" name="Settings" />
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
            <q-circular-progress
              :show-value="n.progress != -1"
              size="lg"
              :class="'text-' + notificationColor[n.type]"
              :color="notificationColor[n.type]"
              track-color="grey-9"
              :value="n.progress"
              :indeterminate="n.progress == -1"
              v-if="n.type == 'progress'"
            />
            <q-icon
              :name="notificationIcon[n.type]"
              :color="notificationColor[n.type]"
              size="lg"
              v-else
            />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ n.title }}</q-item-label>
            <q-item-label caption>{{ n.message }}</q-item-label>
            <q-item-label caption class="row">
              <q-btn
                @click="NotificationDelete(n.id)"
                flat
                text-color="primary"
                size="sm"
                padding="none"
                label="Dismiss"
                v-if="n.type != 'progress' || (n.type == 'progress' && n.progress == 100)"
              />
              <q-space />{{ n.timestamp }}
            </q-item-label>
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
      <WsReconnectDialog ref="wsReconnectDialog" @ws-reconnect="connectNotificationsWebsocket" />
    </q-page-container>
  </q-layout>
</template>

<style lang="scss" scoped>
body.body--light {
  .header-theme {
    background-color: $primary;
  }
}

body.body--dark {
  .header-theme {
    background-color: $dark;
  }
}
</style>

<script>
import { defineComponent, ref } from 'vue'
import ErrorDialog from 'src/components/ErrorDialog.vue'
import WsReconnectDialog from 'src/components/WsReconnectDialog.vue'
import ToolTip from 'src/components/ToolTip.vue'
import { useHostnameStore } from 'stores/hostname'
import { useUsernameStore } from 'stores/username'
import { storeToRefs } from 'pinia'
import ConfirmDialog from 'src/components/ConfirmDialog.vue'
import DashboardItem from 'src/components/DashboardItem.vue'

export default defineComponent({
  name: 'MainLayout',
  data() {
    return {
      leftDrawerOpen: ref(false),
      rightDrawerOpen: ref(false),
      notifications: [],
      showPowerMenu: ref(false),
      notificationIcon: {
        error: 'mdi-alert-circle',
        warning: 'mdi-alert-circle',
        success: 'mdi-check-circle',
        info: 'mdi-information',
      },
      notificationColor: {
        error: 'red',
        warning: 'orange',
        success: 'green',
        info: 'white',
        progress: 'blue',
      },
    }
  },
  setup() {
    const hostname_store = useHostnameStore()
    const { getHostname } = storeToRefs(hostname_store)
    const username_store = useUsernameStore()
    const { getUsername } = storeToRefs(username_store)
    return {
      hostname: getHostname,
      username: getUsername,
      username_store,
    }
  },

  components: {
    ErrorDialog,
    WsReconnectDialog,
    ToolTip,
    ConfirmDialog,
    DashboardItem,
  },
  methods: {
    logout() {
      localStorage.setItem('jwt-token', '')
      this.username_store.clearUsername()
      this.$router.push({ path: '/login' })
    },
    NotificationDelete(id) {
      if (id == -1) {
        this.notifications = this.notifications.filter((n) => n.type == 'progress')
      } else {
        this.notifications = this.notifications.filter((n) => n.id != id)
      }

      this.$api.delete('notifications/' + id).catch((error) => {
        this.$refs.errorDialog.show('Error deleting notification', [
          'Could not delete notification.',
          error.response.data.detail,
        ])
      })
    },
    connectNotificationsWebsocket() {
      const jwt_token = localStorage.getItem('jwt-token')
      this.ws = new WebSocket(this.$WS_ENDPOINT + '/notifications?token=' + jwt_token)

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        if (data.type == 'notifications_init') {
          this.notifications = data.data
        } else if (data.type == 'notifications') {
          this.notifications = data.data
        } else if (data.type == 'auth_error') {
          localStorage.setItem('jwt-token', '')
          this.$router.push({ path: '/login' })
        }
      }

      this.ws.onclose = () => {
        this.$refs.wsReconnectDialog.show()
      }
    },
    powerAction(action) {
      if (action == 'shutdown') {
        this.$refs.confirmDialog.show(
          'Shutdown',
          ['Are you sure you want to shutdown?'],
          this.shutdown,
        )
      } else if (action == 'reboot') {
        this.$refs.confirmDialog.show('Reboot', ['Are you sure you want to reboot?'], this.reboot)
      }
      this.showPowerMenu = false
    },
    shutdown() {
      this.$api
        .post('host/power/shutdown')
        .then(() => {
          this.$router.push({ name: 'shutdown' })
        })
        .catch((error) => {
          let errormsg = ''
          if (error.response == undefined) {
            errormsg = 'Could not connect to server.'
          } else {
            errormsg = error.response.data.detail
          }
          this.$refs.errorDialog.show('Shutdown error', [errormsg])
        })
    },
    reboot() {
      this.$api
        .post('host/power/reboot')
        .then(() => {
          this.$router.push({ name: 'reboot' })
        })
        .catch((error) => {
          let errormsg = ''
          if (error.response == undefined) {
            errormsg = 'Could not connect to server.'
          } else {
            errormsg = error.response.data.detail
          }
          this.$refs.errorDialog.show('Reboot error', [errormsg])
        })
    },
  },
  created() {
    this.connectNotificationsWebsocket()
  },
  unmounted() {
    this.ws.onclose = () => {}
    this.ws.close()
  },
})
</script>
<style lang="scss">
.disable-focus-helper {
  .q-focus-helper {
    opacity: 0 !important;
  }
}
</style>
