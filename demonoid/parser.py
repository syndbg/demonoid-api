from datetime import date, datetime

from .constants import Category, Language, Quality

__all__ = ['Parser']


class Parser:
    # Captures the torrent lists from [4:-3], which is starting from the start torrent list comment and one after the end list comment.
    # A small mislead in the HTML, that's actually handled.
    # last() - 3 will be handled with Python slicing  in `_get_date_row` method
    TORRENTS_LIST_XPATH = '//*[@id="fslispc"]/table/tr/td[1]/table[6]/tr/td/table/tr[position() > 4]'
    DATE_TAG_XPATH = './td[@class="added_today"]'
    DATE_STRPTIME_FORMAT = '%A, %b %d, %Y'
    FIRST_ROW_XPATH = './td/a | ./td/font'

    @staticmethod
    def get_torrents_rows(dom):
        return dom.xpath(Parser.TORRENTS_LIST_XPATH)[:-3]  # trim non-torrents

    @staticmethod
    def get_date_row(dom):
        return dom.xpath(Parser.DATE_TAG_XPATH)[0]

    @staticmethod
    def get_params(url, ignore_empty=True):
        try:
            params_start_index = url.index('?')
        except ValueError:
            params_start_index = 0
        params_string = url[params_start_index + 1:]

        params_dict = {}
        for pair in params_string.split('&'):
            param, value = pair.split('=')
            if value and not ignore_empty:
                params_dict[param] = value
        return params_dict

    @staticmethod
    def parse_date(row):
        text = row[0].text.split('Added on ')
        # Then it's 'Added today'. Hacky
        if len(text) < 2:
            return date.today()
        # Looks like ['', 'Thursday, Mar 05, 2015']
        return datetime.strptime(text[1], Parser.DATE_STRPTIME_FORMAT).date()

    @staticmethod
    def parse_first_row(row, url_instance):
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
    def parse_category_subcategory_and_or_quality(tags):
        output = {'category': None, 'subcategory': None, 'quality': None}
        for tag in tags:
            url = tag.get('href')
            if Parser.is_subcategory(url):
                output['subcategory'] = tag.text
            elif Parser.is_quality(url):
                output['quality'] = tag.text
            elif Parser.is_language(url):
                output['language'] = tag.text
        return output

    @staticmethod
    def is_subcategory(params):
        return Category.ALL != int(params['subcategory'])

    @staticmethod
    def is_quality(params):
        return Quality.ALL != int(params['quality'])

    @staticmethod
    def is_language(params):
        return Language.ALL != int(params['language'])

    @staticmethod
    def parse_torrent_link(tags):
        anchor_tags = tags.findall('./a')
        link_tag = anchor_tags[0] if len(anchor_tags) < 2 else anchor_tags[1]
        return link_tag.get('href')
