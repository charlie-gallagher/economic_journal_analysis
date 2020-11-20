library(ggplot2)
doaj_theme <- theme_minimal() +
  theme(
    axis.line.x = element_line(),
    axis.line.y = element_line(),
    axis.title.x = element_blank()
  )

doaj_plot <- function(base) {
  base + 
    scale_x_continuous(limits = c(1990, 2020), expand = c(0,0)) +
    scale_y_continuous(limits = c(0, 130), expand = c(0,0)) +
    doaj_theme
}
