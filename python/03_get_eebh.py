from bs4 import BeautifulSoup
import requests
from urllib.request import urlretrieve
import json
import re
import time
import pdfminer.high_level as pdf

with open('../article_data_subset/article_subset_master.json') as j:
    master_article = json.load(j)


# All I need are the articles from Essays in Economic and Business History
def filter_journal(article_list, journals):
    article_subset = [d for d in article_list
                      if "journal" in d['bibjson'] and
                      "title" in d['bibjson']['journal'] and
                      d['bibjson']['journal']['title'] in journals]
    return article_subset


eebh = filter_journal(master_article, 'Essays in Economic and Business History')

article_links = [article['bibjson']['link'][0]['url'] for article in eebh]


pdf_filenames = []
base = '../pdf/eebh_'
ext = '.pdf'
for i in range(len(article_links)):
    filename = f"{base}{i:03}{ext}"
    pdf_filenames.append(filename)

n_articles = 0
failed_articles = 0
for file, url in zip(pdf_filenames, article_links):
    n_articles += 1
    try:
        # Get link url
        html = requests.get(url).text
        html_soup = BeautifulSoup(html, 'html.parser')
        pdf_link = html_soup.find(
            name='meta',
            attrs={'name': 'citation_pdf_url'}  # Call direct to avoid name
            # conflict
        )
        pdf_link.get('content')

        # Download pdf
        print(f"Downloading to {file}...", end="")
        urlretrieve(pdf_link, file)  # urlretrieve from urllib.request
        time.sleep(1)
        print("Done.")
    except:
        print("Warning: article not found")
        failed_articles += 1

print(f"Successful articles: {n_articles - failed_articles:4} / {n_articles}")
print(f"Failed articles: {failed_articles} / {n_articles}")

print("\nConverting PDFs to text files ------------------")
txt_filenames = []
base = '../txt/eebh_'
ext = '.txt'
for i in range(len(article_links)):
    txt_filenames.append(f"{base}{i:03d}{ext}")


for file_from, file_to in zip(pdf_filenames, txt_filenames):
    print(f"Converting {file_from}...", end='')
    try:
        with open(file_to, 'w', encoding='utf-8') as w:
            text = pdf.extract_text(file_from)
            w.write(text)
        print("done.")
    except FileNotFoundError:
        print("Warning: file does not exist")


