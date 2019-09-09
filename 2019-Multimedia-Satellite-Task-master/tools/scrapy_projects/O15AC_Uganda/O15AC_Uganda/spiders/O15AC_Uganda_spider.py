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


class DailyMonitor(scrapy.Spider):
    """
    Spider for the local news site Daily Monitor, Uganda. Only scraping results
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
    name = "Uganda_DailyMonitor_spider"
    download_delay = 2
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
        #text = article.xpath('.//article[@class="article"]//div[@itemprop="body-copy^"]//p//text()')
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
#                  article.xpath('.//header//div[@itemprop="image"]//img/@src'
        ).extract()]


        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}


class NewVision(scrapy.Spider):
    """
    Spider for the local news site New Vision, Uganda. Only scraping results
    containing 'a' (so all articles)
    """
    name = "Uganda_NewVision_spider"
    download_delay = 1
    #Scraping via the site of the Daily Nation, kenya, with context idea realting to the Daily Monitor, Uganda

    def start_requests(self):
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.scrape_article)

    def scrape_article(self, response):
        #Article body
        article = response.xpath('//div[@id="wrapper-container"]')

        #Title
        title_section = article.xpath('.//div[@class="top-story-block"]//h1//text()')
        title = title_section.extract_first()

        #Date
        date_section = article.xpath('.//div[@class="top-story-block"]//div[@class="publish-date"]//p//text()') #Looks like Wednesday October 10 2018
        date_long = date_section.extract_first().split(' ')[1:] # looks like 'Added 3rd September 2018 12:11 PM'
        date_txt = '{0} {1} {2}'.format(date_long[0], date_long[1], date_long[2])
        if date_txt is not None:
            date = dparser.get_date_data(date_txt)['date_obj']
        if date is not None:
            date_str = date.strftime('%Y-%m-%d')
        else:
            date_str = None

        #Text

        text = article.xpath('.//div[@class="article-content"]')
        text_section = text.extract_first()
        try:
            text_str = html2text.html2text(text_section).strip()
        except:
            try:
                text_str = str(text_section)
            except:
                text_str = None

        #Photos
        photos = [response.urljoin(l) for l in
                  article.xpath('.//div[@class="article-image"]//img/@src'
        ).extract()]


        yield {'title': title,
               'date': date_str,
               'text': text_str,
               'photos': photos,
               'language' : 'en',
               'url': response.url}
