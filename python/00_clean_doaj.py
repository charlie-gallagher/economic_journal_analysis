import json
import re

# =============================
# Journals
# =============================

# Import the json file
with open("../journal_data/journal_batch_1.json") as j:
    js = json.load(j)

# RegEx for economics journals in US and UK
doaj_re = r".*((E|e)conom(ic|ics|y|etric|ies))|((F|f)inanc)|((L|l)abo(u?)r\b)"
countries = ["US", "GB"]

# Only US and GB journals
js_subset = [d for d in js
             if "title" in d['bibjson'] and
             d['bibjson']['country'] in countries]

# Only Econ journals
js_subset = [d for d in js_subset
             if "title" in d['bibjson'] and
             re.search(doaj_re, d['bibjson']['title'])]

# Make a list of names
journal_names = [d["bibjson"]["title"] for d in js_subset]


# =============================
# Articles
# =============================
def article_subset(file_from, file_to, journals):
    with open(file_from) as j:
        article = json.load(j)
        article_subset = [d for d in article
                          if "journal" in d['bibjson'] and
                          "title" in d['bibjson']['journal'] and
                          d['bibjson']['journal']['title'] in journals]

    with open(file_to, "w") as art_sub:
        art_sub.write(json.dumps(article_subset))


# Looping through the articles ----------------------

# Getting file names
root = '../article_data/article_batch_'
ext = '.json'

files_from = []
for i in range(1, 54):
    files_from.append(f"{root}{str(i)}{ext}")

# Making new file names
root = '../article_data_subset/article_subset_'
ext = '.json'

files_to = []
for i in range(1, 54):
    files_to.append(f"{root}{str(i):0>2}{ext}")

for a, b in zip(files_from, files_to):
    print(f"Filtering {a:<15}")
    article_subset(file_from=a,
                   file_to=b,
                   journals=journal_names)
    print("Done")

# =======================
# MASTER DATASET
# =======================

master_json = []

# names
root = '../article_data_subset/article_subset_'
ext = '.json'

names = []
for i in range(1, 54):
    names.append(f"{root}{str(i):0>2}{ext}")

# Combining all files into a single dictionary
for name in names:
    print(f"Appending {name}", end="")
    with open(name) as js:
        piece_json = json.load(js)
        for article in piece_json:
            master_json.append(article)
    print("   Done.")

with open("../article_data_subset/article_subset_master.json", "w") as m:
    m.write(json.dumps(master_json))
