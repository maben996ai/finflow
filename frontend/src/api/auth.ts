import { apiClient } from "./client";

export const authApi = {
  login(payload: { email: string; password: string }) {
    return apiClient.post<{ access_token: string; token_type: string }>("/auth/login", payload);
  },
  register(payload: { email: string; password: string; display_name?: string }) {
    return apiClient.post<{ id: string; email: string; display_name: string }>("/auth/register", payload);
  },
  me() {
    return apiClient.get<{ id: string; email: string; display_name: string }>("/auth/me");
  },
};
