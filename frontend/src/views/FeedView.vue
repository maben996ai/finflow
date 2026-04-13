<template>
  <section class="stack">
    <div class="hero">
      <div>
        <p class="eyebrow">Live Feed</p>
        <h2>Track creators across Bilibili and YouTube in one timeline.</h2>
      </div>
      <span class="status-pill">Bootstrap state</span>
    </div>

    <div class="grid">
      <article class="panel card" v-for="item in cards" :key="item.title">
        <p class="card-platform">{{ item.platform }}</p>
        <h3>{{ item.title }}</h3>
        <p class="muted">{{ item.description }}</p>
      </article>
    </div>
  </section>
</template>

<script setup lang="ts">
const cards = [
  {
    platform: "Bilibili",
    title: "Unified video feed",
    description: "Video cards, timeline sorting and platform filtering will land here.",
  },
  {
    platform: "YouTube",
    title: "Notification-ready workflow",
    description: "Feishu settings and crawl automation are scaffolded on the backend.",
  },
  {
    platform: "System",
    title: "Composable architecture",
    description: "This page is wired through Vue Router and ready for API-backed stores.",
  },
];
</script>

