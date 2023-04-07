from .helpful_functions import get_as_questionable
from .role import Role
from .emoji import Emoji


class Guild:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.id = data["id"]
        self.name = data["name"]
        self.icon = data["icon"]
        self.icon_hash = get_as_questionable(data, "icon_hash")
        self.splash = data["splash"]
        self.discovery_splash = data["discovery_splash"]
        self.owner_id = data["owner_id"]
        self.verification_level = data["verification_level"]
        self.roles = [Role(discordApi, dt) for dt in data["roles"]]
        self.emojis = [Emoji(discordApi, dt) for dt in data["emojis"]]
        self.system_channel_id = data["system_channel_id"]
        self.system_channel_flags = data["system_channel_flags"]

    async def get_member(self, member_id):
        return await self.discordApi.get_guild_member(member_id, self.id)