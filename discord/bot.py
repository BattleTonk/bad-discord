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


from .gateway_protocol import Gateway
from .api import DiscordAPI


class Bot:
    def __init__(self, token, self_bot=False):
        if not self_bot:
            token = "Bot " + token
        self.discordApi = DiscordAPI(token)
        self._g = Gateway(token, self.discordApi)

    def run_gateway(self):
        self._g.run()

    def event(self, f):
        self._g.event(f)

    async def get_channel(self, channel_id):
        return await self.discordApi.get_channel(channel_id)

    async def respond_to_interaction(self, interaction_id, interaction_token):
        await self.discordApi.respond_to_interaction(interaction_id, interaction_token, "")