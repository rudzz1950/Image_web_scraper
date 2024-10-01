import argparse
import os
import sys
import json
from concurrent.futures import ThreadPoolExecutor
import filetype
import requests
from tqdm.contrib.concurrent import thread_map
from tqdm import tqdm

def get_download_path():
    if os.name == 'nt':
        import winreg
        sub_key = r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
        downloads_guid = '{374DE290-123F-4565-9164-39C4925E467B}'
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return location
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')


def get_default_dir(search_key: str):
    search_key = search_key.replace(" ", ".")
    default_dir = get_download_path()
    default_dir = os.path.join(default_dir, "google-image-scraper")
    default_dir = os.path.join(default_dir, search_key)
    return default_dir

def check_pos_int(val: int):
    val = int(val)
    if val > 0:
        return val
    else:
        raise ValueError

def get_arguments(argv=sys.argv):
    parser = argparse.ArgumentParser(description="Scrape google for images")
    parser.add_argument("keyword", 
                        help="the phrase used to find images",
                        type=str,
                        nargs=1)
    parser.add_argument("-c", "--count",
                        help="How many images to try to scrape",
                        type=check_pos_int,
                        nargs="?",
                        default=10)
    parser.add_argument("-d", "--directory",
                        help="where to save scraped images",
                        type=str,
                        nargs="?")
    parser.add_argument("-t", "--threads",
                        help="How many threads to spawn and download from",
                        type=check_pos_int,
                        nargs="?",
                        default=1)
    args = parser.parse_args(argv[1:])
    if args.directory is None:
        print(args.keyword[0])
        args.directory = get_default_dir(args.keyword[0])
    return args

def sanitize_query(query: str):
    return query.replace(' ', '+')

def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)

def add_filetype(file_path: str):
    try:
        img_type = filetype.guess(file_path).mime.split('/')[-1]
    except:
        img_type = 'jpg'
    new_path = '.'.join((os.path.splitext(file_path)[0], img_type))
    try:
        os.rename(file_path, new_path)
        return 0
    except Exception as err:
        eprint("Couldn't rename file at path {}".format(file_path))
        eprint(err)
        return 1

DEBUG = False

# search url and browser headers for spoofing
headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0'}
search_url = "https://www.google.com/search?q={}&tbm=isch&async=_id:islrg_c,_fmt:json&asearch=ichunklite&ijn={}"

def get_image_urls(query: str, page: int):
    all_images = {}
    try:
        response = requests.get(search_url.format(query, page), headers=headers)
        if DEBUG and response.status_code != 200:
            eprint("ERROR: Status code {} for page {}."
                   .format(response.status_code, page))
            
        if response.status_code == 200:
            json_text = response.content.decode('utf8').removeprefix(")]}'")
            json_data = json.loads(json_text)
            try:
                results = json_data['ichunklite']['results']
                for result in results:
                    id = result['image_docid']
                    image_url = result['viewer_metadata']['original_image']['url']
                    all_images[id] = image_url
            except Exception as err:
                if DEBUG:
                    eprint(f"ERROR: Issue parsing json file for page {page}")
                    eprint(err)
        else:
            if DEBUG:
                eprint("ERROR: Status code {} for page {}."
                       .format(response.status_code, page))
            
    except Exception as err:
        if DEBUG:
            eprint("ERROR: There was an issue requesting the json file")
            eprint(err)
    return all_images

def download_image(img_url: str, file_path: str):
    try:
        response = requests.get(img_url, headers=headers)
    except Exception as err:
        if DEBUG:
            eprint(f"ERROR: Can't request image url: {img_url}")
            eprint(err)
        return 1

    if response.status_code == 200:
        response_content_type = response.headers.get("content-type", '').lower()
        if "image" in response_content_type:
            with open(file_path, 'wb') as img:
                img.write(response.content)
            add_filetype(file_path)
            return 0
        else:
            if DEBUG:
                eprint("ERROR: Bad content-type\n{}"
                       .format(response_content_type))
            return 1
    else:
        if DEBUG:
            eprint("ERROR: Status code {} for url {}."
                   .format(response.status_code, url))
        return 1

def get_manifest(search_key: str, image_cnt: int):
    err_cnt = 0
    err_limit = 5

    img_manifest = {}
    manifest_len = image_cnt

    results_page = 0
    search_key = sanitize_query(search_key)
    while len(img_manifest.items()) < image_cnt:
        try:
            img_manifest.update(get_image_urls(search_key, results_page))
            results_page += 1
        except:
            print(f"err_cnt: {err_cnt}")
            err_cnt += 1
        if err_cnt > err_limit:
            eprint("Couldn't request all images")
            manifest_len = len(img_manifest.items())
            break

    print("Found {} of {} image sources".format(manifest_len, image_cnt))
    return list(img_manifest.items())[0:manifest_len]

def scrape_images(search_key, image_cnt, directory, threads):
    if DEBUG:
        print("savedir: {}".format(directory))
    if not os.path.exists(directory):
        os.makedirs(directory)

    id_url_manifest = get_manifest(search_key, image_cnt)
    with ThreadPoolExecutor(max_workers=threads) as pool:
        with tqdm(total=len(id_url_manifest)) as progress:
            futures = [] 
            for result in id_url_manifest:
                id: str = result[0]
                url: str = result[1]
                save_path = os.path.join(directory, id)
                future = pool.submit(download_image, url, save_path)
                future.add_done_callback(lambda p: progress.update(1))
                futures.append(future)
            for future in futures:
                result = future.result()
    return 0

if __name__ == "__main__":
    args = get_arguments(sys.argv)
    scrape_images(args.keyword[0], args.count, args.directory, args.threads)