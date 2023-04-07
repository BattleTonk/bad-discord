from .helpful_functions import get_as_questionable
from .guild_member import GuildMember
from .user import User
from .message import Message


class Interaction:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.id = data["id"]
        self.application_id = data["application_id"]
        self.type = data["type"]
        self.data = get_as_questionable(data, "data", [])
        self.guild_id = get_as_questionable(data, "guild_id")
        self.channel_id = get_as_questionable(data, "channel_id")
        self.member = get_as_questionable(data, "member")
        if self.member is not None:
            self.member = GuildMember(discordApi, self.guild_id, self.member)
        self.user = get_as_questionable(data, "user")
        if self.user is not None:
            self.user = User(discordApi, self.user)
        self.token = data["token"]
        self.version = data["version"]
        self.message = get_as_questionable(data, "message")
        if self.message is not None:
            self.message = Message(discordApi, self.message)
        self.app_permissions = get_as_questionable(data, "app_permissions")
        self.locale = get_as_questionable(data, "locale")
        self.guild_locale = get_as_questionable(data, "guild_locale")

    async def respond(self, interaction_response):
        await self.discordApi.respond_to_interaction(self.id, self.token, interaction_response.get_dict())
