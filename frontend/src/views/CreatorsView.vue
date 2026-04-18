<template>
  <section class="stack">
    <!-- 头部 + tab -->
    <div class="hero">
      <div>
        <p class="eyebrow">{{ t("creators.eyebrow") }}</p>
        <h2>{{ t("creators.title") }}</h2>
      </div>
      <div class="feed-filters">
        <button class="filter-btn" :class="{ active: contentType === 'video' }" @click="switchTab('video')">{{ t("creators.tabVideos") }}</button>
        <button class="filter-btn" :class="{ active: contentType === 'article' }" @click="switchTab('article')">{{ t("creators.tabArticles") }}</button>
        <button class="filter-btn" :class="{ active: contentType === 'news' }" @click="switchTab('news')">{{ t("creators.tabNews") }}</button>
        <button class="filter-btn" :class="{ active: contentType === 'market' }" @click="switchTab('market')">{{ t("creators.tabMarket") }}</button>
      </div>
    </div>

    <!-- 新增表单（news / market 暂不支持 URL 解析，显示提示） -->
    <div class="panel add-form">
      <template v-if="contentType === 'news' || contentType === 'market'">
        <p class="muted">{{ t("creators.comingSoon") }}</p>
      </template>
      <template v-else>
        <form class="add-row" @submit.prevent="handleAdd">
          <input
            v-model="addUrl"
            class="add-input"
            type="url"
            :placeholder="t('creators.addPlaceholder')"
            :disabled="adding"
            required
          />
          <button class="btn" type="submit" :disabled="adding || !addUrl.trim()">
            {{ adding ? t("creators.adding") : t("creators.addButton") }}
          </button>
        </form>
        <p v-if="addError" class="error-msg">{{ t("creators.addError") }}</p>
      </template>
    </div>

    <!-- 列表 -->
    <p v-if="loading" class="muted feed-state">{{ t("creators.loading") }}</p>
    <p v-else-if="fetchError" class="error-msg feed-state">{{ t("creators.fetchError") }}</p>
    <p v-else-if="creators.length === 0" class="muted feed-state">{{ t("creators.empty") }}</p>

    <div v-else class="creator-list">
      <div v-for="c in creators" :key="c.id" class="creator-row panel">
        <img v-if="c.avatar_url" :src="c.avatar_url" class="creator-row-avatar" :alt="c.name" referrerpolicy="no-referrer" />
        <div v-else class="creator-row-avatar creator-row-avatar-placeholder" />

        <div class="creator-row-info">
          <div class="creator-row-name-line">
            <a :href="c.profile_url" target="_blank" rel="noopener noreferrer" class="creator-row-name">
              {{ c.name }}
            </a>
            <span class="platform-badge" :class="c.platform">
              {{ c.platform === "bilibili" ? t("creators.platformBilibili") : t("creators.platformYoutube") }}
            </span>
            <span v-if="c.starred" class="starred-badge">★</span>
            <span v-if="c.category" class="category-tag">{{ c.category }}</span>
          </div>
          <p v-if="c.note" class="muted creator-row-note">{{ c.note }}</p>
        </div>

        <div class="creator-row-actions">
          <button class="btn-icon" :title="c.starred ? '取消特别关注' : '特别关注'" @click="toggleStar(c)">
            {{ c.starred ? "★" : "☆" }}
          </button>
          <button class="btn-icon edit-btn" title="编辑" @click="startEdit(c)">✎</button>
          <button class="btn-icon delete-btn" title="删除" @click="handleDelete(c.id)">✕</button>
        </div>
      </div>
    </div>

    <!-- 编辑弹层 -->
    <div v-if="editTarget" class="modal-backdrop" @click.self="editTarget = null">
      <div class="modal panel">
        <h3>编辑创作者</h3>
        <div class="form">
          <div class="field">
            <label>{{ t("creators.notePlaceholder") }}</label>
            <input v-model="editNote" type="text" :placeholder="t('creators.notePlaceholder')" />
          </div>
          <div class="field">
            <label>{{ t("creators.categoryPlaceholder") }}</label>
            <input v-model="editCategory" type="text" :placeholder="t('creators.categoryPlaceholder')" />
          </div>
          <div class="field">
            <label>内容类型</label>
            <select v-model="editContentType">
              <option value="video">视频</option>
              <option value="article">文章</option>
              <option value="news">资讯</option>
              <option value="market">市场</option>
            </select>
          </div>
          <div class="modal-actions">
            <button class="btn" @click="submitEdit">{{ t("creators.save") }}</button>
            <button class="btn btn-ghost" @click="editTarget = null">{{ t("creators.cancel") }}</button>
          </div>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";

import { creatorsApi } from "../api/creators";
import { useI18n } from "../i18n";
import type { ContentType, Creator } from "../types";

const { t } = useI18n();

const contentType = ref<ContentType>("video");
const creators = ref<Creator[]>([]);
const loading = ref(false);
const fetchError = ref(false);

const addUrl = ref("");
const adding = ref(false);
const addError = ref(false);

const editTarget = ref<Creator | null>(null);
const editNote = ref("");
const editCategory = ref("");
const editContentType = ref<ContentType>("video");

async function fetchCreators() {
  loading.value = true;
  fetchError.value = false;
  try {
    const resp = await creatorsApi.list({ content_type: contentType.value });
    creators.value = resp.data;
  } catch {
    fetchError.value = true;
  } finally {
    loading.value = false;
  }
}

function switchTab(tab: ContentType) {
  contentType.value = tab;
  fetchCreators();
}

async function handleAdd() {
  addError.value = false;
  adding.value = true;
  try {
    const resp = await creatorsApi.create({ url: addUrl.value.trim(), content_type: contentType.value });
    creators.value.unshift(resp.data);
    addUrl.value = "";
  } catch {
    addError.value = true;
  } finally {
    adding.value = false;
  }
}

async function handleDelete(id: string) {
  if (!confirm(t("creators.deleteConfirm"))) return;
  await creatorsApi.remove(id);
  creators.value = creators.value.filter((c) => c.id !== id);
}

async function toggleStar(creator: Creator) {
  const resp = await creatorsApi.patch(creator.id, { starred: !creator.starred });
  const idx = creators.value.findIndex((c) => c.id === creator.id);
  if (idx !== -1) creators.value[idx] = resp.data;
}

function startEdit(creator: Creator) {
  editTarget.value = creator;
  editNote.value = creator.note ?? "";
  editCategory.value = creator.category ?? "";
  editContentType.value = creator.content_type;
}

async function submitEdit() {
  if (!editTarget.value) return;
  const resp = await creatorsApi.patch(editTarget.value.id, {
    note: editNote.value || null,
    category: editCategory.value || null,
    content_type: editContentType.value,
  });
  const idx = creators.value.findIndex((c) => c.id === editTarget.value!.id);
  if (idx !== -1) creators.value[idx] = resp.data;
  editTarget.value = null;
  // 如果类型改变了，从当前 tab 的列表中移除
  if (resp.data.content_type !== contentType.value) {
    creators.value = creators.value.filter((c) => c.id !== resp.data.id);
  }
}

onMounted(fetchCreators);
</script>
