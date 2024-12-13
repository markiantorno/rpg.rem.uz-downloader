import os
import time
import random
import bs4
import requests
from requests.exceptions import RequestException
from urllib.parse import urljoin

# Configure rate-limiting
REQUEST_DELAY = 1  # Base delay in seconds between requests
MAX_RETRIES = 5    # Number of retries for failed requests

# Ensure target directory exists
def create_directory(directory):
    os.makedirs(directory, exist_ok=True)

# Parse URL recursively
def parse_url(directory, url):
    create_directory(directory)
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = bs4.BeautifulSoup(response.text, "html.parser")

        for link in soup.find_all("a"):
            href = link.get("href")
            if not href or href == "../":
                continue

            full_url = urljoin(url, href)
            if href.endswith(('.pdf', '.png', '.zip', '.txt', '.html', '.jpg', '.jpeg')):
                filename = link.get_text(strip=True)
                download_file(directory, full_url, filename)
            else:
                subdirectory = os.path.join(directory, link.get_text(strip=True))
                parse_url(subdirectory, full_url)

    except RequestException as e:
        print(f"Failed to access {url}. Error: {e}")

# Download file with retries and rate-limiting
def download_file(directory, url, filename):
    create_directory(directory)
    file_path = os.path.join(directory, filename)

    if os.path.exists(file_path):
        print(f"Skipping {file_path}, as it already exists...")
        return

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            print(f"Attempting to download {url} (Attempt {attempt}/{MAX_RETRIES})...")
            response = requests.get(url, timeout=10)
            if response.status_code == 429:  # Rate limit hit
                retry_after = int(response.headers.get("Retry-After", REQUEST_DELAY))
                print(f"Rate limit hit. Retrying after {retry_after} seconds...")
                time.sleep(retry_after)
                continue

            response.raise_for_status()
            with open(file_path, mode='wb') as local_file:
                local_file.write(response.content)
            print(f"Downloaded: {file_path}")
            break
        except RequestException as e:
            print(f"Failed to download {url}. Error: {e}")
            if attempt < MAX_RETRIES:
                delay = REQUEST_DELAY * (2 ** (attempt - 1)) + random.uniform(0, 1)
                print(f"Retrying in {delay:.2f} seconds...")
                time.sleep(delay)
            else:
                print(f"Giving up on {url} after {MAX_RETRIES} attempts.")

if __name__ == "__main__":
    target_url = "https://the-eye.eu/public/Books/rpg.rem.uz/Dungeons%20%26%20Dragons/"
    target_dir = "Dungeons & Dragons"
    
    parse_url(target_dir, target_url)

