# ============================================================
# plot_figure3.r — 简历/展示优化版
# ============================================================

library(TwoSampleMR)
library(ggplot2)
library(patchwork)
library(dplyr)

options(TwoSampleMR.verbose = FALSE)

base_dir <- "/mnt/e/code/casual_works/Identification of sepsis biomarkers through glutamine metabolism-mediated immune regulation"
results_dir <- file.path(base_dir, "results", "tables")
figures_dir <- file.path(base_dir, "results", "figures")
dir.create(figures_dir, showWarnings = FALSE, recursive = TRUE)

all_dat <- readRDS(file.path(results_dir, "MR_harmonised_data.rds"))

pheno_names <- c(
  "GCST90001917" = "CD45 on CD8br",
  "GCST90001592" = "CD8br AC",
  "GCST90001411" = "IgD+ CD24+ %B cell",
  "GCST90002077" = "SSC-A on HLA-DR+ NK",
  "GCST90002072" = "SSC-A on plasmacytoid DC"
)

# ============================================================
# Figure 3D / 3E：森林图
# ============================================================
make_forest <- function(dat, title) {
  singlesnp <- mr_singlesnp(dat)
  p <- mr_forest_plot(singlesnp)[[1]] +
    labs(title = title) +
    theme_bw(base_size = 7) +
    theme(
      plot.title = element_text(hjust = 0.5, size = 7, face = "bold"),
      axis.title.x = element_blank(),
      axis.text.x = element_text(size = 6),
      axis.text.y = element_text(size = 5),
      legend.position = "none",
      plot.margin = margin(2, 2, 2, 2)
    )
  return(p)
}

for (outcome in c("ieu-b-4981", "ieu-b-5086")) {
  plots <- list()
  for (gcst in names(pheno_names)) {
    key <- paste(gcst, outcome, sep = "_")
    if (!is.null(all_dat[[key]])) {
      plots[[pheno_names[gcst]]] <- make_forest(all_dat[[key]], pheno_names[gcst])
    }
  }
  
  fig_num <- ifelse(outcome == "ieu-b-4981", "3D", "3E")
  p <- wrap_plots(plots, ncol = 5) +
    plot_annotation(
      title = paste0("Figure ", fig_num, ": ", outcome),
      theme = theme(plot.title = element_text(hjust = 0.5, face = "bold", size = 12))
    )
  
  ggsave(file.path(figures_dir, paste0("Figure", fig_num, "_forest_", outcome, ".png")),
         p, width = 14, height = 6, dpi = 300, limitsize = FALSE)
  cat("Figure", fig_num, "saved.\n")
}

# ============================================================
# Figure 3F / 3G：散点图
# ============================================================
make_scatter <- function(dat, title) {
  res <- mr(dat, method_list = c(
    "mr_ivw", "mr_weighted_median", "mr_egger_regression",
    "mr_weighted_mode", "mr_simple_mode"
  ))
  p <- suppressMessages(mr_scatter_plot(res, dat)[[1]]) +
    labs(title = title) +
    theme_bw(base_size = 7) +
    theme(
      plot.title = element_text(hjust = 0.5, size = 7, face = "bold"),
      legend.position = "right",
      legend.key.size = unit(0.25, "cm"),
      legend.text = element_text(size = 5),
      legend.title = element_blank(),
      axis.title = element_text(size = 6),
      axis.text = element_text(size = 5),
      plot.margin = margin(2, 2, 2, 2)
    )
  return(p)
}

for (outcome in c("ieu-b-4981", "ieu-b-5086")) {
  plots <- list()
  for (gcst in names(pheno_names)) {
    key <- paste(gcst, outcome, sep = "_")
    if (!is.null(all_dat[[key]])) {
      plots[[pheno_names[gcst]]] <- make_scatter(all_dat[[key]], pheno_names[gcst])
    }
  }
  
  fig_num <- ifelse(outcome == "ieu-b-4981", "3F", "3G")
  p <- wrap_plots(plots, ncol = 3) +
    plot_annotation(
      title = paste0("Figure ", fig_num, ": ", outcome),
      theme = theme(plot.title = element_text(hjust = 0.5, face = "bold", size = 12))
    )
  
  ggsave(file.path(figures_dir, paste0("Figure", fig_num, "_scatter_", outcome, ".png")),
         p, width = 13, height = 7, dpi = 300, limitsize = FALSE)
  cat("Figure", fig_num, "saved.\n")
}

cat("\nDone.\n")