from .helpful_functions import get_as_questionable


class Emoji:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.id = data["id"]
        self.name = data["name"]
        self.roles_id = get_as_questionable(data, "roles", [])
        self.user = get_as_questionable(data, "user")
        self.require_colons = get_as_questionable(data, "require_colons", False)
        self.managed = get_as_questionable(data, "managed", False)
        self.available = get_as_questionable(data, "available", False)
