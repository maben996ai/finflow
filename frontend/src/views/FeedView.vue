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
          <button class="filter-btn" :class="{ active: sortMode === 'author' }" @click="setSortMode('author')">{{ t("feed.sortByAuthor") }}</button>
          <button class="filter-btn" :class="{ active: sortMode === 'time' }" @click="setSortMode('time')">{{ t("feed.sortByTime") }}</button>
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
      <!-- 按作者分组：每页最多 4 个作者 -->
      <template v-if="sortMode === 'author'">
        <div class="panel author-groups-panel">
          <div class="author-groups-scroll">
            <div v-for="group in pagedAuthorGroups" :key="group.sourceId" class="author-group">
              <div class="author-group-header">
                <img v-if="group.avatarUrl" :src="group.avatarUrl" class="creator-avatar" :alt="group.sourceName" referrerpolicy="no-referrer" />
                <div v-else class="creator-avatar creator-avatar-placeholder" />
                <div class="author-group-title-row">
                  <RouterLink :to="`/source/${group.sourceId}`" class="author-group-name">{{ group.sourceName }}</RouterLink>
                  <span class="platform-badge author-inline-platform" :class="group.sourceType">{{ group.sourceType }}</span>
                </div>
                <RouterLink :to="`/source/${group.sourceId}`" class="author-view-all muted">
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
                    <div class="video-meta-sm">
                      <span class="muted">{{ formatPublishedAt(video.published_at) }}</span>
                      <span class="muted">{{ formatDuration(video.duration_seconds) }}</span>
                    </div>
                  </div>
                </a>
              </div>
            </div>

            <div v-if="canPaginateAuthors" class="pagination author-pagination">
              <button class="filter-btn" :disabled="page === 1 || feedStore.loadingMore" @click="page--">{{ t("feed.prevPage") }}</button>
              <span class="muted page-indicator">{{ authorPageLabel }}</span>
              <button class="filter-btn" :disabled="!canGoNextAuthor || feedStore.loadingMore" @click="goNextAuthorPage">{{ t("feed.nextPage") }}</button>
            </div>
          </div>
        </div>
      </template>

      <!-- 按时间排序：默认预加载 3 页，往后翻页时继续请求 -->
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
              <span class="platform-badge" :class="video.source_type">{{ video.source_type }}</span>
            </div>
            <div class="video-info-sm">
              <p class="video-title-sm">{{ video.title }}</p>
              <div class="video-meta-stack-sm">
                <span class="muted video-meta-line-sm">{{ video.data_source_name }}</span>
                <div class="video-meta-sm">
                  <span class="muted">{{ formatPublishedAt(video.published_at) }}</span>
                  <span class="muted">{{ formatDuration(video.duration_seconds) }}</span>
                </div>
              </div>
            </div>
          </a>
        </div>

        <div v-if="canPaginateTime" class="pagination">
          <button class="filter-btn" :disabled="page === 1 || feedStore.loadingMore" @click="page--">{{ t("feed.prevPage") }}</button>
          <span class="muted page-indicator">{{ timePageLabel }}</span>
          <button class="filter-btn" :disabled="!canGoNextTime || feedStore.loadingMore" @click="goNextTimePage">{{ t("feed.nextPage") }}</button>
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
import { formatPublishedAt } from "../utils/datetime";
import { formatDuration } from "../utils/duration";

const { t } = useI18n();
const feedStore = useFeedStore();

const VIDEO_PAGE_SIZE = 15;
const AUTHOR_PAGE_SIZE = 4;
const contentType = ref<"video" | "article" | "news" | "market">("video");
const sortMode = ref<"time" | "author">("author");
const page = ref(1);

const sortedByTime = computed(() =>
  [...feedStore.videos].sort(
    (a, b) => new Date(b.published_at).getTime() - new Date(a.published_at).getTime()
  )
);

const knownTimePages = computed(() => Math.max(1, Math.ceil(sortedByTime.value.length / VIDEO_PAGE_SIZE)));
const pagedVideos = computed(() => {
  const start = (page.value - 1) * VIDEO_PAGE_SIZE;
  return sortedByTime.value.slice(start, start + VIDEO_PAGE_SIZE);
});

interface AuthorGroup {
  sourceId: string;
  sourceName: string;
  avatarUrl: string | null | undefined;
  sourceType: string;
  videos: Video[];
}

const authorGroups = computed((): AuthorGroup[] => {
  const map = new Map<string, AuthorGroup>();
  for (const video of feedStore.videos) {
    if (!map.has(video.data_source_id)) {
      map.set(video.data_source_id, {
        sourceId: video.data_source_id,
        sourceName: video.data_source_name,
        avatarUrl: video.data_source_avatar_url,
        sourceType: video.source_type,
        videos: [],
      });
    }
    map.get(video.data_source_id)!.videos.push(video);
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

const knownAuthorPages = computed(() => Math.max(1, Math.ceil(authorGroups.value.length / AUTHOR_PAGE_SIZE)));
const pagedAuthorGroups = computed(() => {
  const start = (page.value - 1) * AUTHOR_PAGE_SIZE;
  return authorGroups.value.slice(start, start + AUTHOR_PAGE_SIZE);
});

const canGoNextTime = computed(() => page.value < knownTimePages.value || feedStore.hasMore);
const canGoNextAuthor = computed(() => page.value < knownAuthorPages.value || feedStore.hasMore);
const canPaginateTime = computed(() => knownTimePages.value > 1 || feedStore.hasMore);
const canPaginateAuthors = computed(() => knownAuthorPages.value > 1 || feedStore.hasMore);
const timePageLabel = computed(() =>
  feedStore.hasMore ? `${page.value} / ${knownTimePages.value}+` : `${page.value} / ${knownTimePages.value}`
);
const authorPageLabel = computed(() =>
  feedStore.hasMore ? `${page.value} / ${knownAuthorPages.value}+` : `${page.value} / ${knownAuthorPages.value}`
);

function setContentType(type: typeof contentType.value) {
  contentType.value = type;
  page.value = 1;
}

function setSortMode(mode: "time" | "author") {
  sortMode.value = mode;
  page.value = 1;
}

async function ensureTimePageLoaded(targetPage: number) {
  await feedStore.ensureVideoCount(targetPage * VIDEO_PAGE_SIZE);
}

async function ensureAuthorPageLoaded(targetPage: number) {
  const requiredAuthors = targetPage * AUTHOR_PAGE_SIZE;
  while (authorGroups.value.length < requiredAuthors && feedStore.hasMore) {
    await feedStore.fetchNextPage();
  }
}

async function ensureCurrentPageLoaded() {
  if (contentType.value !== "video") return;
  if (sortMode.value === "author") {
    await ensureAuthorPageLoaded(page.value);
    return;
  }
  await ensureTimePageLoaded(page.value);
}

async function goNextTimePage() {
  const nextPage = page.value + 1;
  await ensureTimePageLoaded(nextPage);
  if (nextPage <= knownTimePages.value || feedStore.hasMore || sortedByTime.value.length >= nextPage * VIDEO_PAGE_SIZE) {
    page.value = nextPage;
  }
}

async function goNextAuthorPage() {
  const nextPage = page.value + 1;
  await ensureAuthorPageLoaded(nextPage);
  if (nextPage <= knownAuthorPages.value || feedStore.hasMore || authorGroups.value.length >= nextPage * AUTHOR_PAGE_SIZE) {
    page.value = nextPage;
  }
}

watch([contentType, sortMode], () => {
  page.value = 1;
  void ensureCurrentPageLoaded();
});

watch(page, () => {
  void ensureCurrentPageLoaded();
});

onMounted(async () => {
  await feedStore.fetchVideos(3);
  await ensureCurrentPageLoaded();
});
</script>
