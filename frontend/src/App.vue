<template>
  <div class="app-frame">
    <RouterView />
  </div>
</template>

<script setup lang="ts">
import { useI18n } from "./i18n";

const { locale, setLocale, t } = useI18n();
</script>
