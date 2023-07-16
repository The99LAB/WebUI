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
        component: () => import("pages/ShutdownPage.vue"),
        meta: { title: "Shutdown" },
      },
      // {
      //   path: "reboot",
      //   name: "reboot",
      //   component: () => import("pages/RebootPage.vue"),
      //   meta: { title: "Reboot" },
      // },
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
        name: "vm-manager",
        path: "vm-manager",
        component: () => import("pages/VmPage.vue"),
        meta: { title: "VM Manager" },
      },
      {
        name: "hotplug-usb",
        path: "hotplug-usb",
        component: () => import("pages/HotplugUsbPage.vue"),
        meta: { title: "Hotplug USB" },
      },
      {
        name: "storage-pools",
        path: "storage-pools",
        component: () => import("src/pages/StoragePoolPage.vue"),
        meta: { title: "Storage Pools" },
      },
      {
        path: "backup-manager",
        name: "backup-manager",
        component: () => import("pages/BackupManagerPage.vue"),
        meta: { title: "Backup Manager" },
      },
      {
        path: "tools/system-info",
        name: "system-info",
        component: () => import("pages/SystemInfoPage.vue"),
        meta: { title: "System Info" },
      },
      {
        path: "tools/system-devices",
        name: "system-devices",
        component: () => import("pages/SystemDevicesPage.vue"),
        meta: { title: "System Devices" },
      },
      {
        path: "tools/download-iso",
        name: "download-iso",
        component: () => import("pages/DownloadIsoPage.vue"),
        meta: { title: "Download ISO" },
      },
      {
        path: "tools/about",
        name: "about",
        component: () => import("pages/AboutPage.vue"),
        meta: { title: "About" },
      },
      {
        path: "tools/terminal",
        name: "terminal",
        component: () => import("pages/TerminalPage.vue"),
        meta: { title: "Terminal" },
      },
      {
        path: "settings",
        name: "settings",
        component: () => import("pages/SettingsPage.vue"),
        meta: { title: "Settings" },
      },
      {
        path: "notifications-test",
        name: "notifications-test",
        component: () => import("pages/NotificationsPageTest.vue"),
        meta: { title: "Notifications Test" },
        devOnly: true,
      }
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
