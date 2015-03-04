class Torrent:

    def __init__(self, id, title, url, category, sub_category, torrent_link, magnet_link,
                 size, user, seeders, leachers):
        self.id = id
        self.title = title
        self.url = url
        self.category = category
        self.sub_category = sub_category
        self.torrent_link = torrent_link
        self.magnet_link = magnet_link
        self.size = size
        self.user = user
        self.seeders = seeders
        self.leachers = leachers

        self._description = None
        self._files = None
        self._comments = None

