import json
import urllib.request as request
import requests
import time
from bs4 import BeautifulSoup
import pdfminer.high_level as pdf

with open('../article_data_subset/article_subset_master.json') as j:
    master_article = json.load(j)


# Only the Journal of Agricultural and Applied Economics
def filter_journal(article_list, journals):
    article_subset = [d for d in article_list
                      if "journal" in d['bibjson'] and
                      "title" in d['bibjson']['journal'] and
                      d['bibjson']['journal']['title'] in journals]
    return article_subset


jaae = filter_journal(article_list=master_article,
                      journals="Journal of Agricultural and Resource Economics")

article_url_list = []
for article in jaae:
    article_url_list.append(article['bibjson']['link'][0]['url'])

print("Getting PDF Urls ------------------")
pdf_links = []
for url in article_url_list:
    print(f'Getting pdf url for {url}...', end="")
    html_plaintext = requests.get(url).text
    html_soup = BeautifulSoup(url_text, 'html.parser')
    tag = html_soup.find(name="meta", attrs={'name': 'citation_pdf_url'})

    pdf_links.append(tag['content'])
    print("Done.")

print("Done getting PDF URLs -----------------")
print("Downloading PDFs ----------------------")

# Downloading the PDFs
pdf_filenames = []
base = "../pdf/jare_"
ext = ".pdf"

for i in range(len(pdf_links)):
    pdf_filenames.append(f"{base}{i:03d}{ext}")

for url, file in zip(pdf_links, pdf_filenames):
    print(f'Downloading file {file}...', end='')
    request.urlretrieve(url=url, filename=file)
    print('File downloaded...Sleeping one second')
    time.sleep(1)

print("Done getting PDFs --------------------")
print("Converting PDFs to text -----------------")

txt_filenames = []
base = '../txt/jare_'
ext = '.txt'
for i in range(891):
    txt_filenames.append(f"{base}{i:03d}{ext}")


for file_from, file_to in zip(pdf_filenames, txt_filenames):
    print(f"Converting {file_from}...", end='')
    with open(file_to, 'w', encoding='utf-8') as w:
        text = pdf.extract_text(file_from)
        w.write(text)
    print("done.")
print("Done converting PDF files to text --------------------")

