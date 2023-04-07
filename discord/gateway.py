import asyncio
import websockets
from websockets import exceptions
import json
from .message import Message
from .interaction import Interaction
from .guild_member import GuildMember
import time
import threading
from .helpful_functions import sane_wait_for
from threading import Thread
import logging


GATEWAY_URL = "wss://gateway.discord.gg/"


def handle_data(discordApi, data):
    if data["t"] == "MESSAGE_CREATE":
        return Message(discordApi, data["d"])
    if data["t"] == "INTERACTION_CREATE":
        return Interaction(discordApi, data["d"])
    if data["t"] == "GUILD_MEMBER_ADD":
        return GuildMember(discordApi, data["d"]["guild_id"], data["d"])
    return data["d"]


class Gateway:
    def __init__(self, token, discordApi, voiceClient):
        self.token = token
        self.interval = None
        self.sequence = None
        self.websocket = None
        self.resume_gateway_url = None
        self.session_id = None
        self.discordApi = discordApi
        self.handlers = {}
        self.voiceClient = voiceClient
        self.catch_events = {}
        self.voice_connected = None
        self.loop = None

    def run(self):
        ##loop = asyncio.get_event_loop()
        ##try:
            ##loop.run_until_complete(self._run_connection())
        ##except websockets.exceptions.ConnectionClosedError:
            ##pass
        ##except websockets.exceptions.ConnectionClosedOK:
            ##pass
        try:
            asyncio.run(self._run_connection(resume=False))
        except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
            while True:
                try:
                    asyncio.run(self._run_connection(resume=True))
                except (websockets.exceptions.ConnectionClosedError, websockets.exceptions.ConnectionClosedOK):
                    pass

    async def _run_connection(self, resume=False):
        self.voice_connected = asyncio.Event()
        loop = asyncio.get_running_loop()
        self.loop = loop
        self.voiceClient.loop = loop
        print(self.loop)
        print("running Gateway")
        wsurl = f"{GATEWAY_URL}/?v=9&encoding=json"
        async with websockets.connect(wsurl) as self.websocket:
            if not resume:
                print('Establishing connection to discord websocket.')
                await self.hello()
                print('Connection to discord websocket established.')
            else:
                print('Reconnecting to discord websocket.')
                await self.resume()
                print('Reconnected to discord websocket.')
            await asyncio.gather(self._heartbeat_loop(), self._recv_loop())

    async def _recv_loop(self):
        async for message in self.websocket:
            message = json.loads(message)
            await self.handle_message(message)

    async def _send(self, data):
        data = json.dumps(data)
        await self.websocket.send(data)

    async def hello(self):
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

    async def resume(self):
        data = {
            "op": 6,
            "d": {
                "token": self.token,
                "session_id": self.session_id,
                "seq": self.sequence
            }
        }
        await self._send(data)

    async def _heartbeat_loop(self):
        while True:
            await asyncio.sleep(self.interval)
            ping = {
                "op": 1,
                "d": self.sequence,
            }
            await self._send(ping)

    async def handle_message(self, data):
        if data["op"] == 0:
            self.sequence = data["s"]
            event_type = data["t"]
            if event_type == "VOICE_SERVER_UPDATE":
                self.voice_connected.set()
                self.catch_events["VOICE_SERVER_UPDATE"] = [True, data]

            if event_type == 'READY':
                self.resume_gateway_url = data["d"]["resume_gateway_url"]
                self.session_id = data["d"]["session_id"]
            ##if event_type == "interaction_create":
                ##if data["d"]["id"] in self.interactions_handler:
                    ##await self.interactions_handler[data["d"]["id"]](data["d"])
            event_type = event_type.lower()
            if event_type in self.handlers:
                asyncio.create_task(self.handlers[event_type](handle_data(self.discordApi, data)))
        if data["op"] == 11:
            pass

    async def connect_to_voice(self, guild_id, channel_id, self_mute=False, self_deaf=False):
        if not self.voiceClient.connected:
            self.voice_connected.clear()
            self.catch_events["VOICE_SERVER_UPDATE"] = [False, []]
            data = {
                "op": 4,
                "d": {
                    "guild_id": guild_id,
                    "channel_id": channel_id,
                    "self_mute": self_mute,
                    "self_deaf": self_deaf
                },
            }
            await self._send(data)
            futures = [
                self.voice_connected.wait(),
            ]
            await sane_wait_for(futures, 30)
            if self.catch_events["VOICE_SERVER_UPDATE"][0]:
                data = self.catch_events["VOICE_SERVER_UPDATE"][1]
                await self.voiceClient.connect(data["d"]["endpoint"], data["d"]["guild_id"], self.session_id,
                                               data["d"]["token"])
                return True
            return False

    def event(self, f):
        self.handlers[f.__name__] = f


async def my_coroutine(websocket):
    await websocket.close()


class VoiceGateway:
    def __init__(self, client, url, server_id, session_id, token):
        self.user_id = client.user_id
        self.token = token
        self.url = url
        self.server_id = server_id
        self.session_id = session_id
        self.client = client

        self.websocket = None
        self.heartbeat_interval = None

        self.connected = False
        self.loop = self.client.loop

        self.ping_thread = None

    def close_websocket(self):
        asyncio.run_coroutine_threadsafe(my_coroutine(self.websocket), asyncio.get_event_loop())
        self.connected = False

    def close_connection(self):
        self.close_websocket()

    async def poll_event(self):
        message = await self.websocket.recv()
        message = json.loads(message)
        await self.handle_message(message)

    async def run_connection(self, resume=False):
        print("running Voice Gateway")
        wsurl = f"wss://{self.url}/?v=4"
        self.websocket = websockets.connect(wsurl)
        self.connected = True
        if not resume:
            print('Establishing connection to discord voice websocket.')
            await self.identify()
            print('Connection to discord voice websocket established.')
        else:
            print('Reconnecting to discord voice websocket.')
            await self.resume()
            print('Reconnected to discord voice websocket.')

    async def start_connection(self):
        wsurl = f"wss://{self.url}/?v=4"
        self.websocket = await websockets.connect(wsurl)
        self.connected = True
        print('Establishing connection to discord voice websocket.')
        await self.identify()
        print('Connection to discord voice websocket established.')

    async def _send(self, data):
        if self.connected:
            data = json.dumps(data)
            await self.websocket.send(data)

    async def identify(self):
        print("identifying")
        data = {
            "op": 0,
            "d": {
                "server_id": self.server_id,
                "user_id": self.user_id,
                "session_id": self.session_id,
                "token": self.token
            }
        }
        await self._send(data)
        print("identified")

    async def resume(self):
        data = {
            "op": 7,
            "d": {
                "server_id": self.server_id,
                "session_id": self.session_id,
                "token": self.token
            }
        }
        await self._send(data)

    def _heartbeat_loop(self):
        print(self.loop)
        while True and self.connected:
            time.sleep(self.heartbeat_interval)
            data = {
                "op": 3,
                "d": time.time() / 1000
            }
            asyncio.run_coroutine_threadsafe(self._send(data), loop=self.loop)

    async def handle_message(self, data):
        if data["op"] == 0:
            self.sequence = data["s"]
        if data["op"] == 2:
            await self.client.set_udp_setting(data["d"]["ip"], data["d"]["port"], data["d"]["ssrc"], data["d"]["modes"])
            await self.select_protocol()
        if data["op"] == 4:
            self.client.secret_key = data["d"]["secret_key"]
        if data["op"] == 8:
            self.heartbeat_interval = data["d"]["heartbeat_interval"] / 1000
            await self._send({
                "op": 3,
                "d": time.time() / 1000
            })
            self.ping_thread = threading.Thread(target=self._heartbeat_loop)
            self.ping_thread.start()

        if data["op"] == 11:
            pass

    async def select_protocol(self):
        data = {
            "op": 1,
            "d": {
                "protocol": "udp",
                "data": {
                    "address": self.client.ip,
                    "port": self.client.port,
                    "mode": "xsalsa20_poly1305_lite"
                }
            }
        }
        await self._send(data)

    async def start_sending(self, filepath):
        if not self.client.playing:
            await self.speaking(self.client.ssrc)
            self.client.source = filepath
            thread = threading.Thread(target=self.client.send_voice)
            thread.start()
            print("started sending")

    async def speaking(self, ssrc):
        data = {
            "op": 5,
            "d": {
                "speaking": 5,
                "delay": 0,
                "ssrc": ssrc
            }
        }
        data = json.dumps(data)
        await self.websocket.send(data)