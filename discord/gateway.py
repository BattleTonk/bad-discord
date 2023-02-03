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


import asyncio
import websockets
import json

GATEWAY_URL = "wss://gateway.discord.gg/"


class GatewayCon(object):
    def __init__(self, token):
        print("init Gateway Connection")
        self.token = token
        self.interval = None
        self.sequence = None
        self.websocket = None
        self.resume_gateway_url = None
        self.session_id = None

    def run(self):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self._run_connection())

    async def _run_connection(self):
        print("running Gateway")
        wsurl = f"{GATEWAY_URL}/?v=9&encoding=json"
        async with websockets.connect(wsurl) as self.websocket:
            ret = json.loads(await self.websocket.recv())
            if ret["op"] == 10:
                self.interval = ret["d"]["heartbeat_interval"] / 1000
            else:
                raise Exception("An error occurred while establishing connection with discord gateway, no hello event was sended from discord")
            data = {
                "op": 2,
                "d": {
                    "token": self.token,
                    "intents": 131071,
                    "properties": {
                        "$os": "windows",
                        "$browser": "disco",
                        "$device": "disco"
                    },
                }
            }
            await self._send(data)
            await asyncio.gather(self._heartbeat_loop(), self._recv_loop())

    async def _recv_loop(self):
        async for message in self.websocket:
            message = json.loads(message)
            await self.handle_message(message)

    async def _send(self, data):
        data = json.dumps(data)
        await self.websocket.send(data)

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(self.interval)
            ping = {
                "op": 1,
                "d": self.sequence,
            }
            await self._send(ping)

    async def handle_message(self, msg):
        pass