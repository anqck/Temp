# Overview
This script provides you support for downloading articles and embedded images using the distributed files article and image links. Unfortunately, we are not allowed to distribute the original data and images, but we want you to simplify the process as much as possible. Please follow the instructions below. If you have any questions or problems, please contact benjamin.bischke@dfki.de.

# Setup:
##### 1. Environmental Setup:
* Install Python 3 on your system (https://www.python.org/downloads/) if you do not already use it.
* Make sure all required python packages are installed by executing: "pip3 install -r requirements.txt" in your console.

# Usage:
You can start downloading the images with the following call inside the tools folder:

    python download_images.py -f ./path/to/the/file/devset_image_links.jsonl -o /your/output/directory/NITD
With the first option you can specify the path to the distributed file of image links and with the second option the path to the output folder, in which the images should be stored.

You can start downloading the articles with the following call inside the tools folder:

    python download_articles.py -f ./path/to/the/file/devset_article_links.jsonl -o /your/output/directory/MFLE
With the first option you can specify the path to the distributed file of article links and with the second option the path to the output folder, in which articles and the accompanying images should be stored.
