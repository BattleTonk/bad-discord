

class Guild:
    def __init__(self, discordApi, data):
        self.discordApi = discordApi
        self.id = data["id"]
        self.name = data["name"]