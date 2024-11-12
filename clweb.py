import os
import re
import requests
from urllib.parse import urlparse, urljoin
from requests.utils import cookiejar_from_dict
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

# User inputs
webpage = input("Scrape Website: ")
project_folder = input("Folder Name: ")
html_filename = input("Base Name (example: Scraped.html): ")

# Initialize session and headers
session = requests.Session()
cookies = {"Cookie1": "test", "Cookie2": "test"}
session.cookies.update(cookiejar_from_dict(cookies))

ua = UserAgent()
headers = {"User-Agent": ua.random}

# Ensure the project folder exists
os.makedirs(project_folder, exist_ok=True)

# Helper functions
def is_valid_url(url):
    return url and url.startswith('http')

def resolve_url(url):
    """Resolve a relative URL to an absolute one based on the webpage's base URL."""
    return urljoin(webpage, url)

def create_save_path(url):
    """Create the directory structure and return the local file path to save the asset."""
    parsed_url = urlparse(url)
    save_path = os.path.join(project_folder, *parsed_url.path.strip('/').split('/'))
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    return save_path

def replace_urls(content, original_urls, local_paths):
    """Replace all asset URLs in the content with their corresponding local file paths."""
    for original_url, local_path in zip(original_urls, local_paths):
        content = re.sub(re.escape(original_url), local_path, content)
    return content

def download_asset(url, save_path, binary=False):
    """Download an asset from the given URL and save it to the specified local path."""
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        mode = 'wb' if binary else 'w'
        with open(save_path, mode) as file:
            file.write(response.content if binary else response.text)
        print(f"Downloaded: {url}")
    except requests.RequestException as e:
        print(f"Failed to download {url}: {e}")

def convert_to_local_path(url):
    """Generate a local path relative to the project folder for a given URL."""
    parsed_url = urlparse(url)
    return os.path.join(*parsed_url.path.strip('/').split('/'))

def collect_assets(soup, assets, tag, attribute, category, extensions):
    """Collect assets (e.g., scripts, stylesheets, images) from the HTML soup."""
    for element in soup.find_all(tag, {attribute: True}):
        url = element.get(attribute)
        if url and any(url.endswith(ext) for ext in extensions):
            full_url = resolve_url(url)
            assets[category].append(full_url)
            element[attribute] = convert_to_local_path(full_url)

def download_and_process_html(url, save_path):
    """Fetch and process an HTML page, downloading its assets and saving them locally."""
    try:
        response = session.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html5lib')
    except requests.RequestException as e:
        print(f"Failed to fetch {url}: {e}")
        return

    # Collect assets
    assets = {"js": [], "css": [], "img": [], "other": []}
    collect_assets(soup, assets, 'script', 'src', 'js', ['.js'])
    collect_assets(soup, assets, 'link', 'href', 'css', ['.css'])
    collect_assets(soup, assets, 'img', 'src', 'img', [])
    collect_assets(soup, assets, 'a', 'href', 'other', [])
    collect_assets(soup, assets, 'link', 'href', 'other', [])

    # Download assets
    for category, urls in assets.items():
        for asset_url in urls:
            local_save_path = create_save_path(asset_url)
            is_binary = category == 'img'
            download_asset(asset_url, local_save_path, binary=is_binary)

    # Save the processed HTML
    with open(save_path, 'w', encoding='utf-8') as file:
        file.write(soup.prettify())
    print(f"Saved HTML file: {save_path}")

# Main script
main_html_path = os.path.join(project_folder, html_filename)
download_and_process_html(webpage, main_html_path)

print("Scraping completed.")