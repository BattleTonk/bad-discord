from .helpful_functions import get_as_questionable


class Role:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.id = data["id"]
        self.name = data["name"]
        self.color = data["color"]
        self.hoist = data["hoist"]
        self.icon = get_as_questionable(data, "icon")
        self.unicode_emoji = get_as_questionable(data, "unicode_emoji")
        self.position = data["position"]
        self.permissions = data["permissions"]
        self.managed = data["managed"]
        self.mentionable = data["mentionable"]
        self.tags = get_as_questionable(data, "tags")