import { createRouter, createWebHistory } from "vue-router";

import AppShell from "../components/layout/AppShell.vue";
import CrawlLogsView from "../views/CrawlLogsView.vue";
import CreatorsView from "../views/CreatorsView.vue";
import FeedView from "../views/FeedView.vue";
import LoginView from "../views/LoginView.vue";
import RegisterView from "../views/RegisterView.vue";
import SettingsView from "../views/SettingsView.vue";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: "/login", name: "login", component: LoginView },
    { path: "/register", name: "register", component: RegisterView },
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
