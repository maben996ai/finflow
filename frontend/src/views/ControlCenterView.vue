<template>
  <section class="stack">
    <div class="panel">
      <p class="eyebrow">通知配置</p>
      <h2>飞书 Webhook</h2>
      <p class="muted">配置飞书群机器人 Webhook 地址，抓取到新内容时自动推送通知。</p>

      <el-form :model="form" label-position="top" style="margin-top: 16px; max-width: 560px">
        <el-form-item label="Webhook 地址">
          <el-input
            v-model="form.feishu_webhook_url"
            placeholder="https://open.feishu.cn/open-apis/bot/v2/hook/..."
            clearable
          />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" :loading="saving" @click="save">保存</el-button>
          <el-button :loading="testing" @click="test" style="margin-left: 8px">发送测试消息</el-button>
        </el-form-item>
      </el-form>
    </div>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import { ElMessage } from "element-plus";
import { settingsApi } from "../api/settings";

const form = ref({ feishu_webhook_url: "" });
const saving = ref(false);
const testing = ref(false);

onMounted(async () => {
  try {
    const res = await settingsApi.getFeishu();
    form.value.feishu_webhook_url = res.data.feishu_webhook_url ?? "";
  } catch {
    // ignore
  }
});

async function save() {
  saving.value = true;
  try {
    await settingsApi.updateFeishu({ feishu_webhook_url: form.value.feishu_webhook_url || null });
    ElMessage.success("保存成功");
  } catch {
    ElMessage.error("保存失败");
  } finally {
    saving.value = false;
  }
}

async function test() {
  if (!form.value.feishu_webhook_url) {
    ElMessage.warning("请先填写 Webhook 地址");
    return;
  }
  testing.value = true;
  try {
    await settingsApi.testFeishu();
    ElMessage.success("测试消息已发送，请查看飞书群");
  } catch {
    ElMessage.error("发送失败，请检查 Webhook 地址是否正确");
  } finally {
    testing.value = false;
  }
}
</script>
