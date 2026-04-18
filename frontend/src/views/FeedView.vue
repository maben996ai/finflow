<template>
  <section class="stack">
    <div class="hero">
      <div>
        <p class="eyebrow">{{ t("feed.eyebrow") }}</p>
        <h2>{{ t("feed.title") }}</h2>
      </div>
      <div class="hero-controls">
        <div class="feed-filters">
          <button class="filter-btn" :class="{ active: contentType === 'video' }" @click="setContentType('video')">{{ t("feed.tabVideos") }}</button>
          <button class="filter-btn" :class="{ active: contentType === 'article' }" @click="setContentType('article')">{{ t("feed.tabArticles") }}</button>
          <button class="filter-btn" :class="{ active: contentType === 'news' }" @click="setContentType('news')">{{ t("feed.tabNews") }}</button>
          <button class="filter-btn" :class="{ active: contentType === 'market' }" @click="setContentType('market')">{{ t("feed.tabMarket") }}</button>
        </div>
        <div class="feed-filters">
          <button class="filter-btn" :class="{ active: sortMode === 'time' }" @click="setSortMode('time')">{{ t("feed.sortByTime") }}</button>
          <button class="filter-btn" :class="{ active: sortMode === 'author' }" @click="setSortMode('author')">{{ t("feed.sortByAuthor") }}</button>
        </div>
      </div>
    </div>

    <p v-if="feedStore.loading" class="muted feed-state">{{ t("feed.loading") }}</p>
    <p v-else-if="feedStore.error" class="error-msg feed-state">{{ t("feed.fetchError") }}</p>

    <template v-else-if="contentType !== 'video'">
      <div class="panel feed-state">
        <p class="muted">{{ t("feed.comingSoon") }}</p>
      </div>
    </template>

    <template v-else-if="feedStore.videos.length === 0">
      <p class="muted feed-state">{{ t("feed.empty") }}</p>
    </template>

    <template v-else>
      <!-- 按时间排序：分页平铺 -->
      <template v-if="sortMode === 'time'">
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
              <div class="video-meta-sm">
                <span class="muted">{{ video.creator_name }}</span>
                <span class="muted">{{ formatDate(video.published_at) }}</span>
              </div>
            </div>
          </a>
        </div>

        <div v-if="totalPages > 1" class="pagination">
          <button class="filter-btn" :disabled="page === 1" @click="page--">{{ t("feed.prevPage") }}</button>
          <span class="muted page-indicator">{{ page }} / {{ totalPages }}</span>
          <button class="filter-btn" :disabled="page === totalPages" @click="page++">{{ t("feed.nextPage") }}</button>
        </div>
      </template>

      <!-- 按作者分组：每组最多展示前 5 条，点击作者进入详情页 -->
      <template v-else>
        <div v-for="group in authorGroups" :key="group.creatorId" class="author-group">
          <div class="author-group-header">
            <img v-if="group.avatarUrl" :src="group.avatarUrl" class="creator-avatar" :alt="group.creatorName" referrerpolicy="no-referrer" />
            <div v-else class="creator-avatar creator-avatar-placeholder" />
            <RouterLink :to="`/author/${group.creatorId}`" class="author-group-name">{{ group.creatorName }}</RouterLink>
            <span class="platform-badge" :class="group.platform">{{ group.platform }}</span>
            <RouterLink :to="`/author/${group.creatorId}`" class="author-view-all muted">
              {{ t("feed.viewAll") }} {{ group.videos.length }} →
            </RouterLink>
          </div>
          <div class="video-grid-sm">
            <a
              v-for="video in group.videos.slice(0, 5)"
              :key="video.id"
              :href="video.video_url"
              target="_blank"
              rel="noopener noreferrer"
              class="video-card-sm"
            >
              <div class="video-thumb-sm">
                <img v-if="video.thumbnail_url" :src="video.thumbnail_url" :alt="video.title" loading="lazy" referrerpolicy="no-referrer" />
                <div v-else class="video-thumb-placeholder" />
              </div>
              <div class="video-info-sm">
                <p class="video-title-sm">{{ video.title }}</p>
                <span class="muted video-meta-sm">{{ formatDate(video.published_at) }}</span>
              </div>
            </a>
          </div>
        </div>
      </template>
    </template>
  </section>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from "vue";
import { RouterLink } from "vue-router";

import { useI18n } from "../i18n";
import { useFeedStore } from "../stores/feed";
import type { Video } from "../types";

const { t } = useI18n();
const feedStore = useFeedStore();

const PAGE_SIZE = 15;
const contentType = ref<"video" | "article" | "news" | "market">("video");
const sortMode = ref<"time" | "author">("time");
const page = ref(1);

const sortedByTime = computed(() =>
  [...feedStore.videos].sort(
    (a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime()
  )
);

const totalPages = computed(() => Math.max(1, Math.ceil(sortedByTime.value.length / PAGE_SIZE)));
const pagedVideos = computed(() => {
  const start = (page.value - 1) * PAGE_SIZE;
  return sortedByTime.value.slice(start, start + PAGE_SIZE);
});

interface AuthorGroup {
  creatorId: string;
  creatorName: string;
  avatarUrl: string | null | undefined;
  platform: "bilibili" | "youtube";
  videos: Video[];
}

const authorGroups = computed((): AuthorGroup[] => {
  const map = new Map<string, AuthorGroup>();
  for (const video of feedStore.videos) {
    if (!map.has(video.creator_id)) {
      map.set(video.creator_id, {
        creatorId: video.creator_id,
        creatorName: video.creator_name,
        avatarUrl: video.creator_avatar_url,
        platform: video.platform,
        videos: [],
      });
    }
    map.get(video.creator_id)!.videos.push(video);
  }
  for (const group of map.values()) {
    group.videos.sort(
      (a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime()
    );
  }
  return [...map.values()].sort(
    (a, b) =>
      new Date(b.videos[0].published_at).getTime() -
      new Date(a.videos[0].published_at).getTime()
  );
});

function setContentType(type: typeof contentType.value) {
  contentType.value = type;
  page.value = 1;
}

function setSortMode(mode: "time" | "author") {
  sortMode.value = mode;
  page.value = 1;
}

watch([contentType, sortMode], () => { page.value = 1; });

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

onMounted(() => feedStore.fetchVideos());
</script>
