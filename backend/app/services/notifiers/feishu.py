import httpx

from app.services.notifiers.base import BaseNotifier


class FeishuNotifier(BaseNotifier):
    async def send(self, message: str, webhook_url: str) -> None:
        if not webhook_url:
            return
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                webhook_url,
                json={"msg_type": "text", "content": {"text": message}},
            )

    async def send_card(
        self,
        webhook_url: str,
        title: str,
        creator_name: str,
        platform: str,
        video_url: str,
        thumbnail_url: str | None = None,
        is_new_creator: bool = False,
    ) -> None:
        if not webhook_url:
            return

        header_title = f"🆕 新增信源：{creator_name}" if is_new_creator else f"📹 新视频：{creator_name}"
        platform_label = "Bilibili" if platform == "bilibili" else "YouTube"

        # 标题做成可点击链接，附带封面地址（飞书 webhook 不支持外链图片，需要 img_key）
        title_md = f"**[{title}]({video_url})**"
        if thumbnail_url:
            title_md += f"\n\n🖼 [封面预览]({thumbnail_url})"

        elements: list[dict] = [
            {
                "tag": "div",
                "text": {"tag": "lark_md", "content": title_md},
            },
            {
                "tag": "div",
                "fields": [
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**平台**\n{platform_label}"}},
                    {"is_short": True, "text": {"tag": "lark_md", "content": f"**创作者**\n{creator_name}"}},
                ],
            },
            {"tag": "hr"},
            {
                "tag": "action",
                "actions": [
                    {
                        "tag": "button",
                        "text": {"tag": "plain_text", "content": "▶ 观看视频"},
                        "type": "primary",
                        "url": video_url,
                    }
                ],
            },
        ]

        card = {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": header_title},
                "template": "blue" if is_new_creator else "green",
            },
            "elements": elements,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(webhook_url, json={"msg_type": "interactive", "card": card})
