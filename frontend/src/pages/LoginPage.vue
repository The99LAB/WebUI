<template>
    <q-layout view="lHh Lpr lFf">
        <q-page-container>
            <q-page padding>
            <h5>Login</h5>
            <q-input v-model="username" label="Username" />
            <q-input v-model="password" label="Password" type="password"/>
            <q-separator spaced inset dark />
            <q-btn color="primary" icon="check" label="Login" @click="login" />
            <!-- error -->
            <q-separator spaced inset dark />
            <p class="text-body2 text-weight-bold text-negative">{{ authError }}</p>
            </q-page>
        </q-page-container>
    </q-layout>
</template>

<script>

export default {
    data() {
        return {
            username: '',
            password: '',
            authError: ''
        }
    },
    methods: {
        login() {
            this.$api.post('login', { "username": this.username, "password": this.password })
                .then(response => {
                    this.authError = ''
                    localStorage.setItem("jwt-token", response.data.access_token)
                    this.$router.push({ path: '/dashboard' })
                })
                .catch(error => {
                    this.authError = error.response.data
                })
        },
    }
}
</script>