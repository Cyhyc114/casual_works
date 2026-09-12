# casual_works

这个仓库用于记录我个人突发奇想的一些小作品。每个作品的维护更新并不保证——它们大多是实验性质的，可能随时停止更新或重构。

This repository is a collection of my whimsical side projects. Maintenance and updates are not guaranteed for any of them—most are experimental and may be paused or refactored at any time.

> 代码的编写有 LLM（大语言模型）的辅助。  
> The code in this repository is written with the assistance of LLMs (Large Language Models).

---

## 目前仓库内的小作品 / Current Projects

### Protein2DNA

依据生物的密码子偏好表，将合法的蛋白序列翻译成 DNA 序列。  
该程序已用 PyInstaller 打包好了适合 Windows 的 EXE 文件，位于 `protein2DNA_win_APP.zip` 中。解压到任意目录后应该可以直接使用。

该程序还包含 **GC 值限制** 和 **避免特定序列（如酶切位点）** 的功能，方便下游实验设计。

---

Translate a valid protein sequence into a DNA sequence based on the organism's codon usage table.  

The program has been packaged with PyInstaller into a Windows‑compatible EXE file, available in `protein2DNA_win_APP.zip`. Simply unzip it to any folder and run it directly.

It also includes **GC content restriction** and **sequence avoidance** (e.g., restriction enzyme sites) features, making it convenient for downstream experimental design.

---

### Sepsis Biomarker Replication (Mendelian Randomization)

复现以下文章的技术路线，用于学习生信分析的一般流程：

> Shi Z, Wang F, Yang L, et al. Identification of sepsis biomarkers through glutamine metabolism-mediated immune regulation: a comprehensive analysis employing mendelian randomization, multi-omics integration, and machine learning. *Front Immunol.* 2025;16:1640425. doi:10.3389/fimmu.2025.1640425

**目标**：跑通 MR + 多组学 + 机器学习的核心流程，不追求数值完全一致。

**内容**：
- 孟德尔随机化（MR）：两样本 MR + 中介 MR
- 单细胞 RNA-seq：QC、聚类、注释、代谢评分
- Bulk RNA-seq：差异分析、LASSO、机器学习、SHAP

**当前进度**：
- [x] Figure 3D–G：5 个免疫表型 vs 脓毒症的两样本 MR
- [ ] 其余图表

**复现差异**：
- SNP 数量略多于原文（21–28 vs ~20），可能由于 LD clumping 参考面板不同
- `CD45 on CD8br` 方向与原文相反，其余 4 个表型方向一致
- 核心结论可支持

**环境**：
- OS：Ubuntu 24.04.4 LTS (WSL2)
- R：4.6.1
- 关键 R 包：TwoSampleMR 0.7.9、ieugwasr 1.1.0.9000、MRPRESSO 1.0、dplyr 1.2.1、ggplot2 4.0.3、patchwork 1.3.2
- Python：待补

---

Partial replication of the pipeline from the paper above, for learning the general workflow of bioinformatics analysis.

**Goal**: run through the core pipeline (MR + multi-omics + ML) without aiming for exact numerical agreement.

**Scope**:
- Mendelian Randomization (MR): two-sample MR + mediation MR
- scRNA-seq: QC, clustering, annotation, metabolic scoring
- Bulk RNA-seq: DEG, LASSO, machine learning, SHAP

**Progress**:
- [x] Figure 3D–G: two-sample MR for 5 immune phenotypes vs sepsis
- [ ] Remaining figures

**Reproduction differences**:
- SNP count slightly higher than the paper (21–28 vs ~20), likely due to different LD clumping reference panels
- `CD45 on CD8br` shows opposite direction; the other 4 phenotypes are consistent
- Core conclusion is supported

**Environment**:
- OS: Ubuntu 24.04.4 LTS (WSL2)
- R: 4.6.1
- Key R packages: TwoSampleMR 0.7.9, ieugwasr 1.1.0.9000, MRPRESSO 1.0, dplyr 1.2.1, ggplot2 4.0.3, patchwork 1.3.2
- Python: to be filled

---

## 备注 / Notes

- 欢迎通过 Issues 提出建议，但不保证及时响应。

- Suggestions are welcome via Issues, but responses are not guaranteed.
