const routes = [
  {
    path: "/",
    component: () => import("layouts/MainLayout.vue"),
    children: [
      { path: "", redirect: "/dashboard" },
      { path: "dashboard", component: () => import("pages/DashboardPage.vue") },
      { path: "vm-manager", component: () => import("pages/VmPage.vue") },
      { path: "hotplug-usb", component: () => import("pages/HotplugUsbPage.vue") },
      {
        path: "storage-pools",
        component: () => import("src/pages/StoragePoolPage.vue"),
      },
      { path: "tools", component: () => import("pages/ToolsPage.vue") },
      {
        path: "tools/system-info",
        component: () => import("pages/SystemInfoPage.vue"),
      },
      {
        path: "tools/system-devices",
        component: () => import("pages/SystemDevicesPage.vue"),
      },
      {
        path: "tools/download-iso",
        component: () => import("pages/DownloadIsoPage.vue"),
      },
      { path: "tools/about", component: () => import("pages/AboutPage.vue") },
    ],
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: "/:catchAll(.*)*",
    component: () => import("pages/ErrorNotFound.vue"),
  },
];

export default routes;
