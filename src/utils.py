import sys

from lxml import html
from requests import get

if sys.version_info >= (3, 0):
    class_type = type
else:
    from new import classobj
    class_type = classobj


def get_DOM_root(url):
    response = get(url, headers={'User-Agent': 'Demonoid unofficial API client', 'origin_req_host': 'demonoid.pw'})
    return html.fromstring(response.text)


class URL:

    def __init__(self, base_url, path, params):
        self.base_url = base_url
        self.path = path
        self.params = params

    def add_params(self, params):
        self.params.update(params)
        return self

    def add_param(self, key, value):
        self.params[key] = value
        return self

    @property
    def url(self):
        url = self.base_url
        if not (url.endswith('/') or self.path.startswith('/')):
            url += '/' + self.path
        return url

    def __str__(self):
        return str(self.url)


# Borrowed from https://github.com/karan/TPB and modified.
# Props to Karan.
class ConstantType(type):

    """
    Tree representation metaclass for class attributes. Metaclass is extended
    to all child classes too.
    """
    def __new__(cls, clsname, bases, dct):
        """
        Extend metaclass to all class attributes too.
        """
        attrs = {}
        for name, attr in dct.items():
            if isinstance(attr, class_type):
                # substitute attr with a new class with Constants as
                # metaclass making it possible to spread this same method
                # to all child classes
                attr = ConstantType(
                    attr.__name__, attr.__bases__, attr.__dict__)
            attrs[name] = attr
        return super(ConstantType, cls).__new__(cls, clsname, bases, attrs)

    def __repr__(cls):
        """
        Tree representation of class attributes. Child classes are also
        represented.
        """
        str_representation = '{0}: {1}\n'.format(cls.__name__, cls.value)
        for name in dir(cls):
            if not name.startswith('_'):
                attr = getattr(cls, name)
                output = repr(attr)
                if not isinstance(attr, ConstantType):
                    output = '{0}: {1}'.format(name, output)
                # indent all child attrs
                str_representation += '\n'.join([' ' * 4 + line
                                                 for line in output.splitlines()]) + '\n'
        return str_representation

    def __str__(cls):
        return repr(cls)

    @property
    def value(cls):
        try:
            return cls.__value__
        except:
            return None

    @property
    def is_child(cls):
        return cls.value is None


Constants = ConstantType('Constants', (object,), {})