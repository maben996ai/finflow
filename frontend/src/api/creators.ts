import { apiClient } from "./client";

export const creatorsApi = {
  list(params?: { starred?: boolean }) {
    return apiClient.get("/creators", { params });
  },
  create(payload: { url: string; note?: string }) {
    return apiClient.post("/creators", payload);
  },
  patch(id: string, payload: { note?: string | null; category?: string | null; starred?: boolean }) {
    return apiClient.patch(`/creators/${id}`, payload);
  },
  remove(id: string) {
    return apiClient.delete(`/creators/${id}`);
  },
  crawl(id: string) {
    return apiClient.post(`/creators/${id}/crawl`);
  },
};
