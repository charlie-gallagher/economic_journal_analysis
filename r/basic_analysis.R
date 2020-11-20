library(tidyverse)
library(janitor)

article_meta <- read_csv('../../doaj/python/article_metadata.csv',
                         col_types = cols(
                           journal = col_character(),
                           title = col_character(),
                           nchar = col_double(),
                           is_empty = col_character(),
                           is_abstract = col_character(),
                           .default = col_integer()
                         )) %>% 
  mutate(
    is_empty = is_empty == "True",
    is_abstract = is_abstract == "True"
  )


# This is a dataset containing 1,960 articles, many of which had full texts. 


# Some summary statistics ----------
# n per year
article_meta %>% 
  tabyl(year, journal)

article_meta %>% 
  tabyl(year) %>% 
  ggplot() + geom_line(aes(x = year, y = n))

article_meta %>% 
  group_by(year, journal) %>% 
  summarize(n = n()) %>% 
  ggplot() + 
  geom_line(aes(x = year, y = n, group = journal, color = journal))

article_meta %>% 
  group_by(year, journal, is_abstract) %>% 
  summarize(n = n()) %>%
  ggplot() + 
  geom_line(aes(x = year, y = n, 
                group = interaction(journal, is_abstract),
                color = interaction(journal, is_abstract)))

article_meta %>% 
  ggplot() + geom_point(aes(x = year, y = nchar, color = is_abstract))


# Share of articles that are abstracts only
# n_abstract / n_total
article_meta %>% 
  group_by(year, journal) %>% 
  summarize(
    n = n(),
    n_abstract = sum(is_abstract)
  ) %>% 
  mutate(pct_abstract = n_abstract / n) %>% 
  ggplot() + geom_line(aes(x = year, y = pct_abstract, group = journal,
                           color = journal)) +  
  labs(title = "Share of Articles that are Abstracts", subtitle = "By Journal") + 
  scale_color_discrete() +
  theme_bw()

article_meta %>% 
  group_by(year) %>% 
  summarize(
    n = n(),
    n_abstract = sum(is_abstract)
  ) %>% 
  mutate(pct_abstract = n_abstract / n) %>% 
  ggplot() + geom_line(aes(x = year, y = pct_abstract), color = '#4fb4f7') + 
  labs(title = "Share of Articles that are Abstracts") + 
  scale_y_continuous(limits = c(0,1)) + 
  theme_bw()


# Article length over time
article_meta %>% 
  filter(!is_abstract) %>% 
  ggplot() + 
  geom_boxplot(aes(y = year, x = nchar, group = year), size = 0.5) + 
  facet_wrap(vars(journal), nrow = 1) + 
  scale_y_reverse(breaks = seq(1990, 2020, 5),
                  minor_breaks = seq(1990, 2020, 1)) + 
  ggthemes::theme_few()





# Summaries ------------------------

# Results by journal ---------------
amj <- article_meta %>% 
  filter(!is_abstract) %>%
  pivot_longer(
    cols = starts_with("r_"),
    names_to = "criterion",
    values_to = "count_n"
  ) %>% 
  mutate(
    count_l = count_n > 0
  ) %>% 
  group_by(journal, year, criterion) %>% 
  summarize(
    articles = n(),
    kwd = sum(count_l)
  ) %>% 
  mutate(
    pct_kwd = kwd / articles
  )


# Results in total -----------------
am <- amj %>% 
  group_by(year, criterion) %>% 
  summarize(
    n = sum(articles),
    kwd_l = sum(kwd)
  )


