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
 * Updated: 16.05.19, 11:04
"""

import os
import requests
import shutil
import sys
import urllib
import os.path as op
import json
from six import text_type
import io
from PIL import Image


try:
    from urllib.request import urlretrieve  # Python 3
except ImportError:
    from urllib import urlretrieve  # Python 2


def ensure_dir(fp):
    if not op.exists(fp):
        os.makedirs(fp)
    return fp


def is_image_truncated(path):
    try:
        with io.FileIO(path) as f:
            data = f.read()
            buf = io.BytesIO(data)
            Image.open(buf).load()
            return False
    except OSError as err:
        return True


def img_path_for_url(outdir, image_id, img_url):
    suffix = ".jpg" if img_url.endswith(".jpg") else ".png"
    return os.path.join(outdir, "images", str(image_id) + suffix)


def download_resource(image_id, img_url, image_path):
    print("Downloading ID: ", image_id, "\t", img_url)
    response = requests.get(img_url, stream=True)
    success = response.status_code == 200
    if success:
        with open(image_path, 'wb') as out_file:
            response.raw.decode_content = True
            shutil.copyfileobj(response.raw, out_file)
        response._content_consumed = True


def download_images(image_id, image_url, outdir):
    try:
        try:
            img_url = image_url.replace(".JPG?itok*", ".jpg")\
                                .replace(".jpg?itok*", ".jpg")
            image_path = img_path_for_url(outdir, image_id, img_url)
            if not os.path.exists(image_path):
                download_resource(image_id, image_url, image_path)
            else:
                if is_image_truncated(image_path):
                    print("Already downloaded but corrupted ID:", image_id)
                    os.remove(image_path)
                    download_resource(image_id, image_url, image_path)
                else:
                    print("Already downloaded ID:", image_id)
        except Exception as exp:
            print(exp)
            sys.stdout.write("Error while downloading Image! Please check this article."
                             "(%s)\n" % (exp))
    except urllib.error.HTTPError as er:
        print(er)
        pass


def extract_imgage_urls(json_fp, is_article_image=False):
    with open(json_fp, "r") as fp:
        lines = fp.read().splitlines()
        for idx, l in enumerate(lines):
            l = json.loads(l)
            if is_article_image:
                yield l['article_id'], l['img_url']
            else:
                yield l['image_id'], l['image_url']


def main(json_fp,
         out_dir,
         is_article_image=False
):
    ensure_dir(os.path.join(out_dir, "images"))

    for image_id, image_url in extract_imgage_urls(json_fp, is_article_image=is_article_image):
        download_images(image_id, image_url, out_dir)


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
        help='specifies the path to the image link file (the images to download)',
    )
    parser.add_argument(
        '-o', '--outdir',
        default='.',
        type=text_type,
        help='specifies the output directory in which images will be downloaded',
    )

    args, unknown = parser.parse_known_args()
    try:
        main(
            args.path_to_url_file,
            args.outdir,
        )
    except KeyboardInterrupt:
        pass
    finally:
        sys.stdout.write("Done")

