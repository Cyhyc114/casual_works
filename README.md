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

## 备注 / Notes

- 欢迎通过 Issues 提出建议，但不保证及时响应。

- Suggestions are welcome via Issues, but responses are not guaranteed.
