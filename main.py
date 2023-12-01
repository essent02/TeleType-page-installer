import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

def download_file(url, folder, folder_name):
    local_filename = url.split('/')[-1]
    create_name_folder = os.path.join(folder_name, folder)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    if not os.path.exists(create_name_folder):
        os.makedirs(create_name_folder)
    local_path = os.path.join(folder_name, folder, local_filename)
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

def remove_script_tags(soup):
    for script in soup.find_all("script"):
        script.decompose()
    return soup

def update_html(soup, base_url, folder_name):
    for link in soup.find_all("link", rel="stylesheet"):
        css_url = urljoin(base_url, link['href'])
        css_filename = download_file(css_url, 'css', folder_name)
        link['href'] = os.path.join('css', css_filename)
    
    for img in soup.find_all("img"):
        img_url = urljoin(base_url, img['src'])
        img_filename = download_file(img_url, 'images', folder_name)
        img['src'] = os.path.join('images', img_filename)

    return soup

def remove_elements(soup):
    classes_list = ["loader", "spacer", "menu","article__status", "article__author", "article__badges", "article__info"]
    for i in classes_list:
        for element in soup.find_all(class_=i):
            element.decompose()
    
    return soup

def extract_images_from_noscript(soup):
    noscript_tags = soup.find_all('noscript')
    for noscript in noscript_tags:
        for img in noscript.find_all('img'):
            noscript.insert_before(img)
        noscript.decompose()
    return soup

def download_teletype_page(url):
    response = requests.get(url)
    response.raise_for_status()

    name = url.split("/")
    folder_name = name[-2]
    file_name = name[-1]

    soup = BeautifulSoup(response.content, 'html.parser')
    soup = update_html(soup, url, folder_name)
    soup = remove_script_tags(soup)
    soup = remove_elements(soup)
    soup = extract_images_from_noscript(soup)

    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    file_path = os.path.join(folder_name, f"{file_name}.html")
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(str(soup))

    print(f"File saved to {file_path}")

if __name__ == "__main__":
    while True:
        teletype_url = input("url: ")
        download_teletype_page(teletype_url)