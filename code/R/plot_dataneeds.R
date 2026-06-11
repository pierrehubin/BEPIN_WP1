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
##############################################################

library(readxl)
library(ggplot2)

### 1. Read & clean
path_to_folder <- "//define/path/here/"  # replace with own dir
path_to_excel <- paste0(path_to_folder,"T13_preMapping.xlsx")
path_to_output <- paste0(path_to_folder,"R/plot_dataneeds.png")
df <- read_excel(path_to_excel,sheet = "DataDatasets")
df <- df[!is.na(df$Data_Code), ]
df$cl <- trimws(as.character(df$ClassificationDataNeeds))
df$n_id <- as.numeric(df$NumberOfDatasetsIdentified)
df$min_req <- trimws(as.character(df$MinDatasetsReq))
df$n_id[is.na(df$n_id)] <- 0
df$Data_Code_plot <- as.character(as.numeric(substr(df$Data_Code,2,4)))

### 2. Remove (not, 0) items — pure gaps with no information 
df <- df[!(df$min_req == "not" & df$n_id == 0), ]

### 3. X-axis ordered factor
num_vals <- sort(unique(suppressWarnings(
  as.integer(df$min_req[!df$min_req %in% c("not", "partially")]))))
num_vals <- num_vals[!is.na(num_vals)]
x_levels <- c("not", "partially", as.character(num_vals))
# Drop "not" if no items remain there
x_levels <- x_levels[x_levels %in% df$min_req]
df$x_cat <- factor(df$min_req, levels = x_levels)

### 4. jitter dots
df$x_jit <- jitter(as.numeric(df$x_cat),factor=2.5)
df$y_jit <- jitter(df$n_id,factor=2.5)

### 5. Colours 
cl_colors <- c("G" = "#2E7D32", "O" = "#E65100")
cl_labels <- c("G" = "Good match (G)",
                "O" = "Partial match (O)")

### 6. Axis geometry 
n_x      <- length(x_levels)
y_max    <- max(df$n_id)
y_breaks <- 0:y_max
y_lo     <- min(df$y_jit) - 0.4
y_hi     <- y_max + 0.5

### 7. Plot 
p <- ggplot(df) +

  # Alternating column shading
  geom_rect(data = data.frame(x = seq(1, n_x, 2)),
            aes(xmin = x - 0.5, xmax = x + 0.5, ymin = -Inf, ymax = Inf),
            fill = "#F5F7FA", inherit.aes = FALSE) +

  # Grid lines
  geom_hline(yintercept = y_breaks, color = "#DEDEDE", linewidth = 0.3) +
  geom_vline(xintercept = seq(0.5, n_x + 0.5, 1), color = "#DEDEDE", linewidth = 0.3) +

  # Data need labels
  geom_text(aes(x = x_jit, y = y_jit, label = Data_Code_plot, color = cl),
            family = "mono") +

  # Scales
  scale_color_manual(name   = "Data need classification",
                     values = cl_colors, labels = cl_labels) +
  scale_x_continuous(breaks = seq_along(x_levels), labels = x_levels,
                     limits = c(0.5, n_x + 0.5), expand = c(0, 0)) +
  scale_y_continuous(breaks = y_breaks,
                     limits = c(y_lo, y_hi), expand = c(0, 0)) +

  # Labels
  labs(
    x = "Minimum datasets required",
    y = "Number of datasets identified"
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
    axis.text.x      = element_text(size = 9,  face = "bold", color = "#37474F"),
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
ggsave(path_to_output, plot = p, width = 12, height = 8.5, dpi = 180, bg = "white")
