#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
 * This file is part of the Multimedia Satellite Task 2019 at Media Eval and
 * only for research and educational purposes.
 *
 * We kindly ask you to refer to the following publication in any publication
 * mentioning or employing this script:
 *
 * Benjamin Bischke, Patrick Helber, Erkan Basar, Simon Brugman, Zhengyu Zhao
 * and Konstantin Pogorelov. The Multimedia Satellite Task at MediaEval 2019:
 * Flood Severity Estimation. In Proc. of the MediaEval 2019 Workshop
 * (Oct. 27-29, 2019). Sophia-Antipolis, France.
 *
 * Copyright statement:
 * ====================
 * (c) 2019 by Benjamin Bischke (benjamin.bischke@dfki.de) and FloodTags
 *  https://github.com/multimediaeval/2019-Multimedia-Satellite-Task,
 *  http://www.multimediaeval.org/mediaeval2019/
 *
 * Updated: 16.05.19, 11:03
"""

from six import text_type
from scrapy_projects.O15AC_Kenya.O15AC_Kenya.spiders.O15AC_Kenya_spider import DailyNation
from scrapy_projects.O15AC_Tanzania.O15AC_Tanzania.spiders.Tanzania_spider import DNLocalSpider
from scrapy_projects.O15AC_Tanzania.O15AC_Tanzania.spiders.Tanzania_spider import TheCitizen
from scrapy_projects.O15AC_Tanzania.O15AC_Tanzania.spiders.Tanzania_spider import IPPMedia
from scrapy_projects.O15AC_Liberia.O15AC_Liberia.spiders.O15AC_Liberia_spider import DailyObserver
from scrapy_projects.O15AC_Kenya.O15AC_Kenya.spiders.O15AC_Kenya_spider import EastAfrican
from scrapy_projects.O15AC_Uganda.O15AC_Uganda.spiders.O15AC_Uganda_spider import NewVision
from scrapy_projects.O15AC_Uganda.O15AC_Uganda.spiders.O15AC_Uganda_spider import DailyMonitor
from scrapy_projects.O15AC_SierraLeone.O15AC_SierraLeone.spiders.O15AC_SierraLeone_spider import Awoko

import json
import os
try:
    from urllib.parse import urlparse
except ImportError:
    pass
    #from urlparse import urlparse  # Python 2
import sys
import os.path as op
from scrapy.crawler import CrawlerRunner, CrawlerProcess
from twisted.internet import reactor, defer
from download_images import main as main_download_images


DOMAIN_SPIDER_MAP = {
    "https://www.nation.co.ke/": DailyNation(),
    "http://www.theeastafrican.co.ke/": EastAfrican(),
    "https://www.liberianobserver.com/": DailyObserver(),
    "https://dailynews.co.tz/": DNLocalSpider(),
    "http://www.thecitizen.co.tz/": TheCitizen(),
    "http://www.monitor.co.ug/": DailyMonitor(),
    "https://www.newvision.co.ug/": NewVision(),
    "https://awoko.org/": Awoko(),
    "https://www.ippmedia.com/": IPPMedia(),
}


def extract_article_urls(json_fp):
    with open(json_fp, "r") as fp:
        lines = fp.read().splitlines()
        for idx, l in enumerate(lines):
            l = json.loads(l)
            yield l['article_id'], l['article_url']


def domain_name_from_url(url):
    return '{uri.scheme}://{uri.netloc}/'.format(uri=urlparse(url))


def get_tmp_fn(fp):
    return fp.replace(".jsonl", ".tmp.jsonl")


def crawl_articles(urls, outfile):
    runner = CrawlerProcess({
        'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
        'FEED_URI': get_tmp_fn(outfile),
        'FEED_FORMAT': 'jsonlines',
        'TELNETCONSOLE_ENABLED': False,
    })

    @defer.inlineCallbacks
    def crawl():
        for idx, (article_id, url) in enumerate(urls):
            domain_name = domain_name_from_url(url)
            if domain_name in DOMAIN_SPIDER_MAP:
                spider = DOMAIN_SPIDER_MAP[domain_name]
                yield runner.crawl(spider, start_urls=[url])
        reactor.stop()
    crawl()
    reactor.run()


def add_article_ids_to_file(article_urls, article_fp):
    tmp_fp = get_tmp_fn(article_fp)
    articles = read_article_metadata(tmp_fp)
    for article_id, url in article_urls:
        print(len(articles))
        for a in articles:
            if url == a["url"]:
                a["article_id"] = article_id
                break
    with open(article_fp, "w") as fp:
        for a in articles:
            fp.write(json.dumps(a) + "\n")
    os.remove(tmp_fp)


def read_article_metadata(article_fp):
    with open(article_fp, "r") as fp:
        lines = fp.read().splitlines()
    return [json.loads(l) for l in lines]


def ensure_dir(fp):
    if not op.exists(fp):
        os.makedirs(fp)
    return fp


def main(path_to_article_file, out_dir, image_only=False):
    ensure_dir(out_dir)

    if not image_only:
        out_file = os.path.join(out_dir, "articles_final.jsonl")

        article_urls = list(extract_article_urls(path_to_article_file))
        crawl_articles(article_urls, outfile=out_file)
        add_article_ids_to_file(article_urls, out_file)

    main_download_images(path_to_article_file, out_dir,
                         is_article_image=True)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        '-f', '--path-to-url-file',
        required=True,
        type=text_type,
        help='specifies the path to the article link file (the article and images to download)',
    )
    parser.add_argument(
        '-o', '--outdir',
        default='.',
        type=text_type,
        help='specifies the output directory in which article and images will be downloaded to',
    )

    parser.add_argument(
        '--image_only', '--image-only',
        action='store_true',
        help='sets the program to only download the images of the articles',
    )

    args, unknown = parser.parse_known_args()
    try:
        main(
            args.path_to_url_file,
            args.outdir,
            args.image_only
        )
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("Done")
