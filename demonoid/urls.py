from lxml import html
from requests import Session


BASE_URL = 'http://www.demonoid.pw/'


class URL:

    """
       The URL class handles building urls with a base url, path and params.
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
        :param params: The parameters to pass to the future request. Default is {}
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
        Using `self.combine`, gives the URL that will be used to make requests to.
        :return: Combined self.base_url and self.path
        :rtype: string
        """
        return self.combine(self.path)

    def combine(self, path):
        """
        Gives a combined `self.BASE_URL` with the given `path`.
        Used to build URLs without modifying the current `self.path`.
        Handles conflicts of trailing or preceding slashes.
        :param str path: `path` to append
        :return: combined `self.base_url` and given `path`.
        :rtype: str
        """
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
        """
        Lazy gets (or builds if needed) a DOM from response's text of combined URL.
        :return: DOM built from response
        :rtype: lxml.HtmlElement
        """
        if self._DOM is None:
            self.update_DOM()
        return self._DOM

    def update_DOM(self):
        """
        Makes a request and updates `self._DOM`.
        Worth using only if you manually change `self.base_url` or `self.path`.
        :return: self
        :rtype: url
        """
        response = self.fetch()
        self._DOM = html.fromstring(response.text)
        return self

    def fetch(self):
        """
        Makes a request to combined URL with `self._params` as parameters.
        If the URL server responds with Client or Server error, raises an exception.
        :return: returns the response from URL
        :rtype: requests.models.Response
        """
        response = self._session.get(self.url, params=self.params)
        response.raise_for_status()
        return response

    def __str__(self):
        """
        String representation of combined URL.
        However as it is now, it doesn't add the params from `self.params`.
        Sorry, it'll be fixed
        :return: combined URL.
        :rtype: str
        """
        return str(self.url)
