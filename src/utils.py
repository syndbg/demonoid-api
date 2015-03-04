import sys

# Kindly borrowed from https://github.com/karan/TPB.
# Props to Karan!
if sys.version_info >= (3, 0):
    class_type = type
else:
    from new import classobj
    class_type = classobj


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
        # dump current class name
        tree = '{0}: {1}\n'.format(cls.__name__, cls.value)
        for name in dir(cls):
            if not name.startswith('_'):
                attr = getattr(cls, name)
                output = repr(attr)
                if not isinstance(attr, ConstantType):
                    output = '{0}: {1}'.format(name, output)
                # indent all child attrs
                tree += '\n'.join([' ' * 4 + line
                                   for line in output.splitlines()]) + '\n'
        return tree

    def __str__(cls):
        return repr(cls)

    @property
    def value(cls):
        try:
            return cls.__value__
        except:
            return None


Constants = ConstantType('Constants', (object,), {})
