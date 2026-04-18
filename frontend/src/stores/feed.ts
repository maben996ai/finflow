import { defineStore } from "pinia";
import { ref } from "vue";

import { videosApi } from "../api/videos";
import type { Video } from "../types";

export const useFeedStore = defineStore("feed", () => {
  const videos = ref<Video[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);
  const platformFilter = ref<"all" | "bilibili" | "youtube">("all");

  async function fetchVideos() {
    loading.value = true;
    error.value = null;
    try {
      const platform = platformFilter.value === "all" ? undefined : platformFilter.value;
      const resp = await videosApi.list(platform);
      videos.value = resp.data;
    } catch {
      error.value = "fetch_failed";
    } finally {
      loading.value = false;
    }
  }

  async function setPlatformFilter(value: "all" | "bilibili" | "youtube") {
    platformFilter.value = value;
    await fetchVideos();
  }

  return {
    videos,
    loading,
    error,
    platformFilter,
    fetchVideos,
    setPlatformFilter,
  };
});
