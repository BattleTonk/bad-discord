"""
MIT License

Copyright (c) 2023-present BattleTonk

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from .helpful_functions import *
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