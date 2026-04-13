import { apiClient } from "./client";

export const settingsApi = {
  getFeishu() {
    return apiClient.get("/settings/feishu");
  },
  updateFeishu(payload: { feishu_webhook_url?: string | null }) {
    return apiClient.put("/settings/feishu", payload);
  },
};

