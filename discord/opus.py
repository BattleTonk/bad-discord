from ctypes import util
import ctypes
import os
import sys
import array
import struct


class EncoderStruct(ctypes.Structure):
    pass


EncoderStructPtr = ctypes.POINTER(EncoderStruct)

c_int_ptr = ctypes.POINTER(ctypes.c_int)
c_int16_ptr = ctypes.POINTER(ctypes.c_int16)
c_float_ptr = ctypes.POINTER(ctypes.c_float)


_basedir = os.path.dirname(os.path.abspath(__file__))
_bitness = struct.calcsize('P') * 8
_target = 'x64' if _bitness > 32 else 'x86'
_filename = os.path.join(_basedir, 'bin', f'libopus-0.{_target}.dll')
lib = ctypes.cdll.LoadLibrary(_filename)

lib.opus_encode.argtypes = [EncoderStructPtr, c_int16_ptr, ctypes.c_int, ctypes.c_char_p, ctypes.c_int32]
lib.opus_encode.restype = ctypes.c_int32

lib.opus_encoder_create.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, c_int_ptr]
lib.opus_encoder_create.restype = EncoderStructPtr

lib.opus_encoder_ctl.argtypes = [EncoderStructPtr, ctypes.c_int]

##https://github.com/gcp/opus/blob/master/include/opus_defines.h
OPUS_SET_BITRATE_REQUEST = 4002
OPUS_APPLICATION_AUDIO = 2049
OPUS_SET_INBAND_FEC_REQUEST = 4012
OPUS_SET_PACKET_LOSS_PERC_REQUEST = 4014
OPUS_SET_BANDWIDTH_REQUEST = 4008
OPUS_BANDWIDTH_FULLBAND = 1105
OPUS_SET_SIGNAL_REQUEST = 4024
OPUS_AUTO = -1000


class OpusEncoder:
    SAMPLING_RATE = 48000
    CHANNELS = 2
    FRAME_LENGTH = 20  # in milliseconds
    SAMPLE_SIZE = struct.calcsize('h') * CHANNELS
    SAMPLES_PER_FRAME = int(SAMPLING_RATE / 1000 * FRAME_LENGTH)

    FRAME_SIZE = SAMPLES_PER_FRAME * SAMPLE_SIZE

    def __init__(self):
        self.encoder = lib.opus_encoder_create(48000, 2, OPUS_APPLICATION_AUDIO, ctypes.byref(ctypes.c_int()))##48000 - sample rate(discord requires 48kHz), 2 - the number of channels(discord requires 2)
        lib.opus_encoder_ctl(self.encoder, 128 * 1024, OPUS_SET_BITRATE_REQUEST)##setting the bitrate
        lib.opus_encoder_ctl(self.encoder, OPUS_SET_INBAND_FEC_REQUEST, 1)
        lib.opus_encoder_ctl(self.encoder, OPUS_SET_PACKET_LOSS_PERC_REQUEST, min(100, max(0, int(0.15 * 100))))
        lib.opus_encoder_ctl(self.encoder, OPUS_SET_BANDWIDTH_REQUEST, OPUS_BANDWIDTH_FULLBAND)
        lib.opus_encoder_ctl(self.encoder, OPUS_SET_SIGNAL_REQUEST, OPUS_AUTO)

    def encode(self, pcm: bytes, frame_size: int) -> bytes:
        max_data_bytes = len(pcm)

        pcm_ptr = ctypes.cast(pcm, ctypes.POINTER(ctypes.c_int16))  # type: ignore
        data = (ctypes.c_char * max_data_bytes)()

        ret = lib.opus_encode(self.encoder, pcm_ptr, frame_size, data, max_data_bytes)

        return array.array('b', data[:ret]).tobytes()

