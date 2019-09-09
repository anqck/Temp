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



class DNLocalSpider(scrapy.Spider):
    """
    Test spider for the local news section of dailynews.co.tz
    """
    name = "Tanzania_DN_spider"

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.scrape_article)

    def scrape_article(self, response):
        title_section = response.xpath('//h4[@class="entry-title"]//text()')
        title = title_section.extract_first()


        date_section = response.xpath('//div[@class="entry-main"]//div[@class="post-meta-date"]/text()')
        possible_dates = date_section.extract()
        for date_txt in possible_dates:
            date = dparser.get_date_data(date_txt)['date_obj']
            if date is not None:
                date_str = date.strftime('%Y-%m-%d')
                break
        else:
            date_str = None

        text = response.xpath('//div[@class="entry-main"]//div[@class="entry-content"]')
        text_section = text.extract_first()
        text_str = html2text.html2text(text_section).strip()

        img_section = response.xpath('//div[@class="entry-media"]//img/@src')
        img = img_section.extract_first()


        yield {'title': title, 'date': date_str, 'text': text_str, 'photos': [img], 'url': response.url}


class TheCitizen(scrapy.Spider):
    """
    Spider for the local news site the Citizen, Tanzania. Only scraping results
    containing at least one of the following words:
            'flood',
            'floods',
            'flooding'.

    Overview pages of other websites can be obtained using contextid of databases

    Business Daily (africa) --> contextsIds=539444 -->  74196 artikelen
    The citizen (Tanzania) --> contextsIds=1765046 --> 71839 artikelen
    Daily Nation kenya --> contextsIds=1148 --> 474712  artikelen
    The east african Kenya -->contextsIds=2456  52513 artikelen (vanaf deze site werken)
    Daily Monitor Uganda --> contextsIds=691150 --> 174375 artikelen

    Note that the retrieval of text, date, title and photos does work differently per site
    """
    name = "Tanzania_TheCitizen_spider"
    download_delay = 1
    #Scraping via the site of the Daily Nation, kenya, with context idea realting to the Daily Monitor, Uganda

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

        text = article.xpath('.//article[@class="article"]//section[@class="body-copy"]//div//p//text()')
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
                  article.xpath('.//header//div//img[@class="photo_article"]/@src'
        ).extract()]


        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}

class IPPMedia(scrapy.Spider):
    """
    Spider for the local news site IPP Media, only scraping articles that
    include at least one of the following keywords:
        - flood
        - floods
        - flooding
        - inundate
        - inundated
        - inundates
    """
    name = "Tanzania_IPPMedia_spider"
    download_delay = 1
    #Scraping via the site of the Daily Nation, kenya, with context idea realting to the Daily Monitor, Uganda

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.scrape_article)

    def scrape_article(self, response):
        #Article body
        article = response.xpath('//div[@role="main"]')

        #Title
        title_section = article.xpath('.//div[@class="contentin"]//div[@class="nodetitle"]//text()')
        title = title_section.extract_first()

        #Date
        date_section = article.xpath('.//div[@class="contentin"]//div[@class="ndate"]//text()') #Looks like Wednesday October 10 2018
        date_list = date_section.extract()
        date_txt = '{0} {1}'.format(date_list[0], date_list[1])
        print(date_txt)
        try:
            date = dparser.get_date_data(date_txt)['date_obj']
        except:
            date = None
        if date is not None:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = None

        #Text

        text = article.xpath('.//div[@class="field-items"]//p//text()')
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
                  article.xpath('.//div[@class="nimage"]//picture//img/@src'
        ).extract()]


        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}
