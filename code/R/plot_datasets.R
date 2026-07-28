##############################################################
# Project name — BE-PIN task 1.3 (WP1)
# 
# Script Name: plot_datasets.R
# 
# Short Description: Generate datasets plot
# 
# Author: Pierre Hubin
# 
# Versioning:
# v1 Creation Jun 11 2026 Pierre Hubin
# v2 Categorize y-axis Jul 22 2026 Pierre Hubin
# v3 New version of graph after aggregating by acessibility
##############################################################

library(readxl)
library(jsonlite)
library(tidyverse)
library(ggplot2)

### 1. Read inputs
path_to_folder <- "../"  # replace with own dir
path_to_excel <- paste0(path_to_folder,"T13_preMapping.xlsx")
path_to_output <- paste0(path_to_folder,"R/plot_datasets.png")
df <- read_excel(path_to_excel,sheet = "DataDatasets")
df <- df[!is.na(df$Data_Code), ]

path_to_json <- paste0(path_to_folder,"data_sources.json")
ds_json <- fromJSON(path_to_json)$datasets
acc_lookup     <- setNames(ds_json$accessibility, as.character(ds_json$id))
covid_lookup   <- setNames(ds_json$isCovid,       as.character(ds_json$id))

### 2. Count how many data needs each dataset contributes to 
parse_ids <- function(x) {
  x <- as.character(x)
  if (is.na(x) || trimws(x) %in% c("", "GAP")) return(character(0))
  trimws(strsplit(x, ",")[[1]])
}
all_ids <- unlist(lapply(df$Datasets, parse_ids))
counts  <- as.data.frame(table(all_ids), stringsAsFactors = FALSE)
colnames(counts) <- c("ds_id", "n_needs")

### 3. Attach metadata 
counts$accessibility <- acc_lookup[counts$ds_id]
counts$isCovid       <- covid_lookup[counts$ds_id]

counts$accessibility <- factor(counts$accessibility,
                                levels = c("restricted", "requestable", "opendata"),
                                labels = c("Restricted", "Requestable", "Open data"))

### 4. Aggregate by accessibility x number of needs addressed
###    and by covid flag x number of needs addressed

agg_accessibility <- counts %>% group_by(n_needs,accessibility) %>%
  summarise(n_datasets=n())

agg_covid <- counts %>% group_by(n_needs,isCovid) %>%
  summarise(n_datasets=n())

### 5. Plot 
cl_colors <- c("Restricted" = "#e34916", "Requestable" = "#fa9507", "Open data" = "#41ea0e")
x_ticks <- unique(agg_accessibility$n_needs)
n_x <- length(x_levels)

p <- ggplot(agg_accessibility, aes(fill=accessibility, y=n_datasets, x=n_needs)) +

  geom_bar(position="stack", stat="identity") +

  # Labels
  labs(
    x = "Number of data needs addressed",
    y = "Number of datasets"
  ) +
  
  scale_fill_manual(values = cl_colors, name= "Accessibility") +
  scale_x_continuous(breaks = seq_along(x_ticks), labels = x_ticks,
                     limits = c(0.5, n_x + 0.5), expand = c(0, 0)) +

  # Theme 
  theme_minimal(base_size = 9) +
  theme(
    plot.title       = element_text(size = 13, face = "bold", margin = margin(b = 3)),
    plot.subtitle    = element_text(size = 7,  color = "#546E7A",
                                    margin = margin(b = 8), lineheight = 1.45),
    axis.title       = element_text(size = 10,  face = "bold"),
    axis.title.x     = element_text(margin = margin(t = 10)),
    axis.title.y     = element_text(margin = margin(r = 8)),
    axis.text.x      = element_text(size = 10, face = "bold", color = "#37474F"),
    axis.text.y      = element_text(size = 10,  color = "#37474F"),
    panel.grid       = element_blank(),
    legend.position  = "bottom",
    legend.title     = element_text(size = 10,  face = "bold"),
    legend.text      = element_text(size = 10),
    legend.key.size  = unit(0.45, "cm"),
    plot.background  = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    plot.margin      = margin(t = 10, r = 15, b = 10, l = 10, unit = "pt")
  ) +
  guides(color = guide_legend(override.aes = list(size = 4.5)))

### 6. Save 
ggsave(path_to_output, plot = p, width = 10, height = 8, dpi = 180, bg = "white")
