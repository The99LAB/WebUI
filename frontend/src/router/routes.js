const routes = [
  {
    path: "/login",
    name: "login",
    component: () => import("pages/LoginPage.vue"),
    meta: { title: "Login" },
  },
  {
    path: "/powerstate",
    children: [
      {
        path: "shutdown",
        name: "shutdown",
        component: () => import("pages/power-state/ShutdownPage.vue"),
        meta: { title: "Shutdown" },
      },
      {
        path: "reboot",
        name: "reboot",
        component: () => import("pages/power-state/RebootPage.vue"),
        meta: { title: "Reboot" },
      },
    ],
  },
  {
    path: "/",
    component: () => import("layouts/MainLayout.vue"),
    children: [
      { path: "", redirect: "/dashboard" },
      {
        name: "dashboard",
        path: "dashboard",
        component: () => import("pages/DashboardPage.vue"),
        meta: { title: "Dashboard" },
      },
      {
        name: "vm-manager/vms",
        path: "vm-manager/vms",
        component: () => import("pages/vm-manager/VmPage.vue"),
        meta: { title: "VM Manager" },
      },
      {
        name: "vm-manager/hotplug-usb",
        path: "vm-manager/hotplug-usb",
        component: () => import("pages/vm-manager/HotplugUsbPage.vue"),
        meta: { title: "Hotplug USB" },
      },
      {
        name: "vm-manager/storage-pools",
        path: "vm-manager/storage-pools",
        component: () => import("pages/vm-manager/StoragePoolPage.vue"),
        meta: { title: "Storage Pools" },
      },
      {
        path: "vm-manager/backups",
        name: "vm-manager/backups",
        component: () => import("pages/vm-manager/BackupManagerPage.vue"),
        meta: { title: "Backups" },
      },
      {
        path: "vm-manager/download-iso",
        name: "vm-manager/download-iso",
        component: () => import("pages/vm-manager/DownloadIsoPage.vue"),
        meta: { title: "Download ISO" },
      },
      {
        path: "docker-manager/containers",
        name: "docker-manager/containers",
        component: () => import("pages/docker-manager/ContainersPage.vue"),
        meta: { title: "Docker Containers" },
      },
      {
        path: "docker-manager/images",
        name: "docker-manager/images",
        component: () => import("pages/docker-manager/ImagesPage.vue"),
        meta: { title: "Docker Images" },
      },
      {
        path: "docker-manager/networks",
        name: "docker-manager/networks",
        component: () => import("pages/docker-manager/NetworksPage.vue"),
        meta: { title: "Docker Networks" },
      },
      {
        path: "docker-manager/templates",
        name: "docker-manager/templates",
        component: () => import("pages/docker-manager/TemplatesPage.vue"),
        meta: { title: "Docker Templates" },
      },
      {
        path: "docker-manager/templates/settings",
        name: "docker-manager/templates/settings",
        component: () =>
          import("pages/docker-manager/TemplatesSettingsPage.vue"),
        meta: { title: "Docker Templates Settings" },
      },
      {
        path: "system/system-info",
        name: "system/system-info",
        component: () => import("pages/system/SystemInfoPage.vue"),
        meta: { title: "System Info" },
      },
      {
        path: "system/system-devices",
        name: "system/system-devices",
        component: () => import("pages/system/SystemDevicesPage.vue"),
        meta: { title: "System Devices" },
      },
      {
        path: "system/terminal",
        name: "system/terminal",
        component: () => import("pages/system/TerminalPage.vue"),
        meta: { title: "Terminal" },
      },
      {
        path: "system/settings",
        name: "system/settings",
        component: () => import("pages/system/SettingsPage.vue"),
        meta: { title: "Settings" },
      },
      {
        path: "notifications-test",
        name: "notifications-test",
        component: () => import("pages/NotificationsPageTest.vue"),
        meta: { title: "Notifications Test" },
        devOnly: true,
      },
    ],
  },
  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/ErrorNotFound.vue"),
    meta: { title: "404" },
  },
];

export default routes;
