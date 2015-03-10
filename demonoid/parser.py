from datetime import date, datetime

from .constants import Category, Language, Quality


class Parser:
    """
       The Parser is a static class, responsible for parsing HTML elements and text.
       It shouldn't be used directly.

       :attr: TORRENTS_LIST_XPATH is a XPATH expression used to capture the torrent lists in range [4:-3] from the HTML parent table element.
        However last() - 3 will be handled with Python slicing  in `get_torrents_rows` method as it's more DRY than writing a really longer XPATH expression.
       :attr: DATE_TAG_XPATH is a XPATH expression used to capture the HTML parent `tr`'s  `td` element holding the date row.
       :attr: DATE_STRPTIME_FORMAT is a `datetime`-compliant string used to parse the DATE_TAG's date text.
       :attr: FIRST_ROW_XPATH is a XPATH used to capture the first torrent's table row's id, title, tracked_by, category_url and torrent_url (torrents consist of 2 table rows).
    """

    TORRENTS_LIST_XPATH = '//*[@id="fslispc"]/table/tr/td[1]/table[6]/tr/td/table/tr[position() > 4]'
    DATE_TAG_XPATH = './td[@class="added_today"]'
    DATE_STRPTIME_FORMAT = '%A, %b %d, %Y'
    FIRST_ROW_XPATH = './td/a | ./td/font'

    @staticmethod
    def get_torrents_rows(dom):
        """
        Static method that gets the torrent list rows from the given `dom` by running `TORRENTS_LIST_XPATH` and trims the last() -3 non-torrent rows, which are actually sorting preferences rows.

        :param lxml.HtmlElement dom: the dom to operate on
        :return: returns torrent rows
        :rtype: list of lxml.HtmlElement
        """
        return dom.xpath(Parser.TORRENTS_LIST_XPATH)[:-3]  # trim non-torrents

    @staticmethod
    def get_date_row(dom):
        """
        Static method that gets the torrent data element containing the torrents' date. Executes `DATE_TAG_XPATH` on given `dom`.

        :param lxml.HtmlElement dom: the dom to operate on
        :return: table data containg torrents' date
        :rtype: lxml.HtmlElement
        """
        return dom.xpath(Parser.DATE_TAG_XPATH)[0]

    @staticmethod
    def get_params(url, ignore_empty=True):
        """
        Static method that parses a given `url` and retrieves `url`'s parameters. Could also ignore empty value parameters.
        Handles parameters-only urls as `q=banana&peel=false`.

        :param str url: url to parse
        :param bool ignore_empty: ignore empty value parameter or not
        :return: dictionary of params and their values
        :rtype: dict
        """
        try:
            params_start_index = url.index('?')
        except ValueError:
            params_start_index = 0
        params_string = url[params_start_index + 1:]

        params_dict = {}
        for pair in params_string.split('&'):
            param, value = pair.split('=')
            if value and ignore_empty:
                params_dict[param] = value
            else:
                params_dict[param] = value
        return params_dict

    @staticmethod
    def parse_date(table_data):
        """
        Static method that parses a given table data element with `Url.DATE_STRPTIME_FORMAT` and creates a `date` object from td's text contnet.

        :param lxml.HtmlElement table_data: table_data tag to parse
        :return: date object from td's text date
        :rtype: datetime.date
        """
        text = table_data[0].text.split('Added on ')
        # Then it's 'Added today'. Hacky
        if len(text) < 2:
            return date.today()
        # Looks like ['', 'Thursday, Mar 05, 2015']
        return datetime.strptime(text[1], Parser.DATE_STRPTIME_FORMAT).date()

    @staticmethod
    def parse_first_row(row, url_instance):
        """
        Static method that parses a given table row element by executing `Parser.FIRST_ROW_XPATH` and scrapping torrent's
        id, title, tracked by status, category url and torrent url. Used specifically with a torrent's first table row.

        :param lxml.HtmlElement row: row to parse
        :param urls.Url url_instance: Url used to combine base url's with scrapped links from tr
        :return: list of scrapped id, title, tracked by status, category url and torrent url
        :rtype: list
        """
        tags = row.xpath(Parser.FIRST_ROW_XPATH)
        category_url = url_instance.combine(tags[0].get('href'))
        title = tags[1].text
        # work with the incomplete URL to get str_id
        torrent_url = tags[1].get('href')
        str_id = torrent_url.split('details/')[1]
        # complete the torrent URL with BASE_URL
        torrent_url = url_instance.combine(torrent_url)

        # means that torrent is external
        if len(tags) == 3:
            # monkey patch the missing external query param
            category_url += '&external=1'
            tracked_by = '(external)'
        else:
            tracked_by = 'Demonoid'
        return [str_id, title, tracked_by, category_url, torrent_url]

    @staticmethod
    def parse_second_row(row, url):
        """
        Static method that parses a given table row element by using helper methods `Parser.parse_category_subcategory_and_or_quality`,
         `Parser.parse_torrent_link` and scrapping torrent's
        category, subcategory, quality, user, user url, torrent link, size, comments, times completed, seeders and leechers. Used specifically with a torrent's second table row.

        :param lxml.HtmlElement row: row to parse
        :param urls.Url url_instance: Url used to combine base url's with scrapped links from tr
        :return: list of scrapped category, subcategory, quality, user, user url, torrent link, size, comments, times completed, seeders and leechers
        :rtype: list
        """
        tags = row.findall('./td')
        category, subcategory, quality = Parser.parse_category_subcategory_and_or_quality(tags[0])

        user_info = tags[1].find('./a')
        user = user_info.text_content()
        user_url = url.combine(user_info.get('href'))

        # Two urls - one is spam, second is torrent url.
        # Don't combine it with BASE_URL, since it's an absolute url.
        torrent_link = Parser.parse_torrent_link(tags[2])
        size = tags[3].text
        comments = tags[4].text
        times_completed = tags[5].text
        seeders = tags[6].text
        leechers = tags[7].text
        return [category, subcategory, quality, user, user_url, torrent_link,
                size, comments, times_completed, seeders, leechers]

    @staticmethod
    def parse_category_subcategory_and_or_quality(table_datas):
        """
        Static method that parses a given list of table data elements and using helper methods
        `Parser.is_subcategory`, `Parser.is_quality`, `Parser.is_language`, collect torrent properties.

        :param list of lxml.HtmlElement table_datas: table_datas to parse
        :return: list of identified category, subcategory and quality.
        :rtype: dict
        """
        output = {'category': None, 'subcategory': None, 'quality': None}
        for td in table_datas:
            url = td.get('href')
            if Parser.is_subcategory(url):
                output['subcategory'] = td.text
            elif Parser.is_quality(url):
                output['quality'] = td.text
            elif Parser.is_language(url):
                output['language'] = td.text
        return output

    @staticmethod
    def parse_torrent_link(table_datas):
        """
        Static method that parses list of table data, finds all anchor elements
        and gets the torrent url. However the torrent url is usually hidden behind a fake spam ad url,
        this is handled.

        :param list of lxml.HtmlElement table_datas: table_datas to parse
        :return: torrent url from anchor (link) element
        :rtype: str
        """
        anchors = table_datas.findall('./a')
        link_tag = anchors[0] if len(anchors) < 2 else anchors[1]
        return link_tag.get('href')

    @staticmethod
    def is_subcategory(params):
        """
        Static method that given a dict of parameters, casts parameters' subcategory value to int
        and compares it to default search query value - Category.ALL. Which is also the default `ALL` search query value for all subcategories.

        :param dict params: parameters to get subcategory value from
        :return: if given parameters' subcategory is different from Category.ALL or not
        :rtype: bool
        """
        return Category.ALL != int(params['subcategory'])

    @staticmethod
    def is_quality(params):
        """
        Static method that given a dict of parameters, casts parameters' quality value to int
        and compares it to default search query value - Quality.ALL.

        :param dict params: parameters to get quality value from
        :return: if given parameters' quality is different from Quality.ALL or not
        :rtype: bool
        """
        return Quality.ALL != int(params['quality'])

    @staticmethod
    def is_language(params):
        """
        Static method that given a dict of parameters, casts parameters' language value to int
        and compares it to default search query value - Language.ALL.

        :param dict params: parameters to get language value from
        :return: if given parameters' language is different from Language.ALL or not
        :rtype: bool
        """
        return Language.ALL != int(params['language'])
