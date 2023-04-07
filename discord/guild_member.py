from .helpful_functions import get_as_questionable
from .user import User


class GuildMember:
    def __init__(self, discordApi, guild_id, data):
        self.discordApi = discordApi
        self.guild_id = guild_id
        self.user = User(discordApi, data["user"])
        self.nick = get_as_questionable(data, "nick")
        self.avatar = get_as_questionable(data, "avatar")
        self.roles = data["roles"]
        self.joined_at = data["joined_at"]
        self.premium_since = get_as_questionable(data, "premium_since")
        self.deaf = data["deaf"]
        self.mute = data["mute"]
        self.pending = get_as_questionable(data, "pending")
        self.permissions = get_as_questionable(data, "permissions")
        self.communication_disabled_until = get_as_questionable(data, "communication_disabled_until")

    async def update(self, data):
        await self.discordApi.update_guild_member(self.guild_id, self.user.id, data)

    async def change_nick(self, nick):
        data = {
            "nick": nick
        }
        await self.update(data)
        self.nick = nick

    async def add_role(self, role):
        data = {
            "roles": [role_.id for role_ in self.roles] + [role.id]
        }
        await self.update(data)
        self.roles.append(role)