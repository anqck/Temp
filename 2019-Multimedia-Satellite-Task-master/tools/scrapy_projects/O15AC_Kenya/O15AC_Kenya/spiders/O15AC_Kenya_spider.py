# -*- coding: utf-8 -*-
import scrapy
import html2text
from dateparser.date import DateDataParser
import dateparser
import logging


dparser = DateDataParser(
    languages=['en'],
    try_previous_locales=False
)

# Set html2text configuration
html2text.config.IGNORE_ANCHORS = True
html2text.config.IGNORE_IMAGES = True
html2text.config.IGNORE_EMPHASIS = True
html2text.config.BODY_WIDTH = 0


class EastAfrican(scrapy.Spider):
    """
    Spider for the local news site EastAfrican. Works the same for

    Business Daily (africa) --> contextsIds=539444 -->  74196 artikelen
    The citizen (Tanzania) --> contextsIds=1765046 --> 71839 artikelen
    Daily Nation kenya --> contextsIds=1148 --> 474712  artikelen
    The east african Kenya -->contextsIds=2456  52513 artikelen (vanaf deze site werken)
    Daily Monitor Uganda --> contextsIds=691150 --> 174375 artikelen
    """

    name = "Kenya_EastAfrican_spider"
    download_delay = 2

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.scrape_article)

    def scrape_article(self, response):
        #Article body
        article = response.xpath('//div[@class="story-view"]')

        #Title
        title_section = article.xpath('.//header//h2//text()')
        title = title_section.extract_first()

        #Date
        date_section = article.xpath('.//header//h6/text()') #Looks like Wednesday October 10 2018
        date_txt = date_section.extract_first()
        try:
            date = dparser.get_date_data(date_txt)['date_obj']
        except:
            date = None
        if date is not None:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = None

        #Text
        text = article.xpath('.//section[@class="body-copy"]//div//p//text()')
        text_section = text.extract()
        try:
            text_str = html2text.html2text(text_section).strip()
        except:
            try:
                text_str = str(text_section)
            except:
                text_str = None

        #Photos
        photos = [response.urljoin(l) for l in
                  article.xpath('.//header//img[@class="photo_article"]/@src'
        ).extract()]


        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}

class DailyNation(scrapy.Spider):
    """
    Spider for the local news site DailyNation - scraping only articles
    containing at least one of the following words:
    'flood',
    'floods',
    'flooding'.

    Websites from the same database that can be scraped similarly:

    Business Daily (africa) --> contextsIds=539444 -->  74196 artikelen
    The citizen (Tanzania) --> contextsIds=1765046 --> 71839 artikelen
    Daily Nation kenya --> contextsIds=1148 --> 474712  artikelen
    The east african Kenya -->contextsIds=2456  52513 artikelen (vanaf deze site werken)
    Daily Monitor Uganda --> contextsIds=691150 --> 174375 artikelen
    """

    name = "Kenya_DailyNation_spider"
    download_delay = 2

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.scrape_article)

    def scrape_article(self, response):
        #Article body
        article = response.xpath('//div[@class="story-view"]')

        #Title
        title_section = article.xpath('.//header//h2//text()')
        title = title_section.extract_first()

        #Date
        date_section = article.xpath('.//header//h6/text()') #Looks like Wednesday October 10 2018
        date_txt = date_section.extract_first()
        try:
            date = dparser.get_date_data(date_txt)['date_obj']
        except:
            date = None
        if date is not None:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = None

        #Text
        text = article.xpath('.//section[@class="body-copy"]//div//p//text()')
        text_section = text.extract()
        try:
            text_str = html2text.html2text(text_section).strip()
        except:
            try:
                text_str = str(text_section)
            except:
                text_str = None

        #Photos
        photos = [response.urljoin(l) for l in
                  article.xpath('.//header//img[@class="photo_article"]/@src'
        ).extract()]


        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}
