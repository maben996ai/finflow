import { apiClient } from "./client";

export const authApi = {
  login(payload: { email: string; password: string }) {
    return apiClient.post("/auth/login", payload);
  },
  register(payload: { email: string; password: string; display_name?: string }) {
    return apiClient.post("/auth/register", payload);
  },
};

