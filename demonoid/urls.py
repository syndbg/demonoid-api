from lxml import html
from requests import Session


BASE_URL = 'http://www.demonoid.pw/'


class URL:

    """
       URL handles building urls with a base url, path and params.
       Also it makes requests to URLs and builds a DOM element with lxml.
       It shouldn't be used directly.
    """

    def __init__(self, base_url=None, path=None, params=None):
        """
        Creates a URL instance.
        :param base_url: The url to build from. Default is urls.BASE_URL
        :type base_url: str or None
        :param path: The path to append to the base url. Default is ''
        :type base_url: str or None
        :param params: The parameters to pass to the request. Default is {}
        :type params: dict or None
        """

        self.base_url = base_url or BASE_URL
        self.path = path or ''
        self.params = params or {}

        self._session = Session()
        self._DOM = None

    def add_params(self, params):
        """
        Updates existing `self.params` with given `params`.
        :param params: Parameters to add
        :type params: dict
        :return: self
        :rtype: URL
        """
        self.params.update(params)
        return self

    def add_param(self, key, value):
        """
        Updates or adds a `key`=`value` parameter in existing `self.params`.
        :param str key: Parameter name
        :param str value: Parameter value
        :return: self
        :rtype: URL
        """
        self.params[key] = value
        return self

    @property
    def url(self):
        """
        :return: Combined self.base_url and self.path
        :rtype: string
        """
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

    def fetch(self):
        response = self._session.get(self.url, params=self.params)
        response.raise_for_status()
        return response

    def __str__(self):
        return str(self.url)
