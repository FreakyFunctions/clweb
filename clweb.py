webpage = input("Scrape Website: ") # important we get webpage first!

# packages

import requests # Scraping
from bs4 import BeautifulSoup # Scraping
import re
import os
from urllib.parse import urlparse # Urlib
from requests.utils import cookiejar_from_dict # CookieJar
from fake_useragent import UserAgent # UserAgents

# session

session = requests.session() # start a new session

# cookies (you edit these)

cookies = { # cookies for the session, helpful for sites that need login
    "Cookie1": "test",
    "Cookie2": "test"
}

cookiejar = cookiejar_from_dict(cookies) # convert that to a cookie jar

session.cookies.update(cookiejar) # update cookies!!

# agent

ua = UserAgent() # create a user agent session
agent = ua.random # random user agent

# failed at adding selenium, sad moment.

headers = {"User-Agent": agent} # header

# request webpage

req = "" # blank saving for later

try:
    req = session.get(url=webpage, headers=headers) # set it to the contents we are scraping
except:
    print("Invalid url")
    exit(0)

# our things we will download

js = []
css = []
img = []

# start the scraping

web = BeautifulSoup(req.content, 'html5lib') # scraper

# the rest of this is undocumented

def startswith(string, prefix):
    if string is None or prefix is None:
        return False
    return string[:len(prefix)] == prefix

def endswith(string, suffix):
    if string is None or suffix is None:
        return False
    return string[-len(suffix):] == suffix

def get_url(url):
    if startswith(url, 'http'):
        return url
    return requests.compat.urljoin(webpage, url)
    
def create_folder_structure(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split('/')
    
    current_path = ""
    for part in path_parts[:-1]:
        current_path = os.path.join(current_path, part)
        if not os.path.exists(current_path):
            os.mkdir(current_path)
    
    return os.path.join(current_path, path_parts[-1])

for script in web.find_all('script', src=True):
    src = script.get('src')
    if endswith(src, '.js'):
        js.append(get_url(src))
        script['src'] = create_folder_structure(src)

for style in web.find_all('link', rel="stylesheet"):
    link = style.get('href')
    link2 = style.get('data-href')
    if endswith(link, '.css'):
        css.append(get_url(link))
        style['href'] = create_folder_structure(link)
    if endswith(link2, '.css'):
        css.append(get_url(link2))
        style['href'] = create_folder_structure(link2)

for im in web.find_all('img', src=True):
    link = im.get('src')
    img.append(get_url(link))
    im['src'] = create_folder_structure(link)

# we got the links and allat lets go ahead and just download em including the webpage

project = input("Folder Name: ")
this_file = input("Base Name (example: Scraped.html): ")

# last minute functions

def download_additional_assets(file_content, file_extension):
    additional_assets = []

    url_pattern = re.compile(r'url\([\'"]?(.*?)[\'"]?\)')
    
    for match in url_pattern.findall(file_content):
        if not startswith(match, 'data:'):
            asset_url = get_url(match)
            additional_assets.append(asset_url)
    
    for asset_url in additional_assets:
        try:
            save_path = create_folder_structure(asset_url)
            if not os.path.isfile(save_path):
                asset_data = requests.get(url=asset_url, headers=headers).content
                with open(save_path, 'wb') as file:
                    file.write(asset_data)
            
            file_content = file_content.replace(asset_url, save_path)
        except:
            print(f"Failed to download asset: {asset_url}")
    
    return file_content

# create folder

try:
    if os.path.isdir(project) == False:
        os.mkdir(project)

    os.chdir(project)
except:
    print("Failed to create folder")
    exit()

# html function thingies

def replace_urls(content, original_urls, local_paths):
    for original_url, local_path in zip(original_urls, local_paths):
        content = re.sub(re.escape(original_url), local_path, content)
    return content

def replace_in_file(file_path, original_urls, local_paths):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        updated_content = replace_urls(content, original_urls, local_paths)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        print(f"Replaced URLs in {file_path}")
    except Exception as e:
        print(f"Failed to replace URLs in {file_path}. Error: {e}")

def process_html(html_content, js, css, img):
    all_urls = js + css + img
    local_paths = [create_folder_structure(url) for url in all_urls]
    updated_html = replace_urls(html_content, all_urls, local_paths)
    
    return updated_html

# create html file

try:
    with open(this_file, 'w') as index:
        html_content = web.prettify()
        updated_html = process_html(html_content, js, css, img)
        index.write(updated_html)
        print('Created HTML file')
except Exception as e:
    print(f'Failed to create HTML file due to {e}')
    exit()

# script downloads

def extractfn(url):
    parsed = urlparse(url)
    path = parsed.path
    return os.path.basename(path)

for link in js:
    try:
        print(f"Downloading JS: {link}")
        save_path = create_folder_structure(link)
        if not os.path.isfile(save_path):
            js_content = requests.get(url=link, headers=headers).text
            js_content = download_additional_assets(js_content, ".js")
            with open(save_path, 'w') as file:
                file.write(js_content)
    except:
        print(f"Failed to download JS file: {link}")

# css downloads, hopefully easier?

for link in css:
    try:
        print(f"Downloading CSS: {link}")
        save_path = create_folder_structure(link)
        if not os.path.isfile(save_path):
            css_content = requests.get(url=link, headers=headers).text
            css_content = download_additional_assets(css_content, ".css")
            with open(save_path, 'w') as file:
                file.write(css_content)
    except:
        print(f"Failed to download CSS file: {link}")

# image.

for link in img:
    try:
        save_path = create_folder_structure(link)
        if not os.path.isfile(save_path):
            img_dl = requests.get(url=link, headers=headers).content
            with open(save_path, 'wb') as file:
                file.write(img_dl)
                print(f"Downloading IMG: {link}")
    except:
        print(f"Failed to download IMG file: {link}")

print("Finished Scraping")