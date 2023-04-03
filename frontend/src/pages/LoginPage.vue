<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page
        padding
        class="row justify-center items-center"
      >
        <q-card>
          <q-card-section class="bg-primary">
            <h5 class="text-center q-my-md text-white">{{ hostname }} - Login</h5>
          </q-card-section>
          <q-card-section class="q-px-lg q-py-lg">
            <div class="q-mx-lg">
              <q-input
                class="q-mb-md q-mt-md"
                name="username"
                square
                clearable
                v-model="username"
                label="Username"
                @update:model-value="authError = ''"
              >
                <template v-slot:prepend>
                  <q-icon name="mdi-account" />
                </template>
              </q-input>
              <q-input
                name="password"
                square
                clearable
                v-model="password"
                :type="isPwd ? 'password' : 'text'"
                label="Password"
                @update:model-value="authError = ''"
              >
                <template v-slot:prepend>
                  <q-icon name="mdi-lock" />
                </template>
                <template v-slot:append>
                  <q-icon
                    :name="isPwd ? 'visibility_off' : 'visibility'"
                    class="cursor-pointer"
                    @click="isPwd = !isPwd"
                  />
                </template>
              </q-input>
              <q-separator color="transparent" spaced inset dark />
              <p class="text-body2 text-weight-bold text-center text-negative">
                {{ authError }}
              </p>
            </div>
          </q-card-section>
          <q-card-actions class="q-pa-lg">
            <q-btn
              size="lg"
              color="primary"
              class="full-width"
              label="Login"
              @click="login"
              :loading="loginLoading"
            />
          </q-card-actions>
        </q-card>
      </q-page>
    </q-page-container>
  </q-layout>
  <ErrorDialog ref="errorDialog" />
</template>
<script>
import { ref } from "vue";
import ErrorDialog from "/src/components/ErrorDialog.vue";

export default {
  data() {
    return {
      isPwd: ref(true),
      username: "",
      password: "",
      authError: "",
      loginLoading: false,
      hostname: "Unknown",
    };
  },
  components: {
    ErrorDialog,
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
          this.authError = error.response.data;
          this.loginLoading = false;
        });
    },
  },
  created() {
    this.$api
      .get("/no-auth/hostname")
      .then((response) => {
        this.hostname = response.data.hostname;
      })
      .catch((error) => {
        this.$refs.errorDialog.show("Error connecting to backend", [
          "Couln't get hostname from backend. Please check if the backend is running and the API is reachable.",
        ]);
      });
  },
};
</script>
