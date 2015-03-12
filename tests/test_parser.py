from datetime import date, datetime
from sys import version_info
from unittest import TestCase


if version_info >= (3, 3):
    from unittest import mock
else:
    import mock

from lxml.html import HtmlElement
from requests import Session, HTTPError, Response

from demonoid.constants import Category, Quality, Language
from demonoid.parser import Parser
from demonoid.urls import Url


class OfflineParserTests(TestCase):
    """
       Test Parser against offline HTML pages and with lots of mocked behavior.
    """

    @classmethod
    def setUpClass(cls):
        cls.url = Url(path='files')
        cls.rows = Parser.get_torrents_rows(cls.url.DOM)
        cls.date_td = Parser.get_date_td(cls.rows[0])

    def test_get_torrents_rows(self):
        first_row = self.rows[0]
        last_row = self.rows[-1]
        self.assertIsInstance(self.rows, list)
        # manually confirm that it  captures correct range of torrent rows
        self.assertTrue('added_today' in first_row.getchildren()[0].get('class'))
        # however I noticed that some torrents may have no properties and this test will fail.
        # Lets hope Demonoid staff fixes that. Meanwhile let this fail.
        self.assertIsNotNone(last_row.find('./td/a[@class="subcategory"]'))
        # usual amount of torrent rows per page. Hacky assertion.
        self.assertEqual(101, len(self.rows))

    def test_get_date_td_when_theres_such(self):
        self.assertIsInstance(self.date_td, HtmlElement)

    def test_get_date_when_theres_none(self):
        self.assertIsNone(Parser.get_date_td(self.rows[1]))

    def test_get_params_with_absolute_url(self):
        url = 'http://www.demonoid.pw/files/?category=0&subcategory=0&quality=0&seeded=2&external=2&query=&sort='
        expected_params = {'category': 0, 'subcategory': 0, 'quality': 0, 'seeded': 2, 'external': 2, 'query': '', 'sort': ''}
        self.assertDictEqual(expected_params, Parser.get_params(url))

    def test_get_params_with_empty_url(self):
        self.assertDictEqual({}, Parser.get_params(''))

    def test_get_params_with_query_only(self):
        url = '?category=0&subcategory=0&quality=0&seeded=2&external=2&query=&sort='
        expected_params = {'category': 0, 'subcategory': 0, 'quality': 0, 'seeded': 2, 'external': 2, 'query': '', 'sort': ''}
        self.assertDictEqual(expected_params, Parser.get_params(url))

    def test_get_params_with_ignore_empty(self):
        url = '?category=0&subcategory=0&quality=&seeded=2&external=2&query=&sort='
        expected_params = {'category': 0, 'subcategory': 0, 'seeded': 2, 'external': 2}
        self.assertDictEqual(expected_params, Parser.get_params(url, ignore_empty=True))

    def test_parse_date_with_date_today(self):
        result = Parser.parse_date(self.date_td)
        self.assertIsInstance(result, date)
        self.assertEqual(result, date.today())

    def test_parse_date_with_string_date(self):
        date_str = 'Monday, Mar 09, 2015'
        expected_date = datetime.strptime(date_str, Parser.DATE_STRPTIME_FORMAT).date()

        mocked_td = mock.Mock(text='Added on ' + date_str)
        actual_date = Parser.parse_date(mocked_td)
        self.assertEqual(expected_date, actual_date)

    def test_parse_first_row_without_external_torrent_property(self):
        category_url = 'http://www.demonoid.pw/files/?uid=0&category=0&subcategory=0&language=0&seeded=0&quality=0&query=&sort='
        title = 'Example torrent'
        torrent_url = '/files/details/012345/012345678901/'
        # mock it to test logic and to avoid unpredictable behavior of the online version
        mocked_category_td = mock.Mock(**{'get.return_value': '/files/?uid=0&category=0&subcategory=0&language=0&seeded=0&quality=0&query=&sort='})
        mocked_torrent_anchor_td = mock.Mock(text=title, **{'get.return_value': torrent_url})
        mocked_tags = [mocked_category_td, mocked_torrent_anchor_td]
        mocked_first_row = mock.Mock(**{'xpath.return_value': mocked_tags})

        result = Parser.parse_first_row(mocked_first_row, self.url)
        mocked_first_row.xpath.assert_called_with(Parser.FIRST_ROW_XPATH)
        self.assertEqual(5, len(result))
        self.assertEqual('012345/012345678901', result[0])
        self.assertEqual(title, result[1])
        self.assertEqual('Demonoid', result[2])
        mocked_category_td.get.assert_called_with('href')
        self.assertEqual(category_url, result[3])
        self.assertEqual(self.url.combine(torrent_url), result[4])

        # assert online version returns correct amount of properties
        online_result = Parser.parse_first_row(self.rows[1], self.url)
        self.assertEqual(5, len(online_result))

    def test_parse_first_row_with_external_torrent_property(self):
        category_url = 'http://www.demonoid.pw/files/?uid=0&category=0&subcategory=0&language=0&seeded=0&quality=0&query=&sort='
        title = 'Example torrent'
        torrent_url = '/files/details/012345/012345678901/'
        # mock it to test logic and to avoid unpredictable behavior of the online version
        mocked_category_td = mock.Mock(**{'get.return_value': '/files/?uid=0&category=0&subcategory=0&language=0&seeded=0&quality=0&query=&sort='})
        mocked_torrent_anchor_td = mock.Mock(text=title, **{'get.return_value': torrent_url})
        mocked_tags = [mocked_category_td, mocked_torrent_anchor_td, 'give external property!']
        mocked_first_row = mock.Mock(**{'xpath.return_value': mocked_tags})

        result = Parser.parse_first_row(mocked_first_row, self.url)
        mocked_first_row.xpath.assert_called_with(Parser.FIRST_ROW_XPATH)
        self.assertEqual(5, len(result))
        self.assertEqual('012345/012345678901', result[0])
        self.assertEqual(title, result[1])
        self.assertEqual('(external)', result[2])
        mocked_category_td.get.assert_called_with('href')
        self.assertEqual(category_url + '&external=1', result[3])
        self.assertEqual(self.url.combine(torrent_url), result[4])

        # assert online version returns correct amount of properties
        online_result = Parser.parse_first_row(self.rows[1], self.url)
        self.assertEqual(5, len(online_result))

    @mock.patch('demonoid.parser.Parser.parse_torrent_link', return_value='http://www.demonoid.pw/files/download/1234567/')
    @mock.patch('demonoid.parser.Parser.parse_torrent_properties', return_value=['Audio books', 'Adventure', 'AAC', 'Bulgarian'])
    def test_parse_second_row(self, patched_parse_torrent_properties, patched_parse_torrent_link):
        mocked_user_anchor = mock.Mock(**{'text_content.return_value': 'example', 'get.return_value': '/users/example'})
        mocked_user_info = mock.Mock(**{'find.return_value': mocked_user_anchor})

        mocked_size = mock.Mock(text='1.47GB')
        mocked_comments = mock.Mock(text=0)
        mocked_times_completed = mock.Mock(text=1)
        mocked_seeders = mock.Mock(text=5)
        mocked_leechers = mock.Mock(text=10)

        mocked_tags = ['properties', mocked_user_info, 'torrent link',
                       mocked_size, mocked_comments, mocked_times_completed, mocked_seeders, mocked_leechers]
        mocked_second_row = mock.Mock(**{'findall.return_value': mocked_tags})

        result = Parser.parse_second_row(mocked_second_row, self.url)

        mocked_second_row.findall.assert_called_with('./td')
        patched_parse_torrent_properties.assert_called_with(mocked_tags[0])
        mocked_user_info.find.assert_called_with('./a')
        self.assertTrue(mocked_user_anchor.text_content.called)
        mocked_user_anchor.get.assert_called_with('href')
        patched_parse_torrent_link.assert_called_with(mocked_tags[2])

        self.assertEqual(12, len(result))
        self.assertEqual('Audio books', result[0])
        self.assertEqual('Adventure', result[1])
        self.assertEqual('AAC', result[2])
        self.assertEqual('Bulgarian', result[3])
        self.assertEqual(mocked_user_anchor.text_content(), result[4])
        self.assertEqual(self.url.combine('/users/example'), result[5])
        self.assertEqual(patched_parse_torrent_link.return_value, result[6])
        self.assertEqual(mocked_size.text, result[7])
        self.assertEqual(mocked_comments.text, result[8])
        self.assertEqual(mocked_times_completed.text, result[9])
        self.assertEqual(mocked_seeders.text, result[10])
        self.assertEqual(mocked_leechers.text, result[11])
        # assert online version returns correct amount of properties
        online_result = Parser.parse_second_row(self.rows[2], self.url)
        self.assertEqual(12, len(online_result))

    def test_parse_torrent_properties_when_all_given(self):
        mocked_td_category = mock.Mock(text='Audio', **{'get.return_value': 'category=1&subcategory=0&language=0&quality=0'})
        mocked_td_subcategory = mock.Mock(text='Adventure', **{'get.return_value': 'category=1&subcategory=10&language=0&quality=0'})
        mocked_td_quality = mock.Mock(text='Unbelievable', **{'get.return_value': 'category=1&subcategory=0&language=0&quality=10'})
        mocked_td_language = mock.Mock(text='Hard to understand', **{'get.return_value': 'category=1&subcategory=5&language=6&quality=0'})

        mocked_properties = [mocked_td_category, mocked_td_subcategory, mocked_td_quality, mocked_td_language]
        expected = {'category': mocked_td_category.text, 'subcategory': mocked_td_subcategory.text,
                    'quality': mocked_td_quality.text, 'language': mocked_td_language.text}
        self.assertDictEqual(expected, Parser.parse_torrent_properties(mocked_properties))
        mocked_td_subcategory.get.assert_called_with('href')
        mocked_td_quality.get.assert_called_with('href')
        mocked_td_language.get.assert_called_with('href')

    def test_parse_torrent_properties_when_some_are_missing(self):
        # however category is always present
        mocked_td_category = mock.Mock(text='Audio', **{'get.return_value': 'category=1&subcategory=0&language=0&quality=0'})
        mocked_td_subcategory = mock.Mock(text='Adventure', **{'get.return_value': 'category=1&subcategory=10&language=0&quality=0'})
        mocked_properties = [mocked_td_category, mocked_td_subcategory]

        expected = {'category': mocked_td_category.text, 'subcategory': mocked_td_subcategory.text,
                    'quality': None, 'language': None}
        self.assertDictEqual(expected, Parser.parse_torrent_properties(mocked_properties))
        mocked_td_subcategory.get.assert_called_with('href')

    def test_parse_torrent_link_if_only_one_anchor_tag(self):
        url = 'http://www.demonoid.pw/files/download/1234567/'
        mocked_anchor = mock.Mock(**{'get.return_value': url})
        mocked_anchors = [mocked_anchor]
        mocked_td = mock.Mock(**{'findall.return_value': mocked_anchors})

        result = Parser.parse_torrent_link(mocked_td)
        mocked_td.findall.assert_called_with('./a')
        mocked_anchor.get.assert_called_with('href')
        self.assertEqual(url, result)

    def test_parse_torrent_link_if_two_anchor_tags(self):
        url = 'http://www.demonoid.pw/files/download/1234567/'
        mocked_anchor_with_ad = mock.Mock(**{'get.return_value': 'damn ads'})
        mocked_anchor = mock.Mock(**{'get.return_value': url})
        mocked_anchors = [mocked_anchor_with_ad, mocked_anchor]
        mocked_td = mock.Mock(**{'findall.return_value': mocked_anchors})

        result = Parser.parse_torrent_link(mocked_td)
        mocked_td.findall.assert_called_with('./a')
        mocked_anchor.get.assert_called_with('href')
        self.assertEqual(url, result)

    def test_is_subcategory(self):
        params = {'category': 0, 'subcategory': 0, 'quality': 0, 'seeded': 2, 'external': 2, 'query': '', 'sort': ''}
        self.assertFalse(Parser.is_subcategory(params))
        params['subcategory'] = Category.APPLICATIONS.LINUX
        self.assertTrue(Parser.is_subcategory(params))

    def test_is_quality(self):
        params = {'quality': 0, 'subcategory': 0, 'quality': 0, 'seeded': 2, 'external': 2, 'query': '', 'sort': ''}
        self.assertFalse(Parser.is_quality(params))
        params['quality'] = Quality.PICTURES.HIGH_RESOLUTION
        self.assertTrue(Parser.is_quality(params))

    def test_is_language(self):
        params = {'language': 0, 'subcategory': 0, 'quality': 0, 'seeded': 2, 'external': 2, 'query': '', 'sort': ''}
        self.assertFalse(Parser.is_language(params))
        params['language'] = Language.BULGARIAN
        self.assertTrue(Parser.is_language(params))


class OnlineParserTests(TestCase):
    """
        Test Parser against offline Demonoid HTML pages.
    """

    def setUp(self):
        pass

    def test_get_torrent_rows(self):
        pass

    def test_get_date_td(self):
        pass

    def test_get_params(self):
        pass

    def test_parse_date(self):
        pass

    def test_parse_first_row(self):
        pass

    def test_parse_second_row(self):
        pass

    def test_parse_category_subcategory_and_or_quality(self):
        pass

    def test_parse_torrent_link(self):
        pass

    def test_is_subcategory(self):
        pass

    def test_is_quality(self):
        pass

    def test_is_language(self):
        pass
