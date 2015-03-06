import datetime
import json
import re
import sys

from constants import Category, SortBy, Language, State, TrackedBy, Quality
from utils import URL

if sys.version_info >= (3, 0):
    unicode = str


class List:
    # Captures the torrent lists from [4:-3], which is starting from the start torrent list comment and one after the end list comment.
    # A small mislead in the HTML, that's actually handled.
    # last() - 3 will be handled with Python slicing  in self.items()
    TORRENTS_XPATH = '//*[@id="fslispc"]/table/tr/td[1]/table[6]/tr/td/table/tr[position() > 4]'
    DATE_TAG_XPATH = './td[@class="added_today"]'
    DATE_STRPTIME_FORMAT = '%A, %b %d, %Y'
    base_path = ''

    def __init__(self, url):
        self._url = url
        self._torrents = None

    @property
    def items(self):
        if self._torrents is None:
            rows = self._get_torrent_rows(self._url.DOM)[:-3]  # trim non-torrents
            self._torrents = self._build_torrents(rows)
        return self._torrents

    def __iter__(self):
        return iter(self.items)

    def _get_torrent_rows(self, DOM):
        return DOM.xpath(self.TORRENTS_XPATH)  # the table with all torrent listing

    def _build_torrents(self, rows):
        torrents = []
        current_date = None
        for row in rows:
            date_row = self._get_date_row(row)
            if date_row:
                current_date = self._parse_date(date_row)
            else:
                torrent = self._build_torrent(row, current_date)
                torrents.append(torrent)
        return torrents

    def _parse_date(self, row):
        text = row[0].text.split('Added on ')
        # Then it's 'Added today'. Hacky
        if len(text) < 2:
            return datetime.date.today()
        # Looks like
        # ['', 'Thursday, Mar 05, 2015']
        return datetime.datetime.strptime(text[1], self.DATE_STRPTIME_FORMAT).date()

    def _get_date_row(self, row):
        return self._url.DOM.xpath(self.DATE_TAG_XPATH)[0]

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
