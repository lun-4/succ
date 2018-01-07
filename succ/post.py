import codecs


class Post:
    """Describes a hypnohub post."""
    def __init__(self, data: dict):
        self.id = data['id']
        self.tags = data['tags'].split(' ')
        self.timestamp = data['created_at']
        self.hash = data['md5']
        self.url = data['file_url']

    @property
    def bhash(self):
        return codecs.decode(self.hash, 'hex')
