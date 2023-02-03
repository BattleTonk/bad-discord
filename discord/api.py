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


import requests
import json
from .channel import GuildTextChannel
from .helpful_functions import *


DISCORD_API = "https://discord.com/api/v6"


def handle_api_response(resp):
    body = resp.json()
    if resp.status_code != 200:
        raise Exception(f"invalid status code {resp.status_code}:\n{body}")
    elif "errors" in body:
        raise Exception(f"{body}")

    return body


class DiscordAPI:
    def __init__(self, token):
        self._token = token
        self.multipartFormdataEncoder = MultipartFormdataEncoder()

    async def run(self, path, method, body=None, content_type="application/json"):
        url = f"{DISCORD_API}{path}"
        headers = {
            "Authorization": self._token,
            "content-type": content_type
        }
        if method == "GET":
            request_method_reference = requests.get
        elif method == "PUT":
            request_method_reference = requests.put
        elif method == "POST":
            request_method_reference = requests.post
        elif method == "PATCH":
            request_method_reference = requests.patch
        else:
            raise Exception(f"unsupported HTTP method {method}")
        resp = request_method_reference(url, headers=headers, data=body)
        return handle_api_response(resp)

    async def create_message(self, channel_id, content=None, reply=None, embeds=None, files=None, components=None):
        json_data = {}
        if content != None:
            json_data["content"] = content
        if reply != None:
            json_data["message_reference"] = {
                "message_id": reply
            }
        if embeds != None:
            json_data["embeds"] = [embed.get_dict() for embed in embeds]
        if components != None:
            json_data["components"] = [component.get_dict() for component in components]

        if files != None:
            files_data_multipart = [(f"file{file_directory}", file_directory, open(file_directory, 'rb')) for file_directory in files]
            if json_data != {}:
                 content_type, body = MultipartFormdataEncoder().encode(files=files_data_multipart,
                                                                   json_data=[("payload_json", json.dumps(json_data))])
            else:
                content_type, body = MultipartFormdataEncoder().encode(files=files_data_multipart)
        else:
            body = json.dumps(json_data)
            content_type = "application/json"

        return await self.run(f"/channels/{channel_id}/messages", "POST", body=body, content_type=content_type)

    async def send_files(self, content=None, reply=None, embeds=None, files=None):
        body = {"payload_json"}

    async def create_dm(self, recipient_id, content=None):
        body = {
            "recipient_id": recipient_id
        }
        dm_channel_id = (await self.run(f"/users/@me/channels", "POST", body=body))["id"]
        return await self.create_message(dm_channel_id, content)

    async def get_channel(self, channel_id):
        res = await self.run(f"/channels/{channel_id}", "GET")
        if res["type"] == GUILD_TEXT:
            return GuildTextChannel(self, res)
        return res

    async def update_channel(self, channel_id, data):
        res = await self.run(f"/channels/{channel_id}", "PATCH", data)
        return res

    async def update_guild_member(self, guild_id, guild_member_id, data):
        res = await self.run(f"/guilds/{guild_id}/members/{guild_member_id}", "PATCH", data)
        return res

    async def get_guild_invites(self, guild_id):
        res = await self.run(f"/guilds/{guild_id}/invites", "GET")
        return res


    async def respond_to_interaction(self, interaction_id, interaction_token, data):
        headers = {
            "content-type": "application/json"
        }
        body = {
            "type": 4,
            "data": {
                "content": "Слава Китаю"
            }
        }
        url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
        requests.post(url, headers=headers, data=json.dumps(body))


if __name__ == "__main__":
    with open(".token") as token_file:
        token = token_file.read()
        d = DiscordAPI(token)
        v = d.run("/users/@me", "GET")
        print(v)