# ============================================================
# App A — Adjacency Heatmap
# Info Needs (rows) x Data Needs (cols), filled cell = linked
# ============================================================
# install.packages(c("readxl","shiny","dplyr","stringr","tidyr","DT"))

library(readxl)
library(dplyr)
library(stringr)
library(tidyr)

# ── 1. Load & prepare ────────────────────────────────────────
file_path <- "T13_preMapping.xlsx"

info_needs <- read_excel(file_path, sheet = "InfoNeeds")
data_needs <- read_excel(file_path, sheet = "DataNeeds")
info_data  <- read_excel(file_path, sheet = "InfoData")

names(info_needs) <- c("code","label","layer","domain","topic")
names(data_needs) <- c("code","label","comment","data_driven","description")
names(info_data)  <- c("info_code","data_codes_raw")

# Expand edges
edges <- info_data %>%
  mutate(data_code = str_split(data_codes_raw, ",\\s*")) %>%
  unnest(data_code) %>%
  filter(!is.na(data_code), data_code != "", data_code != "NA") %>%
  select(info_code, data_code)

# Coverage counts
info_counts <- edges %>% count(info_code, name = "n_data") %>%
  rename(code = info_code)
data_counts <- edges %>% count(data_code, name = "n_info") %>%
  rename(code = data_code)

info_needs <- info_needs %>% left_join(info_counts, by = "code") %>%
  mutate(n_data = replace_na(n_data, 0))
data_needs <- data_needs %>% left_join(data_counts, by = "code") %>%
  mutate(n_info = replace_na(n_info, 0))



# Full presence matrix (all info x needs)
mat_full <- expand_grid(info_code = info_needs$code,
                        data_code = data_needs$code) %>%
  left_join(edges %>% mutate(linked = 1L), by = c("info_code","data_code")) %>%
  mutate(linked = replace_na(linked, 0L))

inf <- info_needs
dat <- data_needs
n_i <- nrow(inf)
n_d <- nrow(dat)

m <- matrix(0L, nrow=n_i, ncol=n_d,
            dimnames=list(inf$code, dat$code))
linked_pairs <- mat_full %>% filter(linked == 1L)
for (k in seq_len(nrow(linked_pairs))) {
  r <- linked_pairs$info_code[k]
  c <- linked_pairs$data_code[k]
  if (r %in% rownames(m) && c %in% colnames(m))
    m[r, c] <- 1L
}

#Plot
col_sums <- colSums(m)
row_sums <- rowSums(m)

png("heatmap_static.png", width=2800, height=1200, res=150, bg="#f5f7fa")
  par(mar=c(7, 9, 1.5, 1), bg="#f5f7fa")
  plot(0, type="n", xlim=c(0,n_d), ylim=c(0,n_i),
         xlab="", ylab="", xaxt="n", yaxt="n", bty="n")
    
    for (ci in seq_len(n_d)) {
      for (ri in seq_len(n_i)) {
        fill <- if (m[ri, ci] == 1L) "#2980b9"
        else if (col_sums[ci] == 0) "#fde8e8"
        else "#f0f3f7"
        rect(ci-1, n_i-ri, ci, n_i-ri+1,
             col=fill, border="#e8ecf0", lwd=.3)
      }
    }
    
    # Axes
  axis(1, at=(seq_len(n_d)-.5), labels=dat$code,
       las=2, cex.axis=.48, tick=FALSE, line=-.5, col.axis="#444")
  axis(2, at=(seq_len(n_i)-.5), labels=rev(inf$code),
       las=2, cex.axis=.7, tick=FALSE, line=-.3, col.axis="#444")
  axis(4, at=(seq_len(n_i)-.5),
       labels=rev(paste0("(", row_sums, ")")),
       las=2, cex.axis=.55, tick=FALSE, line=-.3, col.axis="#888")
  
  #Extras
  title(main="Information Needs \u00d7 Data Needs",
        cex.main=1.1, font.main=2, col.main="#2c3e50", line=2.2)
  mtext(paste0(sum(col_sums == 0), " unmapped data needs (red)  |  ",
               n_i, " info needs  \u00d7  ", n_d, " data needs  |  ",
               nrow(edges), " links total"),
        side=3, line=.6, cex=.65, col="#888")
  
  legend("topright",
         legend = c("Linked", "Not linked", "Data need not mapped"),
         fill   = c("#2980b9", "#f0f3f7", "#fde8e8"),
         border = c("#1a6fa8", "#e8ecf0", "#e8b4b8"),
         cex=.7, bg="white", box.col="#ccc", inset=c(.001,.001))
  
  dev.off()
  message("Saved: heatmap_static.png")
  