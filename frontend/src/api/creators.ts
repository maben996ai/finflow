import { apiClient } from "./client";

export const creatorsApi = {
  list() {
    return apiClient.get("/creators");
  },
  create(payload: { url: string; note?: string }) {
    return apiClient.post("/creators", payload);
  },
  remove(id: string) {
    return apiClient.delete(`/creators/${id}`);
  },
};

