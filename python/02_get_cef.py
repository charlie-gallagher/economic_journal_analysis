import json
import requests
from bs4 import BeautifulSoup

with open('../article_data_subset/article_subset_master.json') as j:
    master_article = json.load(j)


# All I need are the articles from Cogent Economics and Finance
def filter_journal(article_list, journals):
    article_subset = [d for d in article_list
                      if "journal" in d['bibjson'] and
                      "title" in d['bibjson']['journal'] and
                      d['bibjson']['journal']['title'] in journals]
    return article_subset


cef = filter_journal(article_list=master_article,
                     journals="Cogent Economics & Finance")

print(json.dumps(cef[0], indent=4))

# Get links
article_links = []
for article in cef:
    article_links.append(article['bibjson']['link'][0]['url'])

filenames = []
base = '../txt/cef_'
ext = '.txt'
for i in range(len(article_links)):
    filename = f"{base}{i:03}{ext}"
    filenames.append(filename)

counter = 0
for file, link in zip(filenames, article_links):
    print(f"Converting {file}...", end=" ")
    article_html = requests.get(link)
    article_bs = BeautifulSoup(article_html.text, 'html.parser')
    if article_bs.title is None:  # Failing early as best I can
        print("Warning: file not written")
    else:
        article_fulltext = article_bs.find('div', class_='hlFld-Fulltext')
        if article_fulltext is None:
            print("Warning: file not written")
        else:
            article_fulltext = article_fulltext.text
            with open(file, 'w', encoding='utf-8') as _f:
                _f.write(article_fulltext)
            print("Done.")
        counter += 1

print(f"Successful conversions: {counter} / 601")
