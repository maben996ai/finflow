import { computed, ref, watch } from "vue";

export type Locale = "zh-CN" | "en";

const LOCALE_KEY = "finflow_locale";
const defaultLocale: Locale = "zh-CN";

const messages = {
  "zh-CN": {
    app: {
      localeLabel: "语言",
      switchToChinese: "切换到中文",
      switchToEnglish: "Switch to English",
    },
    nav: {
      product: "FinFlow",
      title: "投资信号驾驶舱",
      feed: "动态",
      creators: "创作者",
      settings: "设置",
      crawlLogs: "抓取日志",
      signOut: "退出登录",
    },
    feed: {
      eyebrow: "内容动态",
      title: "在同一时间线中追踪 Bilibili 与 YouTube 创作者更新。",
      filterAll: "全部",
      filterBilibili: "Bilibili",
      filterYoutube: "YouTube",
      loading: "加载中…",
      empty: "暂无视频，先去添加创作者并触发抓取吧。",
      fetchError: "加载失败，请稍后重试。",
    },
    creators: {
      eyebrow: "创作者",
      title: "创作者管理",
      addPlaceholder: "粘贴 Bilibili 或 YouTube 主页链接",
      addButton: "添加",
      adding: "添加中…",
      empty: "还没有订阅的创作者，粘贴主页链接开始添加。",
      loading: "加载中…",
      fetchError: "加载失败，请稍后重试。",
      addError: "添加失败，请检查链接格式或网络。",
      deleteConfirm: "确认删除该创作者？",
      notePlaceholder: "备注（可选）",
      categoryPlaceholder: "分类（可选）",
      save: "保存",
      cancel: "取消",
      starred: "特别关注",
      platformBilibili: "Bilibili",
      platformYoutube: "YouTube",
    },
    settings: {
      eyebrow: "设置",
      title: "飞书 Webhook 配置",
      description: "后端设置接口已经准备好，前端表单接入后即可完成配置。",
    },
    crawlLogs: {
      eyebrow: "抓取日志",
      title: "调度执行时间线",
      description: "任务接线完成后，这里会展示爬虫执行历史。",
    },
    auth: {
      loginEyebrow: "欢迎回来",
      loginTitle: "登录 FinFlow",
      registerEyebrow: "新建工作区",
      registerTitle: "创建你的账号",
      email: "邮箱",
      password: "密码",
      displayName: "显示名称",
      emailPlaceholder: "you@example.com",
      passwordPlaceholder: "••••••••",
      displayNamePlaceholder: "你的名字",
      registerPasswordPlaceholder: "至少 8 个字符",
      signIn: "登录",
      signingIn: "登录中…",
      createAccount: "创建账号",
      creatingAccount: "创建中…",
      noAccount: "还没有账号？",
      haveAccount: "已经有账号了？",
      createOne: "立即注册",
      signInLink: "去登录",
      loginFailed: "登录失败，请稍后重试。",
      registerFailed: "注册失败，请稍后重试。",
    },
  },
  en: {
    app: {
      localeLabel: "Language",
      switchToChinese: "切换到中文",
      switchToEnglish: "Switch to English",
    },
    nav: {
      product: "FinFlow",
      title: "Investor signal cockpit",
      feed: "Feed",
      creators: "Creators",
      settings: "Settings",
      crawlLogs: "Crawl Logs",
      signOut: "Sign out",
    },
    feed: {
      eyebrow: "Live Feed",
      title: "Track creators across Bilibili and YouTube in one timeline.",
      filterAll: "All",
      filterBilibili: "Bilibili",
      filterYoutube: "YouTube",
      loading: "Loading…",
      empty: "No videos yet. Add a creator and trigger a crawl first.",
      fetchError: "Failed to load. Please try again.",
    },
    creators: {
      eyebrow: "Creators",
      title: "Creators",
      addPlaceholder: "Paste a Bilibili or YouTube channel URL",
      addButton: "Add",
      adding: "Adding…",
      empty: "No creators yet. Paste a channel URL to get started.",
      loading: "Loading…",
      fetchError: "Failed to load. Please try again.",
      addError: "Failed to add. Check the URL format or your connection.",
      deleteConfirm: "Delete this creator?",
      notePlaceholder: "Note (optional)",
      categoryPlaceholder: "Category (optional)",
      save: "Save",
      cancel: "Cancel",
      starred: "Starred",
      platformBilibili: "Bilibili",
      platformYoutube: "YouTube",
    },
    settings: {
      eyebrow: "Settings",
      title: "Feishu webhook setup",
      description: "Settings APIs are initialized on the backend and waiting for frontend forms.",
    },
    crawlLogs: {
      eyebrow: "Crawl Logs",
      title: "Scheduler activity timeline",
      description: "Crawler execution history will be shown here after job wiring is added.",
    },
    auth: {
      loginEyebrow: "Welcome back",
      loginTitle: "Sign in to FinFlow",
      registerEyebrow: "New workspace",
      registerTitle: "Create your account",
      email: "Email",
      password: "Password",
      displayName: "Display name",
      emailPlaceholder: "you@example.com",
      passwordPlaceholder: "••••••••",
      displayNamePlaceholder: "Your name",
      registerPasswordPlaceholder: "At least 8 characters",
      signIn: "Sign in",
      signingIn: "Signing in…",
      createAccount: "Create account",
      creatingAccount: "Creating account…",
      noAccount: "Don't have an account?",
      haveAccount: "Already have an account?",
      createOne: "Create one",
      signInLink: "Sign in",
      loginFailed: "Login failed. Please try again.",
      registerFailed: "Registration failed. Please try again.",
    },
  },
} as const;

type MessageTree = typeof messages;
type MessageKey =
  | "app.localeLabel"
  | "app.switchToChinese"
  | "app.switchToEnglish"
  | "nav.product"
  | "nav.title"
  | "nav.feed"
  | "nav.creators"
  | "nav.settings"
  | "nav.crawlLogs"
  | "nav.signOut"
  | "feed.eyebrow"
  | "feed.title"
  | "feed.filterAll"
  | "feed.filterBilibili"
  | "feed.filterYoutube"
  | "feed.loading"
  | "feed.empty"
  | "feed.fetchError"
  | "creators.eyebrow"
  | "creators.title"
  | "creators.addPlaceholder"
  | "creators.addButton"
  | "creators.adding"
  | "creators.empty"
  | "creators.loading"
  | "creators.fetchError"
  | "creators.addError"
  | "creators.deleteConfirm"
  | "creators.notePlaceholder"
  | "creators.categoryPlaceholder"
  | "creators.save"
  | "creators.cancel"
  | "creators.starred"
  | "creators.platformBilibili"
  | "creators.platformYoutube"
  | "settings.eyebrow"
  | "settings.title"
  | "settings.description"
  | "crawlLogs.eyebrow"
  | "crawlLogs.title"
  | "crawlLogs.description"
  | "auth.loginEyebrow"
  | "auth.loginTitle"
  | "auth.registerEyebrow"
  | "auth.registerTitle"
  | "auth.email"
  | "auth.password"
  | "auth.displayName"
  | "auth.emailPlaceholder"
  | "auth.passwordPlaceholder"
  | "auth.displayNamePlaceholder"
  | "auth.registerPasswordPlaceholder"
  | "auth.signIn"
  | "auth.signingIn"
  | "auth.createAccount"
  | "auth.creatingAccount"
  | "auth.noAccount"
  | "auth.haveAccount"
  | "auth.createOne"
  | "auth.signInLink"
  | "auth.loginFailed"
  | "auth.registerFailed";

function loadInitialLocale(): Locale {
  const saved = localStorage.getItem(LOCALE_KEY);
  return saved === "zh-CN" || saved === "en" ? saved : defaultLocale;
}

const locale = ref<Locale>(loadInitialLocale());

watch(
  locale,
  (value) => {
    localStorage.setItem(LOCALE_KEY, value);
    document.documentElement.lang = value;
  },
  { immediate: true },
);

function getMessageValue(tree: MessageTree[Locale], key: MessageKey): string {
  return key.split(".").reduce((current, part) => current[part as keyof typeof current], tree as any) as string;
}

export function useI18n() {
  const currentLocale = computed(() => locale.value);

  function setLocale(value: Locale) {
    locale.value = value;
  }

  function toggleLocale() {
    locale.value = locale.value === "zh-CN" ? "en" : "zh-CN";
  }

  function t(key: MessageKey) {
    return getMessageValue(messages[locale.value], key);
  }

  return {
    locale: currentLocale,
    setLocale,
    toggleLocale,
    t,
  };
}
