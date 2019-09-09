# -*- coding: utf-8 -*-
import scrapy
import html2text
from dateparser.date import DateDataParser
import dateparser
import logging
import re


dparser = DateDataParser(
    languages=['fr'],
    try_previous_locales=False
)

# Set html2text configuration
html2text.config.IGNORE_ANCHORS = True
html2text.config.IGNORE_IMAGES = True
html2text.config.IGNORE_EMPHASIS = True
html2text.config.BODY_WIDTH = 0


class AddisFortuneSpider(scrapy.Spider):
    """
    Spider for the local news site http://7sur7.cd/
    """
    name = 'Ethiopia_AddisFortune_spider'
    download_delay = 2

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.scrape_article)

    def scrape_article(self, response):
         #Article body
        article = response.xpath('//div[@id="newsarticletext"]')

        #Title
        title_section = article.xpath('.//h2//text()')
        title = title_section.extract_first()

        #Date
        date_section = article.xpath('.//div[@id="author-line"]//text()') #Looks like Wednesday October 10 2018
        date_long = date_section.extract_first().strip()
        z = date_long.split(' ')
        if len(z) > 6:
            date_txt = '{0} {1}'.format(z[3], z[5])
            print(date_txt)
            date = dparser.get_date_data(date_txt)['date_obj']
        else:
            date_txt = '{0} {1}'.format(z[2],z[3])
            date = dparser.get_date_data(date_txt)['date_obj']
        if date is None:
            date_long = date_section.extract()[3].strip()
            z = date_long.split(' ')
            if len(z) > 6:
                date_txt = '{0} {1}'.format(z[3], z[5])
                print(date_txt)
                date = dparser.get_date_data(date_txt)['date_obj']
            else:
                date_txt = '{0} {1}'.format(z[2],z[3])
                date = dparser.get_date_data(date_txt)['date_obj']




        if date is not None:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = None

        #Text

        text = response.xpath('//div[@id="newsarticletext"]')
        text_section = text.extract_first()
        if text_section is not None:
            text_str = html2text.html2text(text_section).strip()
        else:
            text_str = None

        #Photos
        photos = article.xpath('.//div[@class="item active"]//img/@src'
        ).extract()


        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}
