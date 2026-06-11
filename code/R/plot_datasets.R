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
##############################################################

library(readxl)
library(jsonlite)
library(ggplot2)

### 1. Read inputs
path_to_folder <- "//define/path/here/"  # replace with own dir
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

counts$covid_color <- ifelse(counts$isCovid == 1, "COVID-19 specific", "Not COVID-19 specific")

### 4. Add jitter
counts$x_jit <- jitter(as.numeric(counts$accessibility),factor=2.5)
counts$y_jit <- jitter(counts$n_needs,factor=2.5)

### 5. Colours 
pt_colors <- c("COVID-19 specific"     = "#1565C0",
               "Not COVID-19 specific" = "#90A4AE")

### 6. Axis geometry 
y_max    <- max(counts$n_needs)
y_breaks <- 1:y_max
n_x      <- nlevels(counts$accessibility)
y_lo     <- min(counts$y_jit) - 0.4
y_hi     <- y_max + 0.5

### 7. Plot 
p <- ggplot(counts) +

  # Alternating column shading
  geom_rect(data = data.frame(x = seq(1, n_x, 2)),
            aes(xmin = x - 0.5, xmax = x + 0.5, ymin = -Inf, ymax = Inf),
            fill = "#F5F7FA", inherit.aes = FALSE) +

  # Grid lines
  geom_hline(yintercept = y_breaks, color = "#DEDEDE", linewidth = 0.3) +
  geom_vline(xintercept = seq(0.5, n_x + 0.5, 1), color = "#DEDEDE", linewidth = 0.3) +

  # Dataset id labels
  geom_text(aes(x = x_jit, y = y_jit, label = ds_id, color = covid_color),
            size = 2.7, fontface = "bold", family = "mono") +

  # Scales 
  scale_color_manual(name   = NULL,
                     values = pt_colors) +
  scale_x_continuous(breaks = seq_along(levels(counts$accessibility)),
                     labels = levels(counts$accessibility),
                     limits = c(0.5, n_x + 0.5), expand = c(0, 0)) +
  scale_y_continuous(breaks = y_breaks,
                     limits = c(y_lo, y_hi), expand = c(0, 0)) +

  # Labels
  labs(
    x = "Accessibility",
    y = "Number of data needs addressed"
  ) +

  # Theme 
  theme_minimal(base_size = 9) +
  theme(
    plot.title       = element_text(size = 13, face = "bold", margin = margin(b = 3)),
    plot.subtitle    = element_text(size = 7,  color = "#546E7A",
                                    margin = margin(b = 8), lineheight = 1.45),
    axis.title       = element_text(size = 9,  face = "bold"),
    axis.title.x     = element_text(margin = margin(t = 10)),
    axis.title.y     = element_text(margin = margin(r = 8)),
    axis.text.x      = element_text(size = 10, face = "bold", color = "#37474F"),
    axis.text.y      = element_text(size = 9,  color = "#37474F"),
    panel.grid       = element_blank(),
    legend.position  = "bottom",
    legend.title     = element_text(size = 8,  face = "bold"),
    legend.text      = element_text(size = 8),
    legend.key.size  = unit(0.45, "cm"),
    plot.background  = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA),
    plot.margin      = margin(t = 10, r = 15, b = 10, l = 10, unit = "pt")
  ) +
  guides(color = guide_legend(override.aes = list(size = 4.5)))

### 8. Save 
ggsave(path_to_output, plot = p, width = 10, height = 8, dpi = 180, bg = "white")
