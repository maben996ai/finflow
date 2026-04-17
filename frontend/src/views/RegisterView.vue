<template>
  <section class="panel auth-panel">
    <p class="eyebrow">New workspace</p>
    <h2>Create your account</h2>

    <form class="form" @submit.prevent="handleRegister">
      <div class="field">
        <label for="display_name">Display name</label>
        <input
          id="display_name"
          v-model="displayName"
          type="text"
          placeholder="Your name"
          autocomplete="name"
        />
      </div>

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
          placeholder="At least 8 characters"
          autocomplete="new-password"
          minlength="8"
          required
        />
      </div>

      <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

      <button class="btn" type="submit" :disabled="loading">
        {{ loading ? "Creating account…" : "Create account" }}
      </button>
    </form>

    <p class="auth-footer">
      Already have an account?
      <RouterLink to="/login">Sign in</RouterLink>
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

const displayName = ref("");
const email = ref("");
const password = ref("");
const loading = ref(false);
const errorMsg = ref("");

async function handleRegister() {
  errorMsg.value = "";
  loading.value = true;
  try {
    await authApi.register({
      email: email.value,
      password: password.value,
      display_name: displayName.value || undefined,
    });
    const loginResp = await authApi.login({ email: email.value, password: password.value });
    authStore.setToken(loginResp.data.access_token);
    await authStore.fetchUser();
    router.push("/");
  } catch (err: any) {
    errorMsg.value = err.response?.data?.detail ?? "Registration failed. Please try again.";
  } finally {
    loading.value = false;
  }
}
</script>
