from lxml import html
from requests import Session


BASE_URL = 'http://www.demonoid.pw/'


class URL:

    def __init__(self, base_url, path='', params={}):
        self.base_url = base_url or BASE_URL
        self.path = path
        self.params = params

        self._session = Session()
        self._DOM = None

    def add_params(self, params):
        self.params.update(params)
        return self

    def add_param(self, key, value):
        self.params[key] = value
        return self

    @property
    def url(self):
        return self.combine(self.path)

    def combine(self, path):
        url = self.base_url
        if url.endswith('/') and path.startswith('/'):
            url += path[1:]
        elif url.endswith('/') or path.startswith('/'):
            url += path
        else:
            url += '/' + path
        return url

    @property
    def DOM(self):
        if self._DOM is None:
            self.update_DOM()
        return self._DOM

    def update_DOM(self):
        response = self.fetch()
        self._DOM = html.fromstring(response.text)
        return self

    def __str__(self):
        return str(self.url)
