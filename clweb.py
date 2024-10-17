# clweb is still a work of progress read the readme

# webpage to save/settings (we will get the another linked stuff with it like logos, etc.)

webpage = "https://liablelua.com/"
headers = {'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.135 Safari/537.36 Edge/12.246"}

# packages

import requests
from bs4 import BeautifulSoup

# request webpage

req = requests.get(url=webpage, headers=headers)

# our things we will download
js = []
css = []

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
    link = script.get('link')
    css.append(get_url(link))

# we got the links and allat lets go ahead and just download em including the webpage

project = "Github Scrape Test"
this_file = "git.html"

# import os

import os

# create folder

os.mkdir(project)
os.chdir(project)

# create html file

index = open(this_file, 'w')
index.write(web.prettify())
index.close()

# import js beautifier

import jsbeautifier
from urllib.parse import urlparse

# script downloads

def extractfn(url):
    parsed = urlparse(url)
    path = parsed.path
    return os.path.basename(path)

def weird_bugfix(scr): # possible use for style saving, idfk what this dumbass bug is
    editstr1 = scr[1:]
    editstr2 = editstr1[1:]
    editstr3 = editstr2[:-1] 
    return editstr3

for link in js:
    script_dl = requests.get(url=link, headers=headers).content
    file = open(extractfn(link), 'w')
    file.write(jsbeautifier.beautify(weird_bugfix(str(script_dl).strip())))
    file.close()

# import css

import cssbeautifier

# css downloads, hopefully easier?

for link in css:
    style_dl = requests.get(url=link, headers=headers).content
    file = open(extractfn(link), 'w')
    file.write(cssbeautifier.beautify(str(style_dl).strip()))
    file.close()