import { apiClient } from "./client";
import type { ContentType } from "../types";

export const dataSourcesApi = {
  list(params?: { starred?: boolean; content_type?: ContentType }) {
    return apiClient.get("/data-sources", { params });
  },
  create(payload: { url: string; note?: string; content_type?: ContentType; source_config?: Record<string, unknown> | null }) {
    return apiClient.post("/data-sources", payload);
  },
  patch(id: string, payload: { note?: string | null; category?: string | null; starred?: boolean; content_type?: ContentType; source_config?: Record<string, unknown> | null }) {
    return apiClient.patch(`/data-sources/${id}`, payload);
  },
  remove(id: string) {
    return apiClient.delete(`/data-sources/${id}`);
  },
};
