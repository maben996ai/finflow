import { apiClient } from "./client";

export const videosApi = {
  list(platform?: "bilibili" | "youtube") {
    const params = platform ? { platform } : {};
    return apiClient.get("/videos", { params });
  },
};
