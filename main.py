import os
import bs4
import requests


def parse_url(directory, url):
    os.makedirs(directory, exist_ok=True)
    r = requests.get(url)
    data = bs4.BeautifulSoup(r.text, "html.parser")
    for link in data.find_all("a"):
        if link.getText() == '../' or link["href"].endswith('.iso'):
            pass
        elif link["href"].endswith(('.pdf', '.png', '.zip', '.txt', '.html', '.jpg', '.jpeg')):
            download_pdf_from_url(directory, url + link["href"], link.contents[0])
        else:
            parse_url(directory + '/' + link.getText(), url + link["href"])


def download_pdf_from_url(directory, url, filename):
    request = requests.get(url)
    file_path = directory + '/' + filename
    if os.path.exists(file_path):
    	print(f'Skipping {file_path}, as it already exists...')
    else:
    	print(f'Downloading from {url} into {directory}...')
    	with open(file_path, mode='wb') as local_file:
        	local_file.write(request.content)
            

target_url = "https://the-eye.eu/public/Books/rpg.rem.uz/Dungeons%20%26%20Dragons/"
target_dir = 'Dungeons & Dragons'

parse_url(target_dir, target_url)
