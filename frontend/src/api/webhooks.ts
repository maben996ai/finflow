import { apiClient } from "./client";

export interface FeishuWebhook {
  id: string;
  user_id: string;
  name: string;
  webhook_url: string;
  enabled: boolean;
  created_at: string;
}

export const webhooksApi = {
  list() {
    return apiClient.get<FeishuWebhook[]>("/webhooks/feishu");
  },
  create(payload: { name: string; webhook_url: string }) {
    return apiClient.post<FeishuWebhook>("/webhooks/feishu", payload);
  },
  update(id: string, payload: { name?: string; enabled?: boolean }) {
    return apiClient.put<FeishuWebhook>(`/webhooks/feishu/${id}`, payload);
  },
  delete(id: string) {
    return apiClient.delete(`/webhooks/feishu/${id}`);
  },
  test(id: string) {
    return apiClient.post(`/webhooks/feishu/${id}/test`);
  },
};
