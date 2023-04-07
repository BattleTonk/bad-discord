from .gateway import Gateway
from .voice_client import VoiceClient
from .api import DiscordAPI
import threading


class Bot:
    def __init__(self, token, self_bot=False):
        if not self_bot:
            token = "Bot " + token
        self.discordApi = DiscordAPI(token)
        self.voiceClient = VoiceClient(token, 895726544859852811)
        self.gateway = Gateway(token, self.discordApi, self.voiceClient)

    def run_gateway(self):
        self.gateway.run()

    def event(self, f):
        self.gateway.event(f)

    async def get_channel(self, channel_id):
        return await self.discordApi.get_channel(channel_id)

    async def respond_to_interaction(self, interaction_id, interaction_token, ephemeral=False):
        flags = None
        if ephemeral:
            flags = 64
        await self.discordApi.respond_to_interaction(interaction_id, interaction_token, flags)

    async def get_guild(self, guild_id):
        return await self.discordApi.get_guild(guild_id)

    ##async def create_button(self, *args):
        ##return Button(self._g, **args[0])

    async def send_voice(self, source):
        await self.voiceClient.voiceWebsocket.start_sending(source)

    def disconnect_voice(self):
        self.voiceClient.disconnect()