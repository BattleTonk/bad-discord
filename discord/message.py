from abc import ABC, abstractmethod
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


def do_nothing(data):# This function is used just for Component.on_interact initialization, because i'm a turbo shit paster
    pass


class Message:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.id = int(data['id'])
        self.webhook_id = get_as_questionable(data, 'webhook_id')
        self.channel_id = data["channel_id"]
        self.reactions = get_as_questionable(data, 'reactions')
        self.attachments = get_as_questionable(data, 'attachments')
        self.mentions = data["mentions"]
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
        await self.discordApi.create_message(self.channel_id, content=content, reply=self.id, embeds=embeds,
                                             files=files)

    async def delete(self):
        await self.discordApi.delete_message(self.id, self.channel_id)


class ActionRow:
    def __init__(self, components=None):
        if components is None:
            components = []
        self.type = 1
        self.components = components

    def get_dict(self):
        data = {
            "type": 1,
            "components": [value.get_dict() for value in self.components]
        }
        return data

    def add_component(self, component):
        self.components.append(component)


class Component:
    def __init__(self, type, custom_id):
        self.type = type
        ##self.on_interact = do_nothing
        self.custom_id = custom_id
        ##self.discord_gateway = discord_gateway

    ##def set_on_interact(self, func):#For all of this to work, you should pass a function that takes minimum 1 parameter
        ##self.discord_gateway.add_interaction_event(self.custom_id, func)

    def get_dict(self):
        data = {}
        for (key, value) in self.__dict__.items():
            if value != None and key != "on_interact" and key != "discord_gateway":
                data[key] = value
        return data


class Button(Component):
    def __init__(
            self,
            style,
            label="",
            emoji=None,
            custom_id=None,
            url=None,
            disabled=False,
            type=None
    ):
        super().__init__(2, custom_id)
        self.style = style
        self.label = label
        self.emoji = emoji
        self.custom_id = custom_id
        self.url = url
        self.disabled = disabled


class SelectMenu(Component):
    def __init__(
            self,
            type,
            custom_id,
            placeholder=None,
            min_values=1,
            max_values=1,
            disabled=False,
    ):
        super().__init__(type, custom_id)
        self.placeholder = placeholder
        self.min_values = min_values
        self.max_values = max_values
        self.disabled = disabled


class StringSelect(SelectMenu):
    def __init__(
            self,
            custom_id,
            options,
            placeholder=None,
            min_values=1,
            max_values=1,
            disabled=False,
            type=None
    ):
        super().__init__(3, custom_id, placeholder, min_values, max_values, disabled)
        self.options = options

    def add_option(self, option):
        self.options.append(option)


class UserSelect(SelectMenu):
    def __init__(
            self,
            custom_id,
            placeholder=None,
            min_values=1,
            max_values=1,
            disabled=False,
            type=None
    ):
        super().__init__(5, custom_id, placeholder, min_values, max_values, disabled)


class RoleSelect(SelectMenu):
    def __init__(
            self,
            custom_id,
            placeholder=None,
            min_values=1,
            max_values=1,
            disabled=False,
            type=None
    ):
        super().__init__(6, custom_id, placeholder, min_values, max_values, disabled)


class MentionableSelect(SelectMenu):
    def __init__(
            self,
            custom_id,
            placeholder=None,
            min_values=1,
            max_values=1,
            disabled=False,
            type=None
    ):
        super().__init__(7, custom_id, placeholder, min_values, max_values, disabled)


class ChannelSelect(SelectMenu):
    def __init__(
            self,
            custom_id,
            channel_types,
            placeholder=None,
            min_values=1,
            max_values=1,
            disabled=False,
            type=None
    ):
        super().__init__(8, custom_id, placeholder, min_values, max_values, disabled)
        self.channel_types = channel_types


class TextInput(Component):
    def __init__(
            self,
            custom_id,
            style,
            label,
            min_length=None,
            max_length=None,
            required=True,
            value=None,
            placeholder=None,
            type=None
    ):
        super().__init__(4, custom_id)
        self.style = style
        self.label = label
        self.min_length = min_length
        self.max_length = max_length
        self.required = required
        self.value = value
        self.placeholder = placeholder


