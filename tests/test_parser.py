from datetime import date, datetime
from sys import version_info
from unittest import TestCase


if version_info >= (3, 3):
    from unittest import mock
else:
    import mock

from lxml.html import HtmlElement
from requests import Session, HTTPError, Response

from demonoid.parser import Parser
from demonoid.urls import Url


class OfflineParserTests(TestCase):
    """
        Test Parser against offline Demonoid HTML pages.
    """

    def setUp(self):
        pass

    def test_get_torrent_rows(self):
        pass

    def test_get_date_row(self):
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


class OnlineParserTests(TestCase):
    """
       Test Parser against the current online Demonoid web server.
       Tests may be a little harder to understand at first due to the usage of `setUpClass`,
       but that's to prevent spamming Demonoid's web server.
    """

    @classmethod
    def setUpClass(cls):
        cls.url = Url(path='files')
        cls.rows = Parser.get_torrents_rows(cls.url.DOM)
        cls.date_row = Parser.get_date_row(cls.rows[0])

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

    def test_get_date_row_when_theres_such(self):
        self.assertIsInstance(self.date_row, HtmlElement)

    def test_get_date_when_theres_none(self):
        self.assertIsNone(Parser.get_date_row(self.rows[1]))

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
        result = Parser.parse_date(self.date_row)
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
        mocked_category_td = mock.Mock(**{'get.return_value': category_url})
        mocked_torrent_anchor_td = mock.Mock(text=title, **{'get.return_value': torrent_url})
        mocked_tags = [mocked_category_td, mocked_torrent_anchor_td]
        mocked_first_row = mock.Mock(**{'xpath.return_value': mocked_tags})

        result = Parser.parse_first_row(mocked_first_row, self.url)
        mocked_first_row.xpath.assert_called_with(Parser.FIRST_ROW_XPATH)
        self.assertEqual(5, len(result))
        self.assertEqual('012345/012345678901/', result[0])
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
        mocked_category_td = mock.Mock(**{'get.return_value': category_url})
        mocked_torrent_anchor_td = mock.Mock(text=title, **{'get.return_value': torrent_url})
        mocked_tags = [mocked_category_td, mocked_torrent_anchor_td, 'give external property!']
        mocked_first_row = mock.Mock(**{'xpath.return_value': mocked_tags})

        result = Parser.parse_first_row(mocked_first_row, self.url)
        mocked_first_row.xpath.assert_called_with(Parser.FIRST_ROW_XPATH)
        self.assertEqual(5, len(result))
        self.assertEqual('012345/012345678901/', result[0])
        self.assertEqual(title, result[1])
        self.assertEqual('(external)', result[2])
        mocked_category_td.get.assert_called_with('href')
        self.assertEqual(category_url + '&external=1', result[3])
        self.assertEqual(self.url.combine(torrent_url), result[4])

        mocked_first_row = mock.Mock()
        self.assertEqual(5, len(result))
        # assert online version returns correct amount of properties
        online_result = Parser.parse_first_row(self.rows[1], self.url)
        self.assertEqual(5, len(online_result))

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
