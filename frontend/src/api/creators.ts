import { apiClient } from "./client";
import type { ContentType } from "../types";

export const creatorsApi = {
  list(params?: { starred?: boolean; content_type?: ContentType }) {
    return apiClient.get("/creators", { params });
  },
  create(payload: { url: string; note?: string; content_type?: ContentType }) {
    return apiClient.post("/creators", payload);
  },
  patch(id: string, payload: { note?: string | null; category?: string | null; starred?: boolean; content_type?: ContentType }) {
    return apiClient.patch(`/creators/${id}`, payload);
  },
  remove(id: string) {
    return apiClient.delete(`/creators/${id}`);
  },
  crawl(id: string) {
    return apiClient.post(`/creators/${id}/crawl`);
  },
};
