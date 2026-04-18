<template>
  <section class="stack">
    <div class="hero">
      <div>
        <p class="eyebrow">{{ t("feed.eyebrow") }}</p>
        <h2>{{ t("feed.title") }}</h2>
      </div>
      <div class="feed-filters">
        <button
          v-for="f in filters"
          :key="f.value"
          class="filter-btn"
          :class="{ active: feedStore.platformFilter === f.value }"
          @click="feedStore.setPlatformFilter(f.value)"
        >
          {{ f.label }}
        </button>
      </div>
    </div>

    <p v-if="feedStore.loading" class="muted feed-state">{{ t("feed.loading") }}</p>
    <p v-else-if="feedStore.error" class="error-msg feed-state">{{ t("feed.fetchError") }}</p>
    <p v-else-if="feedStore.videos.length === 0" class="muted feed-state">{{ t("feed.empty") }}</p>

    <div v-else class="video-grid">
      <a
        v-for="video in feedStore.videos"
        :key="video.id"
        :href="video.video_url"
        target="_blank"
        rel="noopener noreferrer"
        class="video-card"
      >
        <div class="video-thumb">
          <img v-if="video.thumbnail_url" :src="video.thumbnail_url" :alt="video.title" loading="lazy" />
          <div v-else class="video-thumb-placeholder" />
          <span class="platform-badge" :class="video.platform">{{ video.platform }}</span>
        </div>
        <div class="video-info">
          <p class="video-title">{{ video.title }}</p>
          <div class="video-meta">
            <img
              v-if="video.creator_avatar_url"
              :src="video.creator_avatar_url"
              class="creator-avatar"
              :alt="video.creator_name"
            />
            <span class="muted video-creator">{{ video.creator_name }}</span>
            <span class="muted video-date">{{ formatDate(video.published_at) }}</span>
          </div>
        </div>
      </a>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted } from "vue";

import { useI18n } from "../i18n";
import { useFeedStore } from "../stores/feed";

const { t } = useI18n();
const feedStore = useFeedStore();

const filters = [
  { value: "all" as const, label: t("feed.filterAll") },
  { value: "bilibili" as const, label: t("feed.filterBilibili") },
  { value: "youtube" as const, label: t("feed.filterYoutube") },
];

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric", year: "numeric" });
}

onMounted(() => {
  feedStore.fetchVideos();
});
</script>
