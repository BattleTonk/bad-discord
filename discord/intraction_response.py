class InteractionResponse:
    def __init__(self, type, tts=None, content=None, embeds=None, allowed_mentions=None, components=None, attachments=None, ephemeral=False):
        self.type = type
        self.tts = tts
        self.content = content
        self.embeds = embeds
        self.allowed_mentions = allowed_mentions
        self.components = components
        self.attachments = attachments
        self.ephemeral = ephemeral

    def get_dict(self):
        data = {
            "type": self.type,
            "data": {}
        }
        if self.tts is not None:
            data["data"]["tts"] = self.tts
        if self.content is not None:
            data["data"]["content"] = self.content
        if self.embeds is not None:
            data["data"]["embeds"] = self.embeds
        if self.allowed_mentions is not None:
            data["data"]["allowed_mentions"] = self.allowed_mentions
        if self.components is not None:
            data["data"]["components"] = [value.get_dict() for value in self.components]
        if self.ephemeral:
            data["data"]["flags"] = 64
        return data


class ModalInteractionResponse:
    def __init__(self, custom_id, title, components):
        self.custom_id = custom_id
        self.title = title
        self.components = components

    def get_dict(self):
        data = {
            "type": 9,
            "data": {}
        }
        if self.custom_id is not None:
            data["data"]["custom_id"] = self.custom_id
        if self.title is not None:
            data["data"]["title"] = self.title
        if self.components is not None:
            data["data"]["components"] = [value.get_dict() for value in self.components]
        return data