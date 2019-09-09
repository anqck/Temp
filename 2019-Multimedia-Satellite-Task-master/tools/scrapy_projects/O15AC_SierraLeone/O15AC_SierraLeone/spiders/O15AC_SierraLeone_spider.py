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

class Awoko(scrapy.Spider):
    """
    Spider for the local news site Awoko, Freetown Sierra Leone.
    """
    name = "SierraLeone_Awoko_spider"
    download_delay = 1
    #Scraping via the site of the Daily Nation, kenya, with context idea realting to the Daily Monitor, Uganda

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.scrape_article)

    def scrape_article(self, response):
        #Article body
        article = response.xpath('//div[@class="col1"]')

        #Title
        title_section = article.xpath('.//h2//text()')
        title = title_section.extract_first()

        #Text
        text = article.xpath('.//div[@class="entry"]')
        text_section = text.extract_first()
        text_str = html2text.html2text(text_section).strip()

        #Date
        full_text = article.xpath('.//div[@class="entry"]//p//text()').extract()
        date_txt = full_text[-1]
        #date_txt = text_section[-1][0]
        if date_txt is not None:
            date = dparser.get_date_data(date_txt)['date_obj']
        if date is None:
            date_txt = full_text[-2]
            date = dparser.get_date_data(date_txt)['date_obj']
            if date is None:
                date_txt = full_text[-3]
                date = dparser.get_date_data(date_txt)['date_obj']
        if date is not None:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = None

        #Photos
        photos = [response.urljoin(l) for l in
                  article.xpath('.//div[@class="entry"]//p//img/@src'
        ).extract()]


        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}
