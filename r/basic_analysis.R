library(tidyverse)
library(janitor)  # For tabyl() function
source("./r/doaj_theme.R")
#   doaj_theme: A theme for consistent plotting
#   doaj_plot: A function that provides common defaults for plotting

article_meta <- read_csv('./python/article_metadata.csv',
                         col_types = cols(
                           journal = col_character(),
                           title = col_character(),
                           nchar = col_double(),
                           is_empty = col_character(),
                           is_abstract = col_character(),
                           .default = col_integer()
                         )) %>% 
  mutate(
    is_empty = (nchar == 0),
    is_abstract = is_abstract == "True"
  )


# This is a dataset containing 1,960 articles, many of which had full texts. 

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
    kwd = sum(count_l),
    pct_kwd = kwd / articles
  )


# Results in total -----------------
am <- amj %>% 
  group_by(year, criterion) %>% 
  summarize(
    n = sum(articles),
    kwd_l = sum(kwd)
  )




# Some summary statistics ----------
p_all_articles <- article_meta %>% 
  tabyl(year) %>% 
  ggplot() + 
  geom_line(aes(x = year, y = n), size = 1) + 
  geom_point(aes(x = year, y = n)) + 
  labs(title = "Number of articles in total")

p_journal_articles <- article_meta %>% 
  group_by(year, journal) %>% 
  summarize(n = n()) %>% 
  ggplot() + 
  geom_line(aes(x = year, y = n, group = journal, color = journal),
            size = 1) +
  geom_point(aes(x = year, y = n, group = journal, color = journal)) +
  labs(title = "Number of articles", subtitle = "By Journal")

p_is_abstract <- article_meta %>% 
  group_by(year, journal, is_abstract) %>% 
  summarize(n = n()) %>%
  ggplot() + 
  geom_line(aes(x = year, y = n, 
                group = journal, color = journal), size = 1) + 
  geom_point(aes(x = year, y = n, 
                color = journal)) + 
  facet_wrap(vars(is_abstract), nrow = 2) +
  labs(title = "Number of articles",
       subtitle = "By Journal and Abstract Status")


p_is_empty <- article_meta %>% 
  group_by(year, journal, is_empty) %>% 
  summarize(n = n()) %>%
  filter(is_empty == TRUE) %>% 
  ggplot() + 
  geom_line(aes(x = year, y = n, 
                group = journal, color = journal), size = 1) + 
  geom_point(aes(x = year, y = n, 
                color = journal))+
  labs(title = "Number of articles",
       subtitle = "By Journal and Missing Status")




doaj_plot(p_all_articles) # NOTE: doaj_plot() is sourced from doaj_theme.R
doaj_plot(p_journal_articles)
doaj_plot(p_is_abstract)
doaj_plot(p_is_empty)


# Share of articles that are abstracts only
# n_abstract / n_total
p_pct_abstract <- article_meta %>% 
  group_by(year, journal) %>% 
  summarize(
    n = n(),
    n_abstract = sum(is_abstract)
  ) %>% 
  mutate(pct_abstract = n_abstract / n) %>% 
  ggplot() + 
  geom_line(aes(x = year, y = pct_abstract, group = journal,
                color = journal)) + 
  geom_point(aes(x = year, y = pct_abstract, color = journal)) +
  labs(title = "Share of Articles that are Abstracts", subtitle = "By Journal") + 
  scale_color_discrete()

p_pct_empty <- article_meta %>% 
  group_by(year, journal) %>% 
  summarize(
    n = n(),
    n_empty = sum(is_empty)
  ) %>% 
  mutate(pct_empty = n_empty / n) %>% 
  ggplot() + 
  geom_line(aes(x = year, y = pct_empty, group = journal,
                color = journal)) + 
  geom_point(aes(x = year, y = pct_empty, color = journal)) +
  labs(title = "Share of Articles that are Missing", subtitle = "By Journal") + 
  scale_color_discrete()


doaj_plot(p_pct_abstract) + scale_y_continuous(limits = c(0,1))
doaj_plot(p_pct_empty) + scale_y_continuous(limits = c(0,1))


# Article length over time
article_meta %>% 
  filter(!is_abstract) %>% 
  ggplot() + 
  geom_boxplot(aes(y = year, x = nchar, group = year), size = 0.5) + 
  facet_wrap(vars(journal), nrow = 1) + 
  scale_y_reverse(breaks = seq(1990, 2020, 5),
                  minor_breaks = seq(1990, 2020, 1)) + 
  ggthemes::theme_few()

