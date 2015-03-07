import json
import sys

from constants import Category, SortBy, Language, State, TrackedBy, Quality
from parser import Parser
from utils import URL

if sys.version_info >= (3, 0):
    unicode = str


class Torrent:

    def __init__(self, date, id, title, tracked_by, category_url, url, category, subcategory,
                 quality, user, user_url, torrent_link, size, comments, times_completed,
                 seeders, leechers):
        self.date = date
        self.id = id  # As '3159986/003226642800/'
        self.title = title
        self.tracked_by = tracked_by
        self.category_url = category_url
        self.url = url
        self.category = category
        self.subcategory = subcategory or Category.ALL
        self.quality = quality or Quality.ALL

        self.user = user
        self.user_url = user_url
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
        raise NotImplementedError
        # return json.dumps(data)

    def __repr__(self):
        return '{0} by {1}'.format(self.title, self.user)


class List:
    base_path = ''

    def __init__(self, url):
        self._url = url
        self._torrents = None

    @property
    def items(self):
        if self._torrents is None:
            self._update_torrents()
        return self._torrents

    def _update_torrents(self):
        rows = Parser.get_torrent_rows(self._url.DOM)
        self._torrents = self._build_torrents(rows)
        return self

    def __iter__(self):
        return iter(self.items)

    def _build_torrents(self, rows):
        torrents = []
        current_date = None
        torrent_info = []  # 2 rows hold info about 1 torrent
        for row in rows:
            date_row = Parser.get_date_row(row)
            if date_row:
                current_date = Parser.parse_date(date_row)
            elif len(torrent_info) < 2:
                torrent_info.append(row)
            else:
                torrent = self._build_torrent(torrent_info, current_date)
                torrents.append(torrent)
                torrent_info = []
        return torrents

    def _build_torrent(self, rows, date):
        first_row_args = Parser.parse_first_row(rows[0])
        second_row_args = Parser.parse_second_row(rows[1])
        args = [date] + first_row_args + second_row_args
        return Torrent(*args)


class Paginated(List):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._multipage = False

    def items(self):
        if self._torrents is None:
            self._update_torrents()
            if self._multipage:
                self.next()
                new_torrents =
                while True:

        return self._torrents

    def multipage(self):
        self._multipage = True
        return self

    def page(self, number=None):
        if number is None:
            return int(self.url.page)
        self.url.page = str(number)
        return self

    def next(self):
        self.page(self.page() + 1)
        return self

    def previous(self):
        self.page(self.page() - 1)
        return self


class Demonoid:

    def __init__(self, base_url=''):
        self.url = URL(base_url)

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
