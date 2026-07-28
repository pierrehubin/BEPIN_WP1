##############################################################
# Project name — BE-PIN task 1.3 (WP1)
# 
# Script Name: plot_dataneeds.R
# 
# Short Description: Generate data needs plot
# 
# Author: Pierre Hubin
# 
# Versioning:
# v1 Creation Jun 10 2026 Pierre Hubin
# v2 Categorize y-axis Jul 22 2026 Pierre Hubin
# v3 New version of graph after aggregating over data needs
##############################################################

library(readxl)
library(ggplot2)
library(tidyverse)

### 1. Read & clean
path_to_folder <- "../"  # replace with own dir
path_to_excel <- paste0(path_to_folder,"T13_preMapping.xlsx")
path_to_output <- paste0(path_to_folder,"R/plot_dataneeds.png")
df <- read_excel(path_to_excel,sheet = "DataDatasets")
df <- df[!is.na(df$Data_Code), ]
df$cl <- trimws(as.character(df$ClassificationDataNeeds))
df$n_id <- as.numeric(df$NumberOfDatasetsIdentified)
df$min_req <- trimws(as.character(df$MinDatasetsReq))
df$n_id[is.na(df$n_id)] <- 0
df$Data_Code_plot <- as.character(as.numeric(substr(df$Data_Code,2,4)))

### 2. Remove (not, 0) items, gaps with no information 
df <- df[!(df$min_req == "not" & df$n_id == 0), ]
x_max <- max(as.integer(df$MinDatasetsReq),na.rm=TRUE)

### 3. Aggregate by accessibility x number of datasets required

agg_dataneeds <- df %>% group_by(ClassificationDataNeeds,MinDatasetsReq) %>%
  summarise(n_dataneeds=n()) %>%
  mutate(MinDatasetsReq=factor(MinDatasetsReq,
    levels=c(seq(1,x_max),"partially"),
    labels=c(seq(1,x_max),"X")))

### 4. Plot 

cl_colors <- c("G" = "#41ea0e", "O" = "#fa9507")
cl_labels <- c("G" = "Total match \n and open",
                "O" = "Partial match \n and/or not open")

p <- ggplot(agg_dataneeds, aes(fill=ClassificationDataNeeds , y=n_dataneeds, x=MinDatasetsReq)) +

  geom_bar(position="stack", stat="identity") +

  # Labels
  labs(
    x = "Number of datasets required",
    y = "Number of data needs"
  ) +
  
  scale_fill_manual(values = cl_colors, name= "Accessibility", labels = cl_labels) +

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

### 5. Save 
ggsave(path_to_output, plot = p, width = 12, height = 8.5, dpi = 180, bg = "white")
