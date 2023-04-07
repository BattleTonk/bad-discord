import codecs
import sys
import uuid
import io
import asyncio

GUILD_TEXT = 0
DM = 1
GUILD_VOICE = 2
GROUP_DM = 3
GUILD_CATEGORY = 4
GUILD_ANNOUNCEMENT = 5
ANNOUNCEMENT_THREAD = 6
PUBLIC_THREAD = 7
PRIVATE_THREAD = 8
GUILD_STAGE_VOICE = 13
GUILD_DIRECTORY = 14
GUILD_FORUM = 15


def u(s):
    if sys.hexversion < 0x03000000 and isinstance(s, str):
        s = s.decode('utf-8')
    if sys.hexversion >= 0x03000000 and isinstance(s, bytes):
        s = s.decode('utf-8')
    return s


def iter(boundary, json_data=None, files=None):
    encoder = codecs.getencoder('utf-8')
    if json_data != None:
        for (key, value) in json_data:
            key = u(key)
            yield encoder('--{}\r\n'.format(boundary))
            yield encoder(u('Content-Disposition: form-data; name="{}"\r\n').format(key))
            yield encoder(
                'Content-Type: application/json\r\n')
            yield encoder('\r\n')
            if isinstance(value, int) or isinstance(value, float):
                value = str(value)
            yield encoder(u(value))
            yield encoder('\r\n')
    if files != None:
        for (key, filename, fd) in files:
            key = u(key)
            filename = u(filename)
            yield encoder('--{}\r\n'.format(boundary))
            yield encoder(
                u('Content-Disposition: form-data; name="{}"; filename="{}"\r\n').format(key, filename))
            yield encoder('\r\n')
            with fd:
                buff = fd.read()
                yield (buff, len(buff))
            yield encoder('\r\n')
    yield encoder('--{}--\r\n'.format(boundary))


def encode_to_multipart_form_data(json_data=None, files=None):
    body = io.BytesIO()
    boundary = uuid.uuid4().hex
    content_type = 'multipart/form-data; boundary={}'.format(boundary)
    for chunk, chunk_len in iter(boundary=boundary, json_data=json_data, files=files):
        body.write(chunk)
    return content_type, body.getvalue()


def get_as_questionable(data, key, default_ret=None):
    try:
        value = data[key]
    except KeyError:
        return default_ret
    else:
        return value


class MultipartFormdataEncoder(object):
    def __init__(self):
        self.boundary = uuid.uuid4().hex
        self.content_type = 'multipart/form-data; boundary={}'.format(self.boundary)

    @classmethod
    def u(cls, s):
        if sys.hexversion < 0x03000000 and isinstance(s, str):
            s = s.decode('utf-8')
        if sys.hexversion >= 0x03000000 and isinstance(s, bytes):
            s = s.decode('utf-8')
        return s

    def iter(self, json_data=None, files=None):
        encoder = codecs.getencoder('utf-8')
        if json_data != None:
            for (key, value) in json_data:
                key = self.u(key)
                yield encoder('--{}\r\n'.format(self.boundary))
                yield encoder(self.u('Content-Disposition: form-data; name="{}"\r\n').format(key))
                yield encoder(
                    'Content-Type: application/json\r\n')
                yield encoder('\r\n')
                if isinstance(value, int) or isinstance(value, float):
                    value = str(value)
                yield encoder(self.u(value))
                yield encoder('\r\n')
        if files != None:
            for (key, filename, fd) in files:
                key = self.u(key)
                filename = self.u(filename)
                yield encoder('--{}\r\n'.format(self.boundary))
                yield encoder(
                    self.u('Content-Disposition: form-data; name="{}"; filename="{}"\r\n').format(key, filename))
                yield encoder('\r\n')
                with fd:
                    buff = fd.read()
                    yield (buff, len(buff))
                yield encoder('\r\n')
        yield encoder('--{}--\r\n'.format(self.boundary))

    def encode(self, json_data=None, files=None):
        body = io.BytesIO()
        for chunk, chunk_len in self.iter(json_data=json_data, files=files):
            body.write(chunk)
        return self.content_type, body.getvalue()


async def sane_wait_for(futures, timeout):
    ensured = [asyncio.ensure_future(fut) for fut in futures]
    done, pending = await asyncio.wait(ensured, timeout=timeout, return_when=asyncio.ALL_COMPLETED)

    if len(pending) != 0:
        raise asyncio.TimeoutError()

    return done