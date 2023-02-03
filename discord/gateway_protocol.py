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


from .gateway import GatewayCon
from .message import Message


def handle_data(discordApi, data):
    if data["t"] == 'MESSAGE_CREATE':
        return Message(discordApi, data["d"])
    return data["d"]


class Gateway(GatewayCon):
    def __init__(self, token, discordApi):
        super().__init__(token)
        self.discordApi = discordApi
        self.handlers = {}

    async def handle_message(self, data):
        if data["op"] == 0:
            self.sequence = data["s"]
            event_type = data["t"].lower()
            if event_type == 'ready':
                self.resume_gateway_url = data["d"]["resume_gateway_url"]
                self.session_id = data["d"]["session_id"]
            if event_type in self.handlers:
                await self.handlers[event_type](handle_data(self.discordApi, data))
        if data["op"] == 11:
            pass

    def event(self, f):
        self.handlers[f.__name__] = f