import { defineStore } from "pinia";
import { ref } from "vue";

export const useFeedStore = defineStore("feed", () => {
  const platformFilter = ref<"all" | "bilibili" | "youtube">("all");

  function setPlatformFilter(value: "all" | "bilibili" | "youtube") {
    platformFilter.value = value;
  }

  return {
    platformFilter,
    setPlatformFilter,
  };
});

