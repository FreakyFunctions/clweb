# clweb is still a work of progress read the readme

# webpage to save/settings (we will get the another linked stuff with it like logos, etc.)

webpage = input("Scrape Website: ")
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

# packages

import requests
from bs4 import BeautifulSoup

# request webpage

req = ""

try:
    req = requests.get(url=webpage, headers=headers)
except:
    print("Invalid url")
    exit(0)

# our things we will download
js = []
css = []
img = []

# start the scraping

web = BeautifulSoup(req.content, 'html5lib')

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

# import os

import os

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
    if os.path.isfile(this_file) == False:
        index = open(this_file, 'w')
        index.write(web.prettify())
        index.close()
except:
    print("Failed to create main html file")
    exit()

# urllib

from urllib.parse import urlparse

# script downloads

def extractfn(url):
    parsed = urlparse(url)
    path = parsed.path
    return os.path.basename(path)

for link in js:
    if os.path.isfile(extractfn(link)) == False:
        script_dl = requests.get(url=link, headers=headers).content
        file = open(extractfn(link), 'wb')
        file.write(script_dl)
        file.close()

# css downloads, hopefully easier?

for link in css:
    if os.path.isfile(extractfn(link)) == False:
        style_dl = requests.get(url=link, headers=headers).content
        file = open(extractfn(link), 'wb')
        file.write(style_dl)
        file.close()

# image.

for link in img:
    if os.path.isfile(extractfn(link)) == False:
        img_dl = requests.get(url=link, headers=headers)
        test = img_dl.content
        file = open(extractfn(link), 'wb')
        file.write(test)
        file.close()