<template>
  <q-dialog v-model="layout">
    <q-card style="min-width: 60vw">
      <q-card-section class="row items-center q-pb-none">
        <div class="text-h6">Add Device</div>
        <q-space />
        <q-btn icon="close" flat round dense v-close-popup />
      </q-card-section>
      <q-separator color="transparent" spaced="lg" inset />
      <q-card-section v-if="optionLayout">
        <q-list bordered>
          <q-item
            clickable
            v-ripple
            :active="option === 'disk-file'"
            @click="option = 'disk-file'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon color="primary" name="mdi-harddisk" />
            </q-item-section>
            <q-item-section>Disk (file)</q-item-section>
          </q-item>
          <q-item
            clickable
            v-ripple
            :active="option === 'disk-block'"
            @click="option = 'disk-block'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon color="primary" name="mdi-harddisk" />
            </q-item-section>
            <q-item-section>Disk (Block)</q-item-section>
          </q-item>
          <q-item
            clickable
            v-ripple
            :active="option === 'network'"
            @click="option = 'network'"
            active-class="my-menu-link"
          >
            <q-item-section avatar>
              <q-icon color="primary" name="mdi-ethernet" />
            </q-item-section>
            <q-item-section>Network Interface</q-item-section>
          </q-item>
        </q-list>
      </q-card-section>
      <q-card-section v-if="diskfileLayout">
        <q-input filled v-model="diskfile" label="Disk File" />
        <q-input filled v-model="diskfile" label="Disk File" />
        <q-input filled v-model="diskfile" label="Disk File" />
      </q-card-section>
      <q-card-section v-if="diskblockLayout">
        <q-input filled v-model="diskblock" label="Disk Block" />
        <q-input filled v-model="diskblock" label="Disk Block" />
        <q-input filled v-model="diskblock" label="Disk Block" />
      </q-card-section>
      <q-card-section v-if="networkLayout" class="q-pa-md">
        <q-select class="q-py-md" v-model="networkSource" :options="libvirtNetworks" label="Network Source" filled/>
        <q-select class="q-py-md" v-model="networkInterfaceType" :options="networkInterfaceTypes" label="Network Interface Type" filled />
        <q-checkbox left-label v-model="networkCustomMac" label="Custom MAC Address" />
        <q-input filled v-model="networkCustomMacAddress" label="Mac address" v-if="networkCustomMac"/>
      </q-card-section>
      <q-card-actions align="right">
        <q-btn
            icon="mdi-arrow-right"
          color="primary"
          flat
          @click="optionChose"
          v-if="optionLayout"
        >
            <ToolTip content="Next" />
        </q-btn>
        <q-btn color="primary" icon="check" flat  @click="networkCreate" v-if="networkLayout">
            <ToolTip content="Create" />
        </q-btn>
        <!-- <q-btn flat label="Yes" @click="confirmYes" />
            <q-btn flat label="No" @click="confirmNo()" /> -->
      </q-card-actions>
    </q-card>
  </q-dialog>
</template>

<style lang="scss">
.my-menu-link {
  color: white;
  background: $secondary;
}
</style>

<script>
import ToolTip from '../ToolTip.vue';

export default {
  data() {
    return {
      layout: false,
      vmid: null,
      option: "disk-file",
      optionLayout: true,
      diskfileLayout: false,
      diskblockLayout: false,
      networkLayout: false,
      networkInterfaceTypes: [
        { label: "VirtIO", value: "virtio" },
        { label: "e1000", value: "e1000" },
        { label: "rtl8139", value: "rtl8139" },
      ],
      networkInterfaceType: "virtio",
      networkSource: "default",
      networkCustomMac: false,
      networkCustomMacAddress: "52:54:00:a8:7e:c9",
      libvirtNetworks: [
        { label: "default", value: "default" },
      ]
    };
  },
  components: {
    ToolTip,
},
  methods: {
    show(vmid) {
      this.layout = true;
      this.vmid = vmid;
      this.optionLayout = true;
      this.diskfileLayout = false;
      this.diskblockLayout = false;
      this.networkLayout = false;
    },
    optionChose() {
      if (this.option === "disk-file") {
        this.optionLayout = false;
        this.diskfileLayout = true;
      } else if (this.option === "disk-block") {
        this.optionLayout = false;
        this.diskblockLayout = true;
      } else if (this.option === "network") {
        this.optionLayout = false;
        this.networkLayout = true;
      }
    },
  },
};
</script>
