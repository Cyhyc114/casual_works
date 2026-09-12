# ============================================================
# 复现 Figure 3D–G：5 个免疫表型 vs 脓毒症的两样本 MR
# ============================================================

library(TwoSampleMR)
library(dplyr)

# ---- 路径 ----
base_dir <- "/mnt/e/code/casual_works/Identification of sepsis biomarkers through glutamine metabolism-mediated immune regulation"
gwas_catalog_dir <- file.path(base_dir, "data", "gwas_catalog")
results_dir <- file.path(base_dir, "results", "tables")
dir.create(results_dir, showWarnings = FALSE, recursive = TRUE)

# ---- 5 个目标表型 ----
target_gcst <- c("GCST90001917", "GCST90001592", "GCST90001411",
                 "GCST90002077", "GCST90002072")

target_names <- c(
  GCST90001917 = "CD45 on CD8br",
  GCST90001592 = "CD8br AC",
  GCST90001411 = "IgD+ CD24+ %B cell",
  GCST90002077 = "SSC-A on HLA-DR+ NK",
  GCST90002072 = "SSC-A on plasmacytoid DC"
)

outcome_ids <- c("ieu-b-5086", "ieu-b-4981")

# ---- 存储 ----
all_mr_results    <- list()
all_het_results   <- list()
all_pleio_results <- list()
all_dat           <- list()

for (gcst in target_gcst) {
  cat("\n========== Processing", gcst, "-", target_names[gcst], "==========\n")

  # 1. 读入 exposure
  exp_file <- file.path(gwas_catalog_dir, paste0(gcst, ".h.tsv.gz"))

  exposure_dat <- tryCatch({
    read_exposure_data(
      filename = exp_file,
      sep = "\t",
      snp_col = "hm_rsid",
      beta_col = "beta",
      se_col = "standard_error",
      effect_allele_col = "effect_allele",
      other_allele_col = "other_allele",
      eaf_col = "effect_allele_frequency",
      pval_col = "p_value"
    )
  }, error = function(e) {
    cat("  Read failed:", conditionMessage(e), "\n"); NULL
  })

  if (is.null(exposure_dat) || nrow(exposure_dat) == 0) next

  # 2. P<1e-5
  exposure_dat <- exposure_dat[exposure_dat$pval.exposure < 1e-5, ]
  cat("  After P<1e-5:", nrow(exposure_dat), "SNPs\n")
  if (nrow(exposure_dat) == 0) next

  # 3. LD clumping
  exposure_dat <- tryCatch({
    clump_data(exposure_dat, clump_r2 = 0.001, clump_kb = 10000, pop = "EUR")
  }, error = function(e) {
    cat("  Clump failed:", conditionMessage(e), "\n"); NULL
  })
  if (is.null(exposure_dat) || nrow(exposure_dat) == 0) next
  cat("  After clumping:", nrow(exposure_dat), "SNPs\n")

  # 4. F > 10
  exposure_dat$F <- (exposure_dat$beta.exposure / exposure_dat$se.exposure)^2
  exposure_dat <- exposure_dat[exposure_dat$F > 10, ]
  cat("  After F>10:", nrow(exposure_dat), "SNPs\n")
  if (nrow(exposure_dat) == 0) next

  # 5. 每个结局
  for (outcome_id in outcome_ids) {
    cat("  Outcome:", outcome_id, "\n")

    outcome_dat <- tryCatch({
      extract_outcome_data(snps = exposure_dat$SNP, outcomes = outcome_id)
    }, error = function(e) {
      cat("    Extract outcome failed:", conditionMessage(e), "\n"); NULL
    })
    if (is.null(outcome_dat) || nrow(outcome_dat) == 0) next

    # 6. Harmonise
    dat <- harmonise_data(exposure_dat, outcome_dat, action = 2)
    dat <- dat[dat$mr_keep == TRUE, ]
    if (nrow(dat) == 0) next

    all_dat[[paste(gcst, outcome_id, sep = "_")]] <- dat

    # 7. 五种方法
    res <- mr(dat, method_list = c(
      "mr_ivw", "mr_weighted_median", "mr_egger_regression",
      "mr_weighted_mode", "mr_simple_mode"
    ))
    res$exposure_name <- target_names[gcst]
    res$outcome_id <- outcome_id
    all_mr_results[[paste(gcst, outcome_id, sep = "_")]] <- res

    # 8. 敏感性
    het <- mr_heterogeneity(dat)
    het$exposure_name <- target_names[gcst]
    het$outcome_id <- outcome_id
    all_het_results[[paste(gcst, outcome_id, sep = "_")]] <- het

    pleio <- mr_pleiotropy_test(dat)
    pleio$exposure_name <- target_names[gcst]
    pleio$outcome_id <- outcome_id
    all_pleio_results[[paste(gcst, outcome_id, sep = "_")]] <- pleio

    cat("    MR done:", nrow(res), "methods\n")
  }
}

# ---- 合并保存 ----
mr_df    <- do.call(rbind, all_mr_results)
het_df   <- do.call(rbind, all_het_results)
pleio_df <- do.call(rbind, all_pleio_results)

write.csv(mr_df,    file.path(results_dir, "MR_5_phenotypes_results.csv"), row.names = FALSE)
write.csv(het_df,   file.path(results_dir, "MR_heterogeneity.csv"), row.names = FALSE)
write.csv(pleio_df, file.path(results_dir, "MR_pleiotropy.csv"), row.names = FALSE)

saveRDS(all_dat, file.path(results_dir, "MR_harmonised_data.rds"))

cat("\n===== MR 结果 =====\n")
print(mr_df[, c("exposure_name", "outcome_id", "method", "nsnp", "b", "se", "pval")])
cat("\nSaved to:", results_dir, "\n")