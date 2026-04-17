import { createRouter, createWebHistory } from "vue-router";

import AppShell from "../components/layout/AppShell.vue";
import { useAuthStore } from "../stores/auth";
import CrawlLogsView from "../views/CrawlLogsView.vue";
import CreatorsView from "../views/CreatorsView.vue";
import FeedView from "../views/FeedView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import SettingsView from "../views/SettingsView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView, meta: { public: true } },
    { path: "/register", name: "register", component: RegisterView, meta: { public: true } },
    {
      path: "/",
      component: AppShell,
      children: [
        { path: "", name: "feed", component: FeedView },
        { path: "creators", name: "creators", component: CreatorsView },
        { path: "settings", name: "settings", component: SettingsView },
        { path: "crawl-logs", name: "crawl-logs", component: CrawlLogsView },
      ],
    },
  ],
});

router.beforeEach(async (to) => {
  const authStore = useAuthStore();

  if (authStore.isAuthenticated && !authStore.user) {
    await authStore.fetchUser();
  }

  if (!to.meta.public && !authStore.isAuthenticated) {
    return { name: "login" };
  }

  if (to.meta.public && authStore.isAuthenticated) {
    return { name: "feed" };
  }
});
