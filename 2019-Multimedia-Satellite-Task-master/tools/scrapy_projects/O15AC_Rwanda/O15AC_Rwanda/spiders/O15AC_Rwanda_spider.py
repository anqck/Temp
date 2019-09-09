# -*- coding: utf-8 -*-
import scrapy
import html2text
from dateparser.date import DateDataParser
import re

dparser = DateDataParser(
    languages=['en'],
    try_previous_locales=False
)

# Set html2text configuration
html2text.config.IGNORE_ANCHORS = True
html2text.config.IGNORE_IMAGES = True
html2text.config.IGNORE_EMPHASIS = True
html2text.config.BODY_WIDTH = 0

p_smaps_cregex = re.compile('.*/post_part\d\.xml$')
source_regex = re.compile(
    r'\n((Source\b)|(Par\b))\s?:?\s?([^\n]{3,32})(\n|$)',
    re.IGNORECASE
    )


class TheNewTimes(scrapy.Spider):
    """
    Spider for the local news site The New times, Kigali Rwanda.
    """
    name = "Rwanda_TheNewTimes_spider"
    download_delay = 1
    #Scraping via the site of the Daily Nation, kenya, with context idea realting to the Daily Monitor, Uganda

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.scrape_article)


    def scrape_article(self, response):
        #Article body
        article = response.xpath('//div[@class="article-container"]')

        #Title
        title_section = article.xpath('.//h1[@class="page-heading"]//text()')
        title = title_section.extract_first()

        #Text
        text = article.xpath('.//div[@class="article-content clearfix"]//div[@class="field-item even"]')
        text_section = text.extract_first()
        text_str = html2text.html2text(text_section).strip()

        #Date
        date_section = article.xpath('.//span[@class="article-date"]//text()')
        date_txt = date_section.extract_first().split(':')[1]
        #date_txt = text_section[-1][0]
        if date_txt is not None:
            date = dparser.get_date_data(date_txt)['date_obj']
        if date is not None:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = None

        #Photos
        photos_section = article.xpath('.//div[@class = "article-media"]//img/@src')
        photos = photos_section.extract()

        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}
