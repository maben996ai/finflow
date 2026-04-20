<template>
  <div class="shell">
    <aside class="sidebar">
      <h1 class="sidebar-logo">TrendRadar</h1>
      <nav class="nav">
        <RouterLink to="/">{{ t("nav.feed") }}</RouterLink>
        <RouterLink to="/sources">{{ t("nav.dataSources") }}</RouterLink>
        <RouterLink to="/content-analysis">{{ t("nav.contentAnalysis") }}</RouterLink>
        <RouterLink to="/control-center">{{ t("nav.controlCenter") }}</RouterLink>
      </nav>
      <div class="sidebar-footer">
        <p class="muted sidebar-user">{{ authStore.user?.display_name ?? authStore.user?.email }}</p>
        <button class="btn btn-ghost sidebar-logout" @click="handleLogout">{{ t("nav.signOut") }}</button>
        <div class="locale-toggle">
          <button
            class="locale-link"
            :class="{ 'locale-link-active': locale === 'zh-CN' }"
            @click="setLocale('zh-CN')"
          >中文</button>
          <span class="locale-sep">/</span>
          <button
            class="locale-link"
            :class="{ 'locale-link-active': locale === 'en' }"
            @click="setLocale('en')"
          >EN</button>
        </div>
      </div>
    </aside>
    <main class="content">
      <RouterView />
    </main>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from "vue-router";

import { useI18n } from "../../i18n";
import { useAuthStore } from "../../stores/auth";

const router = useRouter();
const authStore = useAuthStore();
const { t, locale, setLocale } = useI18n();

function handleLogout() {
  authStore.logout();
  router.push("/login");
}
</script>
