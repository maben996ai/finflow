export type ContentType = "video" | "article" | "news" | "market";

export interface Creator {
  id: string;
  name: string;
  platform: "bilibili" | "youtube";
  platform_creator_id: string;
  profile_url: string;
  avatar_url?: string | null;
  note?: string | null;
  category?: string | null;
  content_type: ContentType;
  starred: boolean;
  notifications_enabled: boolean;
  created_at: string;
}

export interface Video {
  id: string;
  creator_id: string;
  platform_video_id: string;
  platform: "bilibili" | "youtube";
  title: string;
  thumbnail_url?: string | null;
  video_url: string;
  published_at: string;
  creator_name: string;
  creator_avatar_url?: string | null;
}

