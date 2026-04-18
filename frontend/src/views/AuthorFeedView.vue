<template>
  <section class="stack">
    <div class="hero">
      <div class="author-hero-info">
        <RouterLink to="/" class="back-link">{{ t("feed.backToFeed") }}</RouterLink>
        <div class="author-hero-identity">
          <img v-if="authorAvatar" :src="authorAvatar" class="creator-avatar-lg" :alt="authorName" referrerpolicy="no-referrer" />
          <div v-else class="creator-avatar-lg creator-avatar-placeholder" />
          <div>
            <p class="eyebrow">{{ authorPlatform }}</p>
            <h2>{{ authorName }}</h2>
          </div>
        </div>
      </div>
    </div>

    <p v-if="feedStore.loading" class="muted feed-state">{{ t("feed.loading") }}</p>
    <p v-else-if="!authorVideos.length" class="muted feed-state">{{ t("feed.empty") }}</p>

    <template v-else>
      <div class="video-grid-sm">
        <a
          v-for="video in pagedVideos"
          :key="video.id"
          :href="video.video_url"
          target="_blank"
          rel="noopener noreferrer"
          class="video-card-sm"
        >
          <div class="video-thumb-sm">
            <img v-if="video.thumbnail_url" :src="video.thumbnail_url" :alt="video.title" loading="lazy" referrerpolicy="no-referrer" />
            <div v-else class="video-thumb-placeholder" />
            <span class="platform-badge" :class="video.platform">{{ video.platform }}</span>
          </div>
          <div class="video-info-sm">
            <p class="video-title-sm">{{ video.title }}</p>
            <span class="muted video-meta-sm">{{ formatDate(video.published_at) }}</span>
          </div>
        </a>
      </div>

      <div v-if="totalPages > 1" class="pagination">
        <button class="filter-btn" :disabled="page === 1" @click="page--">{{ t("feed.prevPage") }}</button>
        <span class="muted page-indicator">{{ page }} / {{ totalPages }}</span>
        <button class="filter-btn" :disabled="page === totalPages" @click="page++">{{ t("feed.nextPage") }}</button>
      </div>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from "vue";
import { RouterLink, useRoute } from "vue-router";

import { useI18n } from "../i18n";
import { useFeedStore } from "../stores/feed";

const { t } = useI18n();
const route = useRoute();
const feedStore = useFeedStore();

const PAGE_SIZE = 15;
const page = ref(1);

const creatorId = computed(() => route.params.creatorId as string);

const authorVideos = computed(() =>
  feedStore.videos
    .filter((v) => v.creator_id === creatorId.value)
    .sort((a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime())
);

const authorName = computed(() => authorVideos.value[0]?.creator_name ?? "");
const authorAvatar = computed(() => authorVideos.value[0]?.creator_avatar_url ?? null);
const authorPlatform = computed(() => authorVideos.value[0]?.platform ?? "");

const totalPages = computed(() => Math.max(1, Math.ceil(authorVideos.value.length / PAGE_SIZE)));
const pagedVideos = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return authorVideos.value.slice(start, start + PAGE_SIZE);
});

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

onMounted(() => {
  if (!feedStore.videos.length) feedStore.fetchVideos();
});
</script>
