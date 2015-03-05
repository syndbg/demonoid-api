class Torrent:

    def __init__(self, id, title, tracked_by, url, category, sub_category,
                 quality, owner, torrent_link, size, comments, times_completed,
                 seeders, leechers):
        self.id = id
        self.title = title
        self.tracked_by = tracked_by
        self.url = url
        self.category = category
        self.sub_category = sub_category
        self.quality = quality

        self.owner = owner
        self.torrent_link = torrent_link
        self.size = size
        self.comments = comments  # integer count
        self.times_completed = times_completed
        self.seeders = seeders
        self.leechers = leechers

        # needing additional requests
        self._magnet_link = None
        self._description = None
        self._files = None
        self._comments = None

    @property
    def magnet_link(self):
        raise NotImplementedError

    @property
    def files(self):
        raise NotImplementedError

    # to be updated
    def to_json(self):
        data = {'id': self.id, 'title': self.title, 'url': self.url, 'self.category': self.category, 'sub_category': self.sub_category,
                'torrent_link': self.torrent_link, 'magnet_link': self.magnet_link, 'size': self.size, 'user': self.user,
                'seeders': self.seeders, 'leechers': self.leechers}
        return json.dumps(data)

    def __repr__(self):
        return '{0} by {1}'.format(self.title, self.user)


class Demonoid:

    def __init__(self, base_url=BASE_URL):
        self.base_url = base_url

    # def recent(self, page=0):
        # return Recent(self.base_url, page)

    def top(self, category=0):
        return Top(self.base_url, category)
