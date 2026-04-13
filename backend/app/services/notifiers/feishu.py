import httpx

from app.services.notifiers.base import BaseNotifier


class FeishuNotifier(BaseNotifier):
    async def send(self, message: str, webhook_url: str) -> None:
        if not webhook_url:
            return

        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                webhook_url,
                json={
                    "msg_type": "text",
                    "content": {"text": message},
                },
            )
