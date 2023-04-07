import requests
import json
from .channel import GuildTextChannel
from .guild_member import GuildMember
from .guild import Guild
from .helpful_functions import *

# Constants for discord api
DISCORD_API = "https://discord.com/api/v9"


class DiscordAPI:
    def __init__(self, token):
        self._token = token
        ##self.session = requests.Session()
        self.requests_methods = {
            "GET": requests.get,
            "PUT": requests.put,
            "POST": requests.post,
            "PATCH": requests.patch
        }

    def handle_api_response(self, resp):
        body = resp.json()
        if resp.status_code != 200:
            raise Exception(f"invalid status code {resp.status_code}:\n{body}")
        elif "errors" in body:
            raise Exception(f"{body}")
        return body

    async def run(
            self,
            path,
            method,
            body=None,
            content_type="application/json"
    ):
        url = f"{DISCORD_API}{path}"
        headers = {
            "Authorization": self._token,
            "content-type": content_type
        }
        if method in self.requests_methods:
            request_method_reference = self.requests_methods[method]
        else:
            raise Exception(f"Unsupported HTTP method {method}.\nI dunno, try to change the discord API or the HTTP "
                            f"protocol, or just don't use my library for your HTTP requests")

        resp = request_method_reference(url, headers=headers, data=body)
        return self.handle_api_response(resp)

    async def create_message(
            self,
            channel_id,
            content=None,
            reply=None,
            embeds=None,
            files=None,
            components=None
    ):
        json_data = {}

        if content is not None:
            json_data["content"] = content

        if reply is not None:
            json_data["message_reference"] = {
                "message_id": reply
            }

        if embeds is not None:
            json_data["embeds"] = [embed.get_dict() for embed in embeds]

        if components is not None:
            json_data["components"] = [component.get_dict() for component in components]

        if files is not None:
            files_data_multipart = [(f"file{file_directory}", file_directory, open(file_directory, 'rb')) for
                                    file_directory in files]
            if json_data != {}:
                content_type, body = encode_to_multipart_form_data(files=files_data_multipart,
                                                                          json_data=[
                                                                              ("payload_json", json.dumps(json_data))])
            else:
                content_type, body = encode_to_multipart_form_data(files=files_data_multipart)
        else:
            body = json.dumps(json_data)
            content_type = "application/json"

        return await self.run(f"/channels/{channel_id}/messages", "POST", body=body, content_type=content_type)

    async def create_dm(self, recipient_id, content=None):
        body = {
            "recipient_id": recipient_id
        }
        body = json.dumps(body)
        dm_channel_id = (await self.run(f"/users/@me/channels", "POST", body=body))["id"]
        return await self.create_message(dm_channel_id, content)

    async def get_channel(self, channel_id):
        res = await self.run(f"/channels/{channel_id}", "GET")
        if res["type"] == GUILD_TEXT:
            return GuildTextChannel(self, res)
        return res

    async def update_channel(self, channel_id, data):
        data = json.dumps(data)
        res = await self.run(f"/channels/{channel_id}", "PATCH", data)
        return res

    async def update_guild_member(self, guild_id, guild_member_id, data):
        data = json.dumps(data)
        res = await self.run(f"/guilds/{guild_id}/members/{guild_member_id}", "PATCH", data)
        return res

    async def get_guild_invites(self, guild_id):
        res = await self.run(f"/guilds/{guild_id}/invites", "GET")
        return res

    async def respond_to_interaction(self, interaction_id, interaction_token, data):
        headers = {
            "content-type": "application/json"
        }
        body = data
        url = f"https://discord.com/api/v10/interactions/{interaction_id}/{interaction_token}/callback"
        requests.post(url, headers=headers, data=json.dumps(body))

    async def get_guild(self, guild_id):
        res = await self.run(f"/guilds/{guild_id}", "GET")
        return Guild(self, res)

    async def get_guild_member(self, member_id, guild_id):
        res = await self.run(f"/guilds/{guild_id}/members/{member_id}", "GET")
        return GuildMember(self, guild_id, res)
