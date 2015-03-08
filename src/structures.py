import json
import sys

from .exceptions import HeadReachedException, InvalidSearchParameterException
from .constants import Category, SortBy, Language, State, TrackedBy, Quality
from .parser import Parser
from .urls import URL


class Torrent(object):

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


class List(object):
    base_path = ''

    def __init__(self, url):
        url.path = self.base_path
        self._url = url
        self._torrents = None

    @property
    def items(self):
        if self._torrents is None:
            self._update_torrents()
        return self._torrents

    def _update_torrents(self):
        rows = Parser.get_torrents_rows(self._url.DOM)
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

    def __init__(self, url, page=None, multipage=None):
        super(Paginated, self).__init__(url)
        self._url.params['page'] = page or 1
        self.multipage = multipage or False

    @property
    def _page(self):
        return self._url.params['page']

    @property
    def items(self):
        if self._torrents is None:
            self._update_torrents()
            if self.multipage:
                while True:
                    self.next()
                    self._url.update_DOM()
                    new_torrents = Parser.get_torrents_rows(self._url.DOM)
                    if not new_torrents:
                        break
                    self._torrents.extend(new_torrents)
        return self._torrents

    def make_multipage(self):
        self.multipage = True
        return self

    @property
    def page(self):
        return self._url.params['page']

    @page.setter
    def page(self, value):
        if not isinstance(value, int):
            value = int(value)
        self._url.params['page'] = value

    def next(self):
        self.page(self.page + 1)
        return self

    def previous(self):
        if self.page <= 1:
            raise HeadReachedException('Reached head of paginated list. Can\'t go to previous.')
        self.page(self.page - 1)
        return self


class Search(Paginated):
    base_path = '/files'

    def __init__(self, **kwargs):
        url = kwargs.pop('url')
        page = kwargs.pop('page', None)
        multipage = kwargs.pop('multipage', None)
        super(Search, self).__init__(url, page, multipage)
        self.modify(kwargs)

    def modify(self, **params):
        self._validate_params(params)
        self._url.params.update(params)

    def _validate_params(self, params):
        valid_params = ('query', 'category', 'subcategory', 'quality',
                        'language', 'seeded', 'external', 'sort', 'search')
        for param in params:
            if param not in valid_params:
                name = params[param]
                valid_params_names = ','.join(valid_params)
                raise InvalidSearchParameterException('{} is not a valid search criteria. \
                                              The valid parameters are {1}'.format(name, valid_params_names))

    @property
    def query(self):
        return self._url.params['query']

    @query.setter
    def query(self, value):
        self._url.params['query'] = value

    # TO-DO. Needs update in Constants type and Torrent members, before it's possible.
    def filter(self, **params):
        self._validate_search_params(params)
        raise NotImplementedError


class Demonoid(object):

    def __init__(self, base_url=''):
        self.url = URL(base_url)

    def search(self, **kwargs):
        search = Search(**kwargs)
        return search
