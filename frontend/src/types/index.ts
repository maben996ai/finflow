export interface Creator {
  id: string;
  name: string;
  platform: "bilibili" | "youtube";
  profile_url: string;
  avatar_url?: string | null;
  note?: string | null;
}

export interface Video {
  id: string;
  creator_id: string;
  title: string;
  thumbnail_url?: string | null;
  video_url: string;
  published_at: string;
}

