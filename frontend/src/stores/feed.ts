import { defineStore } from "pinia";
import { ref } from "vue";

import { videosApi } from "../api/videos";
import type { Video, VideoListResponse } from "../types";

function isVideoListResponse(data: Video[] | VideoListResponse): data is VideoListResponse {
  return !Array.isArray(data) && Array.isArray(data.items);
}

export const useFeedStore = defineStore("feed", () => {
  const videos = ref<Video[]>([]);
  const loading = ref(false);
  const error = ref<string | null>(null);

  async function fetchVideos() {
    loading.value = true;
    error.value = null;
    try {
      const resp = await videosApi.list();
      videos.value = isVideoListResponse(resp.data) ? resp.data.items : resp.data;
    } catch {
      error.value = "fetch_failed";
      videos.value = [];
    } finally {
      loading.value = false;
    }
  }

  return { videos, loading, error, fetchVideos };
});
