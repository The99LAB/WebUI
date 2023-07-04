const routes = [
  {
    path: "/login",
    component: () => import("pages/LoginPage.vue"),
    meta: { title: "Login" },
  },
  {
    path: "/",
    component: () => import("layouts/MainLayout.vue"),
    children: [
      { path: "", redirect: "/dashboard" },
      {
        path: "dashboard",
        component: () => import("pages/DashboardPage.vue"),
        meta: { title: "Dashboard" },
      },
      {
        path: "vm-manager",
        component: () => import("pages/VmPage.vue"),
        meta: { title: "VM Manager" },
      },
      {
        path: "hotplug-usb",
        component: () => import("pages/HotplugUsbPage.vue"),
        meta: { title: "Hotplug USB" },
      },
      {
        path: "storage-pools",
        component: () => import("src/pages/StoragePoolPage.vue"),
        meta: { title: "Storage Pools" },
      },
      {
        path: "backup-manager",
        component: () => import("pages/BackupManagerPage.vue"),
        meta: { title: "Backup Manager" },
      },
      {
        path: "tools/system-info",
        component: () => import("pages/SystemInfoPage.vue"),
        meta: { title: "System Info" },
      },
      {
        path: "tools/system-devices",
        component: () => import("pages/SystemDevicesPage.vue"),
        meta: { title: "System Devices" },
      },
      {
        path: "tools/download-iso",
        component: () => import("pages/DownloadIsoPage.vue"),
        meta: { title: "Download ISO" },
      },
      {
        path: "tools/about",
        component: () => import("pages/AboutPage.vue"),
        meta: { title: "About" },
      },
      {
        path: "tools/terminal",
        component: () => import("pages/TerminalPage.vue"),
        meta: { title: "Terminal" },
      },
      {
        path: "settings",
        component: () => import("pages/SettingsPage.vue"),
        meta: { title: "Settings" },
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
