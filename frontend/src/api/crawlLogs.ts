import { apiClient } from "./client";

export const crawlLogsApi = {
  list() {
    return apiClient.get("/crawl-logs");
  },
};

