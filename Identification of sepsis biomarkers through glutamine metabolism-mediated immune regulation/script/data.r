# ---- 项目根目录（硬编码）----
base_dir <- "/mnt/e/code/casual_works/Identification of sepsis biomarkers through glutamine metabolism-mediated immune regulation"

data_dir         <- file.path(base_dir, "data")
gwas_catalog_dir <- file.path(data_dir, "gwas_catalog")
opengwas_dir     <- file.path(data_dir, "opengwas")
geo_dir          <- file.path(data_dir, "geo")
msigdb_dir       <- file.path(data_dir, "msigdb")

results_dir <- file.path(base_dir, "results")
figures_dir <- file.path(results_dir, "figures")
tables_dir  <- file.path(results_dir, "tables")

# 创建目录
for (d in c(data_dir, gwas_catalog_dir, opengwas_dir, geo_dir, msigdb_dir,
            results_dir, figures_dir, tables_dir)) {
  dir.create(d, showWarnings = FALSE, recursive = TRUE)
}