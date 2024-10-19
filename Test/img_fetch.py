#!/usr/bin/env python3
import os
import re
import requests
import threading
import posixpath
import urllib.parse
import argparse
import time
import hashlib
import pickle
import signal
import imghdr
from requests.exceptions import RequestException

# Config
output_dir = './output'
adult_filter = True
tried_urls = []
image_md5s = {}
in_progress = 0
urlopenheader = {'User-Agent': 'Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0'}

# Function to download images
def download(pool_sema: threading.Semaphore, url: str, output_dir: str):
    global in_progress

    if url in tried_urls:
        return
    pool_sema.acquire()
    in_progress += 1
    path = urllib.parse.urlsplit(url).path
    filename = posixpath.basename(path).split('?')[0]
    name, ext = os.path.splitext(filename)
    name = name[:36].strip()
    filename = name + ext

    try:
        response = requests.get(url, headers=urlopenheader, timeout=5)
        image = response.content
        if not imghdr.what(None, image):
            print(f'Invalid image, not saving {filename}')
            return

        md5_key = hashlib.md5(image).hexdigest()
        if md5_key in image_md5s:
            print(f'Image is a duplicate of {image_md5s[md5_key]}, not saving {filename}')
            return

        i = 0
        while os.path.exists(os.path.join(output_dir, filename)):
            if hashlib.md5(open(os.path.join(output_dir, filename), 'rb').read()).hexdigest() == md5_key:
                print(f'Already downloaded {filename}, not saving')
                return
            i += 1
            filename = f"{name}-{i}{ext}"

        image_md5s[md5_key] = filename

        with open(os.path.join(output_dir, filename), 'wb') as imagefile:
            imagefile.write(image)
        print(f"OK: {filename}")
        tried_urls.append(url)

    except RequestException as e:
        print(f"FAIL: {filename}, Error: {e}")
    finally:
        pool_sema.release()
        in_progress -= 1

# Function to fetch images from keyword search
def fetch_images_from_keyword(pool_sema: threading.Semaphore, keyword: str, output_dir: str, filters: str, limit: int):
    current = 0
    last = ''
    while True:
        time.sleep(0.1)

        if in_progress > 10:
            continue

        request_url = f"https://www.bing.com/images/async?q={urllib.parse.quote_plus(keyword)}&first={current}&count=35&adlt={adlt}&qft={'' if filters is None else filters}"
        response = requests.get(request_url, headers=urlopenheader)

        html = response.text
        links = re.findall(r'murl&quot;:&quot;(.*?)&quot;', html)

        if not links or links[-1] == last:
            return

        for index, link in enumerate(links):
            if limit is not None and current + index >= limit:
                return
            t = threading.Thread(target=download, args=(pool_sema, link, output_dir))
            t.start()
            current += 1

        last = links[-1]

# Function to back up download history
def backup_history(*args):
    with open(os.path.join(output_dir, 'download_history.pickle'), 'wb') as download_history:
        pickle.dump(tried_urls, download_history)
        pickle.dump(image_md5s, download_history)
    print('History dumped')
    if args:
        exit(0)

# Main execution
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='R3TR0_Ex.prog:img_fetch')
    parser.add_argument('-s', '--search-string', help='Keyword to search', required=False)
    parser.add_argument('-f', '--search-file', help='Path to a file containing search strings line by line', required=False)
    parser.add_argument('-o', '--output', help='Output directory', required=False)
    parser.add_argument('--adult-filter-on', help='Enable adult filter', action='store_true', required=False)
    parser.add_argument('--adult-filter-off', help='Disable adult filter', action='store_true', required=False)
    parser.add_argument('--filters', help='Any query-based filters to append, e.g. +filterui:license-L1', required=False)
    parser.add_argument('--limit', help='Maximum number of images to fetch.', required=False, type=int)
    parser.add_argument('--threads', help='Number of threads', type=int, default=20)
    args = parser.parse_args()

    if not args.search_string and not args.search_file:
        parser.error('Provide either search string or file containing search strings')

    if args.output:
        output_dir = args.output
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_dir_origin = output_dir
    signal.signal(signal.SIGINT, backup_history)

    try:
        with open(os.path.join(output_dir, 'download_history.pickle'), 'rb') as download_history:
            tried_urls = pickle.load(download_history)
            image_md5s = pickle.load(download_history)
    except (OSError, IOError):
        tried_urls = []

    adlt = 'off' if args.adult_filter_off else ''
    pool_sema = threading.BoundedSemaphore(args.threads)

    if args.search_string:
        fetch_images_from_keyword(pool_sema, args.search_string, output_dir, args.filters, args.limit)
    elif args.search_file:
        try:
            with open(args.search_file) as inputFile:
                for keyword in inputFile.readlines():
                    output_sub_dir = os.path.join(output_dir_origin, keyword.strip().replace(' ', '_'))
                    if not os.path.exists(output_sub_dir):
                        os.makedirs(output_sub_dir)
                    fetch_images_from_keyword(pool_sema, keyword, output_sub_dir, args.filters, args.limit)
                    backup_history()
                    time.sleep(10)
        except (OSError, IOError):
            print(f"Couldn't open file {args.search_file}")
