from .helpful_functions import get_as_questionable


class User:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.id = data["id"]
        self.username = data["username"]
        self.discriminator = data["discriminator"]
        self.isBot = get_as_questionable(data, "bot", False)

    async def send(self, content):
        await self.discordApi.create_dm(self.id, content)