import { apiClient } from "./client";

export const videosApi = {
  list() {
    return apiClient.get("/videos");
  },
};

