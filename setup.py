from setuptools import setup
import os


VERSION = '0.0.1'
README = None
with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()


setup(
    name='demonoid-api',
    version=VERSION,
    packages=['src'],
    install_requires=['requests'],
    include_package_data=True,
    license='MIT',
    description='Unofficial demonoid.pw API.',
    long_description=README,
    url='https://github.com/syndbg/demonoid-api',
    author='Anton Antonov',
    author_email='syndbe@gmail.com',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Browsers',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Utilities',
    ],
    platforms='any',
    keywords='pypi demonoid api rest client torrent',
)
