<template>
  <section class="panel auth-panel">
    <p class="eyebrow">Welcome back</p>
    <h2>Sign in to FinFlow</h2>

    <form class="form" @submit.prevent="handleLogin">
      <div class="field">
        <label for="email">Email</label>
        <input
          id="email"
          v-model="email"
          type="email"
          placeholder="you@example.com"
          autocomplete="email"
          required
        />
      </div>

      <div class="field">
        <label for="password">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          placeholder="••••••••"
          autocomplete="current-password"
          required
        />
      </div>

      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

      <button class="btn" type="submit" :disabled="loading">
        {{ loading ? "Signing in…" : "Sign in" }}
      </button>
    </form>

    <p class="auth-footer">
      Don't have an account?
      <RouterLink to="/register">Create one</RouterLink>
    </p>
  </section>
</template>

<script setup lang="ts">
import { ref } from "vue";
import { useRouter } from "vue-router";

import { authApi } from "../api/auth";
import { useAuthStore } from "../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMsg = ref("");

async function handleLogin() {
  errorMsg.value = "";
  loading.value = true;
  try {
    const resp = await authApi.login({ email: email.value, password: password.value });
    authStore.setToken(resp.data.access_token);
    await authStore.fetchUser();
    router.push("/");
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail ?? "Login failed. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>
