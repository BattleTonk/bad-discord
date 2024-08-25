from .gateway import VoiceGateway
import socket
import struct
from .opus import OpusEncoder
import nacl
from nacl import secret, utils
import io
import time
import subprocess
import asyncio
import logging


def convert_mp4(filename)->io.BytesIO:
    converted_data = subprocess.run(['ffmpeg', '-i', filename, '-f', 's16le', '-ar', '48000', '-ac', '2', '-loglevel', 'warning', "pipe:1"], stdout=subprocess.PIPE).stdout
    return io.BytesIO(converted_data)


class VoiceClient:# handles everything related to discord voice
    def __init__(self, token, user_id):
        self.voiceWebsocket = None
        self.token = token
        self.user_id = user_id
        self.ssrc = None
        self.udp_ip = None
        self.udp_port = None
        self.ip = None
        self.port = None
        self.modes = []
        self.encoder = OpusEncoder()
        self.mode = "xsalsa20_poly1305_lite"
        self.secret_key = None
        self.socket = None
        self.sequence = 0
        self.timestamp = 0
        self._lite_nonce = 0
        self.source = "D:/Музыка/Прикольный треш/red sun in the sky.mp3"
        self.voice_connected = None#used in VoiceGateway

        self.connected = False
        self.playing = False

        self.log:logging.Logger = None

    def set_source(self, source):
        self.source = source

    async def connect(self, gateway_url, server_id, session_id, token):
        self.log.debug("Starting a discord voice connection")
        self.voiceWebsocket = VoiceGateway(self, gateway_url, server_id, session_id, token)
        self.voiceWebsocket.log = self.log
        await self.voiceWebsocket.run_connection()
        while self.secret_key is None:
            await self.voiceWebsocket.poll_event()
        self.connected = True
        self.log.debug("The connection to the discord voice was successful")

    def disconnect(self):
        self.voiceWebsocket.close_connection()

    async def set_udp_setting(self, udp_ip, udp_port, ssrc, modes):
        self.log.debug(f"Setting up the udp connection, setting udp_ip to: {udp_ip}, setting udp_port to: {udp_port}, setting ssrc to: {ssrc}")
        self.udp_ip = udp_ip
        self.udp_port = udp_port
        self.ssrc = ssrc
        self.modes = modes

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        packet = bytearray(74)
        struct.pack_into('>H', packet, 0, 1)
        struct.pack_into('>H', packet, 2, 70)
        struct.pack_into('>I', packet, 4, self.ssrc)

        self.socket.sendto(packet, (self.udp_ip, self.udp_port))
        recv = await asyncio.get_running_loop().sock_recv(self.socket, 74)

        ip_start = 8
        ip_end = recv.index(0, ip_start)
        ip = recv[ip_start:ip_end].decode('ascii')

        port = struct.unpack_from('>H', recv, len(recv) - 2)[0]
        self.ip = ip
        self.port = port

    def _get_voice_packet(self, data):
        header = bytearray(12)

        # Setting the RTP header
        header[0] = 0x80
        header[1] = 0x78
        struct.pack_into('>H', header, 2, self.sequence)
        struct.pack_into('>I', header, 4, self.timestamp)
        struct.pack_into('>I', header, 8, self.ssrc)

        encrypt_packet = self._encrypt_xsalsa20_poly1305_lite
        return encrypt_packet(header, data)

    def _encrypt_xsalsa20_poly1305(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        nonce = bytearray(24)
        nonce[:12] = header

        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext

    def _encrypt_xsalsa20_poly1305_suffix(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        nonce = nacl.utils.random(nacl.secret.SecretBox.NONCE_SIZE)

        return header + box.encrypt(bytes(data), nonce).ciphertext + nonce

    def _encrypt_xsalsa20_poly1305_lite(self, header: bytes, data) -> bytes:
        box = nacl.secret.SecretBox(bytes(self.secret_key))
        nonce = bytearray(24)

        nonce[:4] = struct.pack('>I', self._lite_nonce)
        self._lite_nonce += 1

        return header + box.encrypt(bytes(data), bytes(nonce)).ciphertext + nonce[:4]

    async def send_voice(self):
        self.log.debug("sending the voice packets to discord")
        self.sequence = 0
        self.timestamp = 0
        self._lite_nonce = 0

        if self.ip is None:
            self.log.debug("voice client is not connected")
            return
        if self.secret_key is None:
            self.log.debug("secret key is not set")
            return

        data = convert_mp4(self.source)

        loops = 0
        DELAY = OpusEncoder.FRAME_LENGTH / 1000.0
        start = time.perf_counter()

        self.playing = True

        while (audio_data := data.read(self.encoder.FRAME_SIZE)):
            loops += 1
            self.sequence += 1
            encoded_audio_data = self.encoder.encode(audio_data, self.encoder.SAMPLES_PER_FRAME)
            packet = self._get_voice_packet(encoded_audio_data)
            self.socket.sendto(packet, (self.udp_ip, self.udp_port))
            self.timestamp += OpusEncoder.SAMPLES_PER_FRAME
            next_time = start + DELAY * loops
            delay = max(0, DELAY + (next_time - time.perf_counter()))
            await asyncio.sleep(delay)
        self.playing = False