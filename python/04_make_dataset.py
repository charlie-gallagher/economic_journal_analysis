import json
import re
import csv
from pathlib import Path

# Use only JARE, CEF, and EEBH
journals = ["Journal of Agricultural and Resource Economics",
            "Cogent Economics & Finance",
            "Essays in Economic and Business History"]
with open('../article_data_subset/article_subset_master.json') as w:
    temp_master = json.load(w)
    master = [entry for entry in temp_master if entry['bibjson']['journal'][
        'title'] in journals]
    # Order: CEF, EEBH, JARE
    master.sort(key=lambda t: t['bibjson']['journal']['title'])
    del temp_master



class Article:
    """ Store a full-text article """

    # TODO: Turn fulltext getter into function

    def __init__(self, path, article_entry):
        if Path(path).exists():
            with open(path, encoding='utf-8') as ft:
                self.fulltext = ft.read()
            self.nchar = len(self.fulltext)
            self.is_abstract = False
            if self.nchar < 1000:
                try:
                    self.fulltext = article_entry['bibjson']['abstract']
                    self.nchar = len(self.fulltext)
                    self.is_abstract = True
                except KeyError:
                    self.fulltext = ""
                    self.nchar = 0
                    self.is_abstract = False
                self.is_corrupt = True
            else:
                self.is_corrupt = False
                self.is_abstract = False
        else:
            try:
                self.fulltext = article_entry['bibjson']['abstract']
                self.nchar = len(self.fulltext)
                self.is_abstract = True
            except KeyError:
                self.fulltext = ""
                self.nchar = 0
                self.is_abstract = False
            self.is_corrupt = True

        self.title = article_entry['bibjson']['title']
        self.year = int(article_entry['bibjson']['year'])
        self.journal = article_entry['bibjson']['journal']['title']

    def __str__(self):
        return f"<Article object, year: {self.year}>"

    def get_fulltext(self):
        return self.fulltext

    def search_n(self, regex, case=True):
        """
        Return number of matches of a regular expression.

        :param regex: Regular expression
        :param case: Case sensitive?
        :return an integer:
        """
        if case:
            n_matches = len(re.findall(regex, self.fulltext))
        else:
            n_matches = len(re.findall(regex, self.fulltext,
                                       flags=re.IGNORECASE))
        return n_matches

    def search_l(self, regex):
        """
        Return a logical indicating whether the regular expression matches
        any text in the full-text.

        :param regex:
        :return a boolean True or False:
        """
        match_l = bool(re.search(regex, self.fulltext))
        return match_l


class ArticleDataset:
    """ Store any number of Article objects """

    def __init__(self, article_paths, article_data):
        self.articles = []
        for i, path in enumerate(article_paths):
            a_article = Article(path, article_data[i])
            self.articles.append(a_article)

        self.articles.sort(key=lambda x: x.year)

        temp_years = [article.year for article in self.articles]
        self.years = list(range(min(temp_years), max(temp_years) + 1))

    def __str__(self):
        return f"<ArticleDataset Object, n = {len(self.articles)}>"

    def print_titles(self, *, year=True, nchar=True):
        if year and nchar:
            for article in self.articles:
                print(f"{article.year} (nchar: {article.nchar:6d}) \t"
                      f" {article.title}")
        elif nchar and not year:
            for article in self.articles:
                print(f"{article.nchar:8d} \t {article.title}")
        elif not (nchar and year):
            for article in self.articles:
                print(f"{article.title}")

    def search_all_l(self, regex):
        output = [x.search_l(regex) for x in self.articles]
        return sum(output)

    def search_all_n(self, regex):
        output = [x.search_n(regex) for x in self.articles]
        return sum(output)

    def search_all_years_l(self, regex):
        output = {}
        for year in self.years:
            year_output = [x.search_l(regex) for x in self.articles if x.year
                           == year]
            output[year] = sum(year_output)
        return output

    def search_all_years_n(self, regex):
        output = {}
        for year in self.years:
            year_output = [x.search_n(regex) for x in self.articles if x.year
                           == year]
            output[year] = sum(year_output)
        return output

    def articles_per_year(self):
        output = {}
        for year in self.years:
            year_output = len([x for x in self.articles if x.year == year])
            output[year] = year_output
        return output


# Application ---------------
# Filenames for the text files
txt_filenames = []

# CEF
base = '../txt/cef_'
ext = '.txt'
for i in range(601):
    txt_filenames.append(f"{base}{i:03d}{ext}")

# EEBH
base = '../txt/eebh_'
ext = '.txt'
for i in range(468):
    txt_filenames.append(f"{base}{i:03d}{ext}")

# JARE
base = '../txt/jare_'
ext = '.txt'
for i in range(891):
    txt_filenames.append(f"{base}{i:03d}{ext}")

# The master dataset of Article objects
print('Making article database...')
art_dataset = ArticleDataset(article_paths=txt_filenames, article_data=master)


# --------------------
# Making the Dataset
# --------------------
# Regular expressions
r_rdd = r"regression discontinuity"
r_did = r"((D|d)ifference(\s|-)?in-?(D|d)ifference(s)?|(D(i|I)D)"
r_bigdata = r"big data"
r_internet = r"internet"
r_ols = r"(OLS)|((O|o)rdinary (L|l)east (S|s)quares)"
r_arch = r"ARCH"
r_ne = r"natural experiment"
r_event = r"event study"
r_fincris = r"Great Recession"
r_id = r"identification"
r_admin = r"administrative data"
r_ml = r"machine learning"
r_data = r"data"
r_python = r"(Python)|(\.py)"


def make_col(regex, case=False, articles=art_dataset):
    """
    Make a list of results for each article.

    By default, case-insensitive.

    :param regex: Regular expression
    :param case: If true, case-sensitive.
    :param articles: ArticleDataset object containing searchable articles
    """
    regex_result = [x.search_n(regex, case=case) for x in articles.articles]
    return regex_result


print("Making dictionary...")

article_metadata_csv = dict(
    journal=[article.journal for article in art_dataset.articles],
    title=[article.title for article in art_dataset.articles],
    year=[article.year for article in art_dataset.articles],
    nchar=[article.nchar for article in art_dataset.articles],
    is_empty=[article.is_corrupt for article in art_dataset.articles],
    is_abstract=[article.is_abstract for article in art_dataset.articles],
    r_did=make_col(r_did, case=True),
    r_rdd=make_col(r_rdd),
    r_internet=make_col(r_internet),
    r_ols=make_col(r_ols, case=True),
    r_arch=make_col(r_arch, case=True),
    r_natexp=make_col(r_ne),
    r_financialcrisis=make_col(r_fincris, case=True),
    r_identification=make_col(r_id),
    r_data=make_col(r_data),
    r_bigdata=make_col(r_bigdata),
    r_admin=make_col(r_admin),
    r_ml=make_col(r_ml),
    r_python=make_col(r_python, case=True)
)

print("Writing file...")

with open('article_metadata.csv', 'w', newline='', encoding='utf-8') as c:
    doaj_writer = csv.writer(c, delimiter=',')
    doaj_writer.writerow(article_metadata_csv.keys())
    for i in range(len(art_dataset.articles)):
        line = []
        for key in article_metadata_csv.keys():
            line.append(article_metadata_csv[key][i])
        doaj_writer.writerow(line)

print("Done.")
