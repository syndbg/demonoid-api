import json
import re
import sys

from constants import BASE_URL, Category, SortBy, Language, State, TrackedBy, Quality
from utils import get_DOM_root, URL

if sys.version_info >= (3, 0):
    unicode = str


class List:
    # Captures the torrent lists from [4:-3], which is starting from the start torrent list comment and one after the end list comment.
    # A small mislead in the HTML, that's actually handled.
    # last() - 3 will be handled with Python slicing  in self.items()
    TORRENTS_XPATH = '//*[@id="fslispc"]/table/tr/td[1]/table[3]/tr/td/table/tr[position() > 4]'
    base_path = ''

    def __init__(self):
        self._DOM = None

    @property
    def items(self):
        if self._DOM is None:
            self.DOM = get_DOM_root(self.url)
        rows = self._get_torrent_rows(self.DOM)[:-3]  # trim non torrents
        return [self._build_torrent(row) for row in rows]

    def __iter__(self):
        return iter(self.items)

    def _get_torrent_rows(self, DOM):
        return DOM.xpath(self.TORRENTS_XPATH)  # the table with all torrent listing

    def _build_torrent(self, row, date):
        raise NotImplementedError


class Paginated(List):
    def __init__(self, *args, **kwargs):
        super(Paginated, self).__init__(*args, **kwargs)
        self._multipage = False

    def items(self):
        if self._multipage:
            while True:
                # Pool for more torrents
                items = super(Paginated, self).items()
                # Stop if no more torrents
                first = next(items, None)
                if first is None:
                    raise StopIteration()
                # Yield them if not
                else:
                    yield first
                    for item in items:
                        yield item
                # Go to the next page
                self.next()
        else:
            for item in super(Paginated, self).items():
                yield item

    def multipage(self):
        self._multipage = True
        return self

    def page(self, number=None):
        if number is None:
            return int(self.url.page)
        self.url.page = str(number)

    def next(self):
        self.page(self.page() + 1)
        return self

    def previous(self):
        self.page(self.page() - 1)
        return self


class Torrent:

    def __init__(self, date, id, title, tracked_by, url, category, sub_category,
                 quality, owner, torrent_link, size, comments, times_completed,
                 seeders, leechers):
        self.date = date  # as in today, Wednesday, Mar 04, 2015 and etc.
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
        self._datetime = None
        self._magnet_link = None
        self._description = None
        self._files = None
        self._comments = None

    @property
    def datetime(self):
        # exact date and time
        raise NotImplementedError

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

    def search(self, query, category=Category.ALL, language=Language.ALL,
               state=State.BOTH, quality=Quality.ALL, tracked_by=TrackedBy.BOTH, sort=SortBy.DATE, page=0, multipage=False):
        search = Search(self.base_url, query, page, order, category)
        if multipage:
            search.multipage()
        return search

    # def recent(self, page=0):
        # return Recent(self.base_url, page)

    def top(self, category=0):
        return Top(self.base_url, category)
