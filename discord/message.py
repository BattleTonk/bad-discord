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


def decode_components(data):
    componets = []
    for componet in data:
        if componet["type"] == 1:
            action_row_componets = []
            for componet2 in componet["components"]:
                if componet2["type"] == 2:
                    action_row_componets.append(Button(**componet2))
            componets.append(
                {
                    "type": 1,
                    "componets": action_row_componets
                }
            )
    return componets


class Message:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.id = int(data['id'])
        self.webhook_id = get_as_questionable(data, 'webhook_id')
        self.channel_id = data["channel_id"]
        self.reactions = get_as_questionable(data, 'reactions')
        self.attachments = get_as_questionable(data, 'attachments')
        self.embeds = data['embeds']
        self.application = get_as_questionable(data, 'application')
        self.activity = get_as_questionable(data, 'activity')
        self.call = None
        self._edited_timestamp = data['edited_timestamp']
        self.type = data['type']
        self.pinned = data['pinned']
        self.flags = get_as_questionable(data, 'flags')
        self.mention_everyone = data['mention_everyone']
        self.tts = data['tts']
        self.content = data['content']
        self.nonce = get_as_questionable(data, 'nonce')
        self.stickers = get_as_questionable(data, 'stickers')
        self.author = User(discordApi, data['author'])
        self.components = decode_components(get_as_questionable(data, 'components', []))

    async def reply(self, content=None, embeds=None, files=None):
        await self.discordApi.create_message(self.channel_id, content=content, reply=self.id, embeds=embeds, files=files)


class Component:
    def __init__(self, type):
        self.type = type

    def get_dict(self):
        data = {}
        for (key, value) in self.__dict__.items():
            if value != None:
                data[key] = value
        return data


class ActionRow(Component):
    def __init__(self, components=[], type=1):
        super().__init__(type)
        self.components = components

    def get_dict(self):
        data = {
            "type": 1,
            "components": [value.get_dict() for value in self.components]
        }
        return data


class Button(Component):
    def __init__(self, style, label="", emoji=None, custom_id=None, url=None, disabled=False, type=2):
        super().__init__(type)
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled

    def get_dict(self):
        data = {}
        for (key, value) in self.__dict__.items():
            if value != None:
                data[key] = value
        return data
