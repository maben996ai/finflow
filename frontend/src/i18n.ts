import { computed, ref, watch } from "vue";

export type Locale = "zh-CN" | "en";

const LOCALE_KEY = "trendradar_locale";
const defaultLocale: Locale = "zh-CN";

const messages = {
  "zh-CN": {
    app: {
      localeLabel: "语言",
      switchToChinese: "切换到中文",
      switchToEnglish: "Switch to English",
    },
    nav: {
      product: "TrendRadar",
      title: "信号台",
      feed: "动态资讯",
      dataSources: "信源管理",
      settings: "设置",
      crawlLogs: "抓取日志",
      controlCenter: "控制中心",
      contentAnalysis: "内容分析",
      signOut: "退出登录",
    },
    feed: {
      eyebrow: "内容动态",
      title: "最新动态",
      sortByTime: "按时间",
      sortByAuthor: "按作者",
      loading: "加载中…",
      empty: "暂无视频，先去添加信源并触发抓取吧。",
      fetchError: "加载失败，请稍后重试。",
      prevPage: "上一页",
      nextPage: "下一页",
      tabVideos: "视频",
      tabArticles: "文章",
      tabNews: "资讯",
      tabMarket: "市场",
      viewAll: "查看全部",
      comingSoon: "即将上线，敬请期待",
      backToFeed: "← 返回动态",
    },
    dataSources: {
      eyebrow: "信源",
      title: "信源管理",
      addPlaceholder: "粘贴 Bilibili 或 YouTube 主页链接",
      addButton: "添加",
      adding: "添加中…",
      empty: "还没有订阅的信源，粘贴主页链接开始添加。",
      loading: "加载中…",
      fetchError: "加载失败，请稍后重试。",
      addError: "添加失败，请检查链接格式或网络。",
      initializing: "初始化中…",
      deleteConfirm: "确认删除该信源？",
      notePlaceholder: "备注（可选）",
      categoryPlaceholder: "分类（可选）",
      contentTypeLabel: "内容类型",
      editTitle: "编辑信源",
      save: "保存",
      cancel: "取消",
      starred: "特别关注",
      unstar: "取消特别关注",
      edit: "编辑",
      delete: "删除",
      tabVideos: "视频",
      tabArticles: "文章",
      tabNews: "资讯",
      tabMarket: "市场",
      comingSoon: "该板块即将上线",
      platformBilibili: "Bilibili",
      platformYoutube: "YouTube",
      platformWechat: "公众号",
      platformWebsite: "网站",
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
    contentAnalysis: {
      eyebrow: "内容分析",
      title: "内容分析",
      description: "基于大模型的视频内容分析与投研洞察，即将上线。",
    },
    auth: {
      loginEyebrow: "欢迎回来",
      loginTitle: "登录 TrendRadar",
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
      product: "TrendRadar",
      title: "Signal Desk",
      feed: "Latest Updates",
      dataSources: "Sources",
      settings: "Settings",
      crawlLogs: "Crawl Logs",
      controlCenter: "Control Center",
      contentAnalysis: "Content Analysis",
      signOut: "Sign out",
    },
    feed: {
      eyebrow: "Feed",
      title: "Latest Updates",
      sortByTime: "By Time",
      sortByAuthor: "By Author",
      loading: "Loading…",
      empty: "No videos yet. Add a source and trigger a crawl first.",
      fetchError: "Failed to load. Please try again.",
      prevPage: "Prev",
      nextPage: "Next",
      tabVideos: "Videos",
      tabArticles: "Articles",
      tabNews: "News",
      tabMarket: "Market",
      viewAll: "View all",
      comingSoon: "Coming soon",
      backToFeed: "← Back to Feed",
    },
    dataSources: {
      eyebrow: "Sources",
      title: "Source Management",
      addPlaceholder: "Paste a Bilibili or YouTube channel URL",
      addButton: "Add",
      adding: "Adding…",
      empty: "No sources yet. Paste a channel URL to get started.",
      loading: "Loading…",
      fetchError: "Failed to load. Please try again.",
      addError: "Failed to add. Check the URL format or your connection.",
      initializing: "Initializing…",
      deleteConfirm: "Delete this source?",
      notePlaceholder: "Note (optional)",
      categoryPlaceholder: "Category (optional)",
      contentTypeLabel: "Content type",
      editTitle: "Edit source",
      save: "Save",
      cancel: "Cancel",
      starred: "Star",
      unstar: "Unstar",
      edit: "Edit",
      delete: "Delete",
      tabVideos: "Videos",
      tabArticles: "Articles",
      tabNews: "News",
      tabMarket: "Market",
      comingSoon: "This section is coming soon",
      platformBilibili: "Bilibili",
      platformYoutube: "YouTube",
      platformWechat: "WeChat",
      platformWebsite: "Website",
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
    contentAnalysis: {
      eyebrow: "Content Analysis",
      title: "Content Analysis",
      description: "AI-powered content analysis and investment insights — coming soon.",
    },
    auth: {
      loginEyebrow: "Welcome back",
      loginTitle: "Sign in to TrendRadar",
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
  | "nav.dataSources"
  | "nav.settings"
  | "nav.crawlLogs"
  | "nav.controlCenter"
  | "nav.contentAnalysis"
  | "nav.signOut"
  | "feed.eyebrow"
  | "feed.title"
  | "feed.sortByTime"
  | "feed.sortByAuthor"
  | "feed.loading"
  | "feed.empty"
  | "feed.fetchError"
  | "feed.prevPage"
  | "feed.nextPage"
  | "feed.tabVideos"
  | "feed.tabArticles"
  | "feed.tabNews"
  | "feed.tabMarket"
  | "feed.viewAll"
  | "feed.comingSoon"
  | "feed.backToFeed"
  | "dataSources.eyebrow"
  | "dataSources.title"
  | "dataSources.addPlaceholder"
  | "dataSources.addButton"
  | "dataSources.adding"
  | "dataSources.empty"
  | "dataSources.loading"
  | "dataSources.fetchError"
  | "dataSources.addError"
  | "dataSources.initializing"
  | "dataSources.deleteConfirm"
  | "dataSources.notePlaceholder"
  | "dataSources.categoryPlaceholder"
  | "dataSources.contentTypeLabel"
  | "dataSources.editTitle"
  | "dataSources.save"
  | "dataSources.cancel"
  | "dataSources.starred"
  | "dataSources.unstar"
  | "dataSources.edit"
  | "dataSources.delete"
  | "dataSources.tabVideos"
  | "dataSources.tabArticles"
  | "dataSources.tabNews"
  | "dataSources.tabMarket"
  | "dataSources.comingSoon"
  | "dataSources.platformBilibili"
  | "dataSources.platformYoutube"
  | "dataSources.platformWechat"
  | "dataSources.platformWebsite"
  | "settings.eyebrow"
  | "settings.title"
  | "settings.description"
  | "crawlLogs.eyebrow"
  | "crawlLogs.title"
  | "crawlLogs.description"
  | "contentAnalysis.eyebrow"
  | "contentAnalysis.title"
  | "contentAnalysis.description"
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
