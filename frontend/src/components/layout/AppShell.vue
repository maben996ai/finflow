<template>
  <div class="shell">
    <aside class="sidebar">
      <div>
        <p class="eyebrow">FinFlow</p>
        <h1>Investor signal cockpit</h1>
      </div>
      <nav class="nav">
        <RouterLink to="/">Feed</RouterLink>
        <RouterLink to="/creators">Creators</RouterLink>
        <RouterLink to="/settings">Settings</RouterLink>
        <RouterLink to="/crawl-logs">Crawl Logs</RouterLink>
      </nav>
      <div class="sidebar-footer">
        <p class="muted sidebar-user">{{ authStore.user?.display_name ?? authStore.user?.email }}</p>
        <button class="btn btn-ghost sidebar-logout" @click="handleLogout">Sign out</button>
      </div>
    </aside>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

import { useAuthStore } from "../../stores/auth";

const router = useRouter();
const authStore = useAuthStore();

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>
