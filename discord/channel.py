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


from .message import Message


class TextChannel:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.id = data["id"]
        self.type = data["type"]
        self.last_message_id = data["last_message_id"]
        self.flags = data["flags"]

    async def send(self, content=None, embeds=None, files=None, components=None):
        return Message(self.discordApi, await self.discordApi.create_message(self.id, content=content, embeds=embeds, files=files, components=components))

    async def update(self, data):
        self.__init__(self.discordApi, await self.discordApi.update_channel(self.id, data))
        return self


class DMChannel(TextChannel):
    def __init__(self, discordApi, data):
        super().__init__(discordApi, data)
        self.recipients = data["recipients"]


class GuildChannel:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.name = data["name"]
        self.position = data["position"]
        self.flags = data["flags"]
        self.parent_id = data["parent_id"]
        self.guild_id = data["guild_id"]
        self.permission_overwrites = data["permission_overwrites"]


class GuildTextChannel(GuildChannel, TextChannel):
    def __init__(self, discordApi, data):
        GuildChannel.__init__(self, discordApi, data)
        TextChannel.__init__(self, discordApi, data)
        self.topic = data["topic"]
        self.rate_limit_per_user = data["rate_limit_per_user"]
        self.nsfw = data["nsfw"]


class GuildVoiceChannel(GuildTextChannel):
    def __init__(self, discordApi, data):
        super().__init__(discordApi, data)
        self.rtc_region = data["rtc_region"]
        self.user_limit = data["user_limit"]
        self.bitrate = data["bitrate"]
