webpage = input("Scrape Website: ")

# packages

import http.cookiejar
import requests
from bs4 import BeautifulSoup
import re
import os
from urllib.parse import urlparse
import http
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from chromedriver_py import binary_path

# cookies (you edit these)

cookies = {"test": "hi"} # basically just look up how to use cookies, will be helpful for services that need logins

# agent

ua = UserAgent()
agent = ua.random

# selenium

opt = Options()
opt.add_argument(f"user-agent={agent}")
svc = webdriver.ChromeService(executable_path=binary_path)
driver = webdriver.Chrome(options=opt, service=svc)
driver.add_cookie(cookies)

# request webpage

req = ""

try:
    req = driver.get(webpage)
except:
    print("Invalid url")
    exit(0)

# our things we will download

js = []
css = []
img = []

# start the scraping

web = BeautifulSoup(req.page_source, 'html5lib')

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

for script in web.find_all('script', src=True):
    src = script.get('src')
    if endswith(src, '.js'):
        js.append(get_url(src))

for style in web.find_all('link', rel="stylesheet"):
    link = style.get('href')
    if endswith(link, '.css'):
        css.append(get_url(link))

for im in web.find_all('img', src=True):
    link = im.get('src')
    img.append(get_url(link))

# we got the links and allat lets go ahead and just download em including the webpage

project = input("Folder Name: ")
this_file = input("Base Name (example: Scraped.html): ")

# last minute functions

def create_folder_structure(url):
    parsed_url = urlparse(url)
    path_parts = parsed_url.path.strip("/").split('/')
    
    current_path = ""
    for part in path_parts[:-1]:
        current_path = os.path.join(current_path, part)
        if not os.path.exists(current_path):
            os.mkdir(current_path)
    
    return os.path.join(current_path, path_parts[-1])

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

# create html file

try:
    with open(this_file, 'w', encoding='utf-8') as index:
        html_content = web.prettify()

        for link in js + css + img:
            local_path = create_folder_structure(link)
            html_content = html_content.replace(link, local_path)
        index.write(html_content)
        print(f"Main HTML file '{this_file}' created successfully.")
except Exception as e:
    print(f"Failed to create main HTML file '{this_file}'. Error: {e}")
    exit(0)

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
    except:
        print(f"Failed to download IMG file: {link}")
