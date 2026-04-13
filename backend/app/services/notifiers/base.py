class BaseNotifier:
    async def send(self, message: str, webhook_url: str) -> None:
        raise NotImplementedError

