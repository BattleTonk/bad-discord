class Embed:
    def __init__(self, title=None, description=None, url=None, timestamp=None, color=None, footer=None,
                 image=None, thumbnail=None, video=None, provider=None, author=None, fields=None):
        self.title = title
        self.description = description
        self.url = url
        self.timestamp = timestamp
        self.color = color
        self.footer = footer
        self.image = image
        self.thumbnail = thumbnail
        self.video = video
        self.provider = provider
        self.author = author
        self.fields = fields

    def get_dict(self):
        ret = {}
        for (key, value) in self.__dict__.items():
            if value != None:
                ret[key] = value
        return ret

    def set_title(self, title):
        self.title = title
