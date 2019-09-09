# -*- coding: utf-8 -*-
import scrapy
import html2text
from dateparser.date import DateDataParser

dparser = DateDataParser(
    languages=['en'],
    try_previous_locales=False
)

# Set html2text configuration
html2text.config.IGNORE_ANCHORS = True
html2text.config.IGNORE_IMAGES = True
html2text.config.IGNORE_EMPHASIS = True
html2text.config.BODY_WIDTH = 0


class DailyObserver(scrapy.Spider):
    """
    Spider for the local news site The Daily Observer, Monrovia- Liberia.
    """
    name = "Liberia_DailyObserver_spider"
    download_delay = 0.5

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.scrape_article)

    def scrape_article(self, response):
        #Article body
        article = response.xpath('//div[@class="td-ss-main-content"]')

        #Title
        title_section = article.xpath('.//h1[@class="entry-title"]//text()')
        title = title_section.extract_first()

        #Text
        text = article.xpath('.//div[@class="td-post-content"]')
        text_section = text.extract_first()
        text_str = html2text.html2text(text_section).strip()

        #Date
        date_section = article.xpath('.//span[@class="td-post-date"]//time/@datetime').extract()
        date_txt = date_section[0]
        if date_txt is not None:
            date = dparser.get_date_data(date_txt)['date_obj']
        if date is not None:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = None

        #Photos
        photos = [response.urljoin(l) for l in
                  article.xpath('.//div[@class="td-post-featured-image"]//img/@src'
        ).extract()]


        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}
