<template>
  <q-page padding>
    <div class="row justify-evenly">
      <div class="text-center" v-show="!loadingVisible">
        <p>CPU</p>
        <q-circular-progress
          show-value
          class="text-light-blue q-ma-md"
          size="150px"
          color="light-blue"
          :value="cpu_progress"
          >{{ cpu_progress_text }}</q-circular-progress
        >
      </div>
      <div class="text-center" v-show="!loadingVisible">
        <p>Memory</p>
        <q-circular-progress
          show-value
          class="text-light-blue q-ma-md"
          size="150px"
          color="light-blue"
          :value="mem_progress"
        >
          {{ mem_progress_text }}
        </q-circular-progress>
      </div>
    </div>
    <q-inner-loading :showing="loadingVisible">
      <q-spinner-gears size="50px" color="primary" />
    </q-inner-loading>
  </q-page>
</template>

<script>
export default {
  data() {
    return {
      cpu_progress: 0,
      cpu_progress_text: "",
      mem_progress: 0,
      mem_progress_text: "",
      loadingVisible: true,
    };
  },
  methods: {
    get_data(){
      this.$api
        .get("/host/state/dashboard")
        .then((response) => {
          this.cpu_progress = response.data.cpuOverall;
          this.cpu_progress_text = response.data.cpuOverall + "%";
          this.mem_progress = response.data.memory;
          this.mem_progress_text = response.data.memory + "%";
          this.loadingVisible = false;
        })
        .catch((error) => {
          this.$refs.errorDialog.show("Error getting dashboard data", [error])
        });
    }
  },
  mounted() {
    this.get_data();
    
    this.cpuinterval = setInterval(() => {
      this.get_data();
    }, 1000);

    // this.meminterval = setInterval(() => {
    //   if (this.socket.connected){
    //     this.$socket.emit("get_mem_usage");
    //   }
    // }, 1000);
  },
  unmounted() {

  },
  beforeUnmount() {
    // clearInterval(this.cpuinterval);
    // clearInterval(this.meminterval);
  },
};
</script>
