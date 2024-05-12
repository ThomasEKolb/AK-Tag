import requests
from bs4 import BeautifulSoup
import os
import re

def fetch_detail_links_from_rss(rss_url):
    response = requests.get(rss_url)
    soup = BeautifulSoup(response.content, features="xml")
    detail_page_links = []
    items = soup.find_all('item')
    for item in items:
        description_soup = BeautifulSoup(item.description.text, 'html.parser')
        link = description_soup.a['href']
        title = description_soup.a.get_text(strip=True)  # Optional: Fetch the title for naming.
        detail_page_links.append((link, title))
    return detail_page_links

def sanitize_filename(filename):
    """Remove invalid characters and limit length for compatibility."""
    filename = re.sub('[^a-zA-Z0-9 \n\.]', '', filename)  # Keep alphanumeric, spaces, and dots.
    filename = filename[:100]  # Limit filename length if necessary.
    return filename

def download_pdfs(detail_page_links, base_url, save_dir):
    for link, title in detail_page_links:
        detail_page_url = base_url + link
        detail_page_response = requests.get(detail_page_url)
        detail_soup = BeautifulSoup(detail_page_response.content, 'html.parser')
        pdf_links = detail_soup.find_all('a', href=lambda href: href and "/dokument/" in href)
        for pdf_link in pdf_links:
            pdf_href = pdf_link['href']
            if not pdf_href.lower().endswith('.pdf'):
                continue
            pdf_url = base_url + pdf_href
            file_name = sanitize_filename(title) + '.pdf'  # Use title as file name
            pdf_response = requests.get(pdf_url)
            with open(os.path.join(save_dir, file_name), 'wb') as f:
                f.write(pdf_response.content)
            print(f"Downloaded {file_name}")

def main():
    rss_url = "https://www.parlament.gv.at/Filter/api/filter/rss/142?FBEZ=FP_142_vhg&selectedStage=101&BEZUG_GP_CODE=XXVII&BEZUG_ITYP=ME&BEZUG_INR=95&SORTRNR=5&ASCDESC=DESC"
    base_url = "https://www.parlament.gv.at"
    save_dir = "downloaded_pdfs"
    os.makedirs(save_dir, exist_ok=True)
    
    detail_page_links = fetch_detail_links_from_rss(rss_url)
    download_pdfs(detail_page_links, base_url, save_dir)

if __name__ == "__main__":
    main()
