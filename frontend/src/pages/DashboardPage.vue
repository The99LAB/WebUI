<template>
  <q-page padding>
    <div class="row justify-center text-center q-gutter-md">
      <q-card class="dashboard-card">
        <div class="row justify-between full-height items-center q-pb-none">
          <div class="system-info-logo col-5 full-height column q-pa-sm">
            <div class="col">
              <q-img
                src="/src/assets/Server99-logo-text.png"
                style="width: 9em"
              />
            </div>
            <div class="col">
              <q-img
                src="/src/assets/Server99-logo-base.png"
                style="width: 6em; transform: translateY(-50%)"
              />
            </div>
          </div>
          <div class="col self-start">
            <p class="text-h6 q-my-none q-pl-md text-left">
              System Information
            </p>
            <div class="row items-center q-my-none q-pl-md text-grey-8">
              <p class="text-subtitle2 q-my-none">Overview</p>
              <q-btn
                flat
                dense
                round
                icon="mdi-eye-outline"
                size="sm"
                @click="$router.push({ name: 'system/system-info' })"
              >
                <q-tooltip :offset="[5, 5]"
                  >View full system information</q-tooltip
                >
              </q-btn>
            </div>
            <div class="text-left row items-center q-pl-md q-my-md">
              <p class="text-subtitle2 text-weight-bolder q-mr-xs q-mb-none">
                Version:
              </p>
              <p class="text-weight-regular q-mb-none">{{ os_name }}</p>
            </div>
            <q-separator spaced="md" />
            <div class="text-left row items-center q-pl-md q-my-md">
              <p class="text-subtitle2 text-weight-bolder q-mr-xs q-mb-none">
                Hostname:
              </p>
              <p class="text-weight-regular q-mb-none">{{ hostname }}</p>
            </div>
            <q-separator spaced="md" />
            <div class="text-left row items-center q-pl-md q-my-md">
              <p class="text-subtitle2 text-weight-bolder q-mr-xs q-mb-none">
                Uptime:
              </p>
              <p class="text-weight-regular q-mb-none">
                {{ uptime }}
              </p>
            </div>
          </div>
        </div>
      </q-card>
      <q-card class="dashboard-card">
        <q-card-section class="text-left row items-center q-pb-none">
          <p class="text-h6 q-mb-none">CPU</p>
          <q-space />
          <p class="text-subtitle2 text-grey-8 q-mb-none">{{ cpu_name }}</p>
        </q-card-section>
        <q-card-section class="row items-center q-py-none">
          <div class="col">
            <q-circular-progress
              show-value
              class="text-light-blue q-ma-md"
              :size="$q.screen.lt.md ? '110px' : '125px'"
              color="light-blue"
              track-color="blue-grey-10"
              :value="cpu_progress"
              >{{ cpu_progress_text }}</q-circular-progress
            >
          </div>
          <div class="col-7">
            <div class="row justify-start q-ml-lg q-my-none items-center">
              <p class="q-mr-sm text-weight-bold">Threads:</p>
              <p>{{ cpu_thread_count }}</p>
            </div>
            <div class="row justify-start q-ml-lg q-my-none items-center">
              <p class="q-mr-sm text-weight-bold">Highest usage:</p>
              <p>
                {{ cpu_thread_highest_usage.usage.toFixed(0) }}% (Thread
                {{ cpu_thread_highest_usage.thread }})
              </p>
            </div>
          </div>
        </q-card-section>
        <q-card-section class="q-py-none">
          <apexchart
            height="150"
            ref="cpuThreadChart"
            type="bar"
            :options="cpuChartOptions"
            :series="cpuChartSeries"
          />
        </q-card-section>
      </q-card>
      <q-card class="dashboard-card">
        <q-card-section class="text-left q-pb-none">
          <p class="text-h6 q-mb-none">Memory</p>
        </q-card-section>
        <q-card-section
          class="row items-center justify-center q-pt-none"
          style="height: 85%"
        >
          <div class="col">
            <div class="row justify-start q-ml-lg q-my-none items-center">
              <div class="q-py-none q-my-none row justify-center items-end">
                <p class="text-h3 q-mr-xs q-py-none q-my-none">
                  {{ Math.round(mem_total * 10) / 10 }}
                </p>
                <p class="text-subtitle1 q-py-none q-my-none">GB</p>
              </div>
            </div>
            <div class="row justify-start q-ml-lg q-my-none items-center">
              <p class="text-subtitle2 text-grey-8 q-py-none">
                Total Available
              </p>
            </div>
            <div class="row justify-start q-ml-lg q-my-none items-center">
              <q-icon
                name="fiber_manual_record"
                class="text-secondary q-mr-xs q-pa-none"
              />
              Used ({{ mem_used }} GB)
            </div>
            <div class="row justify-start q-ml-lg q-my-none items-center">
              <q-icon
                name="fiber_manual_record"
                class="text-primary q-mr-xs q-pa-none"
              />
              Free ( {{ (mem_total - mem_used).toFixed(2) }} GB)
            </div>
          </div>
          <div class="col-8">
            <apexchart
              ref="memUsageChart"
              type="donut"
              :options="memChartOptions"
              :series="memChartSeries"
            />
          </div>
        </q-card-section>
      </q-card>
    </div>
    <q-inner-loading :showing="loadingVisible" />
  </q-page>
  <WsReconnectDialog ref="wsReconnectDialog" @ws-reconnect="connectWebSocket" />
</template>

<style lang="scss" scoped>
body.screen--xs {
  .dashboard-card {
    width: 350px;
    height: 350px;
  }
}
body.screen--sm {
  .dashboard-card {
    width: 400px;
    height: 350px;
  }
}
body.screen--md {
  .dashboard-card {
    width: 500px;
    height: 375px;
  }
}

body.screen--lg,
body.screen--xl {
  .dashboard-card {
    width: 500px;
    height: 400px;
  }
}

.system-info-logo {
  border-top-left-radius: 0.2em;
  border-bottom-left-radius: 0.2em;
}

body.body--light {
  .system-info-logo {
    background-color: $grey-4;
  }
}

body.body--dark {
  .system-info-logo {
    background-color: $grey-10;
  }
}
</style>

<script>
import WsReconnectDialog from "src/components/WsReconnectDialog.vue";
import { convertEpochToUptime } from 'src/utils/timeUtils.js';
import { colors } from "quasar";
import { useHostnameStore } from "stores/hostname";
import { storeToRefs } from "pinia";

export default {
  data() {
    return {
      cpu_name: "",
      cpu_progress: 0,
      cpu_thread_count: null,
      cpu_thread_categories: null,
      cpu_thread_highest_usage: {
        thread: 0,
        usage: 0,
      },
      cpu_progress_text: "",
      mem_used: null,
      mem_total: null,
      uptime: null,
      up_since: null,
      os_name: null,
      loadingVisible: true,
      cpuChartOptions: {
        grid: {
          show: false,
        },
        dataLabels: {
          enabled: false,
        },
        xaxis: {
          axisBorder: {
            show: false,
          },
          axisTicks: {
            show: false,
          },
          categories: [0],
        },
        tooltip: {
          enabled: false,
        },
        states: {
          hover: {
            filter: {
              type: "none",
            },
          },
        },
        chart: {
          toolbar: {
            show: false,
          },
        },
        yaxis: {
          max: 100,
          min: 0,
          tickAmount: 2,
          labels: {
            formatter: function (value) {
              return value.toFixed(0);
            },
          },
        },
        loading: {
          enabled: false,
        },
      },
      cpuChartSeries: [
        {
          name: "Thread",
          data: [0],
        },
      ],
      memChartOptions: {
        type: "donut",
        labels: ["Used", "Free"],
        legend: {
          show: false,
        },
        dataLabels: {
          enabled: false,
        },
        grid: {
          show: false,
        },
        tooltip: {
          enabled: false,
        },
        states: {
          hover: {
            filter: {
              type: "none",
            },
          },
        },
        stroke: {
          show: false,
        },
      },
      memChartSeries: [0],
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
    WsReconnectDialog,
  },
  methods: {
    connectWebSocket() {
      const jwt_token = localStorage.getItem("jwt-token");
      this.ws = new WebSocket(
        this.$WS_ENDPOINT + "/dashboard?token=" + jwt_token,
      );

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type == "dashboard_init") {
          this.mem_total = data.data.mem_total;
          this.cpu_name = data.data.cpu_name;
          this.os_name = data.data.os_name;
          this.up_since = data.data.up_since;
          this.updateUptime();
        }
        if (data.type == "dashboard") {
          this.cpu_progress = data.data.cpu_percent;
          this.cpu_progress_text = data.data.cpu_percent + "%";
          this.cpu_thread_count = data.data.cpu_thread_data.length;
          this.updateCpuChart(this.cpu_thread_count, data.data.cpu_thread_data);
          let highest_thread_usage = Math.max(...data.data.cpu_thread_data);
          this.cpu_thread_highest_usage.thread =
            data.data.cpu_thread_data.indexOf(highest_thread_usage);
          this.cpu_thread_highest_usage.usage = highest_thread_usage;
          this.mem_used = data.data.mem_used;
          this.updateMemChart(this.mem_used, this.mem_total);
          this.loadingVisible = false;
        } else if (data.type == "auth_error") {
          localStorage.setItem("jwt-token", "");
          this.$router.push({ path: "/login" });
        }
      };

      this.ws.onclose = (event) => {
        this.$refs.wsReconnectDialog.show();
      };
    },
    updateCpuChart(threadCount, threadData) {
      if (this.cpu_thread_categories == null) {
        this.cpu_thread_categories = [];
        for (let i = 0; i < threadCount; i++) {
          this.cpu_thread_categories.push(i);
        }
      }
      this.$refs.cpuThreadChart.updateOptions({
        xaxis: {
          categories: this.cpu_thread_categories,
        },
      });
      this.$refs.cpuThreadChart.updateSeries([
        {
          data: threadData,
        },
      ]);
    },
    updateMemChart(used, total) {
      this.$refs.memUsageChart.updateOptions({
        colors: [
          colors.getPaletteColor("secondary"),
          colors.getPaletteColor("primary"),
        ],
      });
      this.$refs.memUsageChart.updateSeries([used, total - used]);
    },
    updateUptime() {
      if (this.up_since != null) {
        this.uptime = convertEpochToUptime(this.up_since);
      }
    }
  },
  created() {
    this.connectWebSocket();
  },
  mounted() {
    this.upTimeInterval = setInterval(() => {
      this.updateUptime();
    }, 1000);
  },
  unmounted() {
    this.ws.onclose = () => {};
    this.ws.close();
  },
  beforeUnmount() {
    clearInterval(this.upTimeInterval);
  },
};
</script>
