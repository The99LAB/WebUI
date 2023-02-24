<template>
  <q-layout view="lHh Lpr lFf">
    <q-page-container>
      <q-page
        padding
        class="window-height window-width row justify-center items-center"
      >
        <q-card square class="shadow-24" style="width: 400px; height: 540px">
          <q-card-section class="bg-primary">
            <h5 class="text-white text-center q-my-md">Login</h5>
          </q-card-section>
          <q-card-section>
            <div class="q-px-sm q-pt-xl">
              <q-input
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
                square
                clearable
                v-model="password"
                type="password"
                label="Password"
                @update:model-value="authError = ''"
              >
                <template v-slot:prepend>
                  <q-icon name="mdi-lock" />
                </template>
              </q-input>
              <q-separator spaced inset dark />
              <p class="text-body2 text-weight-bold text-center text-negative">
                {{ authError }}
              </p>
            </div>
          </q-card-section>

          <q-card-actions class="q-px-lg">
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
</template>
<script>
export default {
  data() {
    return {
      username: "",
      password: "",
      authError: "",
      loginLoading: false,
    };
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
};
</script>
