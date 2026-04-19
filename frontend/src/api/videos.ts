import { apiClient } from "./client";
import type { Video, VideoListResponse } from "../types";

export const videosApi = {
  list(platform?: "bilibili" | "youtube") {
    const params = platform ? { platform } : {};
    return apiClient.get<Video[] | VideoListResponse>("/videos", { params });
  },
};
