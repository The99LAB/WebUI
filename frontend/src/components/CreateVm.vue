<template>
    <q-dialog v-model="layout">
        <q-layout view="hHh lpR fFf" container class="bg-white">
            <q-header bordered class="bg-primary text-white" height-hint="98">
                <q-toolbar>
                    <q-toolbar-title>Create VM</q-toolbar-title>
                    <q-btn icon="close" flat round dense v-close-popup />
                </q-toolbar>

                <q-tabs allign="left" v-model="tab">
                    <q-tab name="cpu" label="CPU" />
                    <q-tab name="memory" label="Memory" />
                    <q-tab name="storage" label="Storage" />
                </q-tabs>
                <q-separator />

                
            </q-header>

            <q-page-container>
                <q-page padding>
                    <q-tab-panels v-model="tab" animated>
                    <q-tab-panel name="cpu">
                        <div class="text-h6">CPU</div>
                       CPU tab
                    </q-tab-panel>

                    <q-tab-panel name="memory">
                        <div class="text-h6">Memory</div>
                        Memory tab
                    </q-tab-panel>

                    <q-tab-panel name="storage">
                        <div class="text-h6">Storage</div>
                        Storage tab
                    </q-tab-panel>
                    </q-tab-panels>
                </q-page>
            </q-page-container>
        </q-layout>
    </q-dialog>
</template>


<script>
import { ref } from 'vue'

export default {
  data () {
    return {
      layout: ref(false),
      tab: ref('cpu')
    }
  },
    methods: {
        show() {
            this.layout = true
        }
    }
}
</script>