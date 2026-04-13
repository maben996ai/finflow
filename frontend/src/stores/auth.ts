import { defineStore } from "pinia";
import { ref } from "vue";

export const useAuthStore = defineStore("auth", () => {
  const token = ref<string | null>(null);

  function setToken(value: string | null) {
    token.value = value;
  }

  return {
    token,
    setToken,
  };
});

