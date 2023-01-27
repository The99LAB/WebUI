<template>
  <q-page padding>
    <q-card>
      <q-card-section>
        <div class="text-h6 text-center">System Information</div>
      </q-card-section>
      <q-separator dark inset />
      <q-card-section>
        <div class="row justify-center text-body2">
          <div class="col text-right q-mr-sm text-weight-bold">
            <p>Motherboard</p>
            <p>Processor</p>
            <p>Memory</p>
            <p>Operating System</p>
            <p>Host Name</p>
          </div>
          <div class="col text-weight-regular">
            <p>{{ motherboard }}</p>
            <p>{{ processor }}</p>
            <p>{{ memory }}</p>
            <p>{{ os }}</p>
            <p>{{ hostname }}<q-btn round icon="edit" flat text-color="primary" size="sm" padding="none"
                @click="editHostName()"></q-btn></p>
          </div>
        </div>
      </q-card-section>
    </q-card>

  </q-page>
</template>

<script>
export default {
  data() {
    return {
      motherboard: "MSI A320 Pro Max",
      processor: "Ryzen 5 3600X",
      memory: "4GB",
      os: "Fedora 36 (server)",
      hostname: "Server3",

    }
  },
  components: {
  },
  methods: {
    editHostName() {
      console.log('Editing host name');
    }
  },
}
</script>
