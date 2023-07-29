<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page padding class="row justify-center items-center">
        <q-card>
          <q-linear-progress
            rounded
            :query="loginLoading"
            track-color="primary"
            color="secondary"
          />
          <q-card-section class="q-pb-none">
            <img
              class="login-logo"
              src="/src/assets/Server99-logo-full.png"
              alt="Logo"
            />
          </q-card-section>
          <q-card-section class="q-py-lg q-px-lg">
            <q-input
              class="q-mb-md q-mt-md"
              name="username"
              square
              clearable
              v-model="username"
              label="Username"
              @update:model-value="authError = ''"
              @keydown.tab.prevent="$refs.passwordInput.focus()"
              autocapitalize="off"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-account" />
              </template>
            </q-input>
            <q-input
              style="width: 20em"
              name="password"
              square
              clearable
              v-model="password"
              :type="isPwd ? 'password' : 'text'"
              label="Password"
              ref="passwordInput"
              @update:model-value="authError = ''"
              @keyup.enter="login"
            >
              <template v-slot:prepend>
                <q-icon name="mdi-lock" />
              </template>
              <template v-slot:append>
                <q-icon
                  :name="isPwd ? 'visibility_off' : 'visibility'"
                  class="cursor-pointer"
                  @click="isPwd = !isPwd"
                >
                  <ToolTip
                    :content="isPwd ? 'Show Password' : 'Hide Password'"
                  />
                </q-icon>
              </template>
            </q-input>
            <p
              class="text-body2 text-weight-bold text-center text-negative q-mb-none"
            >
              {{ authError }}&nbsp;
            </p>
          </q-card-section>
          <q-card-actions class="q-pb-md q-px-md">
            <q-btn
              outline
              size="lg"
              color="primary"
              class="full-width"
              label="Login"
              @click="login"
            />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
  <ErrorDialog ref="errorDialog" />
</template>

<style lang="scss" scoped>
body.screen--xs,
body.screen--sm,
body.screen--md,
body.screen--lg,
body.screen--xl {
  .login-logo {
    width: 12em;
    margin-left: auto;
    margin-right: auto;
    display: block;
  }
}
</style>
<script>
import { ref } from "vue";
import ErrorDialog from "/src/components/ErrorDialog.vue";
import ToolTip from "src/components/ToolTip.vue";
import { useHostnameStore } from "stores/hostname";
import { storeToRefs } from "pinia";

export default {
  data() {
    return {
      isPwd: ref(true),
      username: "",
      password: "",
      authError: "",
      loginLoading: false,
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
    ErrorDialog,
    ToolTip,
  },
  methods: {
    login() {
      this.loginLoading = true;
      this.$api
        .post("login", { username: this.username, password: this.password })
        .then((response) => {
          this.authError = "";
          localStorage.setItem("jwt-token", response.data.access_token);
          this.$router.push({ path: "/dashboard" });
          this.loginLoading = false;
        })
        .catch((error) => {
          if (error.response == undefined) {
            this.authError = "Server is not responding";
          } else {
            this.authError = error.response.data.detail;
          }
          this.loginLoading = false;
        });
    },
  },
};
</script>
