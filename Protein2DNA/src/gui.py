import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from src.get_codons import CodonDatabase
from src.translator import translate


class ProteinToDNAApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Protein to DNA Translator")
        self.root.geometry("900x600")

        # 加载数据库（只加载一次，保持 species_list 缓存）
        self.db = CodonDatabase()
        self.species_list = self.db.species_list

        self.create_widgets()

    def create_widgets(self):
        # 主框架（带内边距）
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # ---- 第1行：物种 ----
        ttk.Label(main_frame, text="Species:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.species_var = tk.StringVar()
        self.species_combo = ttk.Combobox(
            main_frame, textvariable=self.species_var, values=self.species_list, state="readonly"
        )
        self.species_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        if self.species_list:
            self.species_combo.current(0)

        # ---- 第2行：蛋白质序列 ----
        ttk.Label(main_frame, text="Protein Sequence:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.protein_entry = ttk.Entry(main_frame, width=50)
        self.protein_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)

        # ---- 第3行：GC min ----
        ttk.Label(main_frame, text="GC min (%) :").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.gc_min_entry = ttk.Entry(main_frame, width=10)
        self.gc_min_entry.insert(0, "40")
        self.gc_min_entry.grid(row=2, column=1, sticky=tk.W, pady=2)

        # ---- 第4行：GC max ----
        ttk.Label(main_frame, text="GC max (%) :").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.gc_max_entry = ttk.Entry(main_frame, width=10)
        self.gc_max_entry.insert(0, "60")
        self.gc_max_entry.grid(row=3, column=1, sticky=tk.W, pady=2)

        # ---- 第5行：规避序列 ----
        ttk.Label(main_frame, text="Avoid motifs (comma separated):").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.avoid_entry = ttk.Entry(main_frame, width=50)
        self.avoid_entry.grid(row=4, column=1, sticky="we", pady=2)

        # ---- 第6行：翻译按钮 ----
        self.translate_btn = ttk.Button(main_frame, text="Translate", command=self.on_translate)
        self.translate_btn.grid(row=5, column=0, columnspan=2, pady=10)

        # ---- 第7行：DNA序列显示（滚动+自动换行） ----
        ttk.Label(main_frame, text="DNA Sequence:").grid(row=6, column=0, sticky=tk.W, pady=(5, 0))
        self.dna_text = scrolledtext.ScrolledText(
            main_frame,
            height=10,
            width=70,
            wrap=tk.WORD,  # 自动换行
            state="normal",  # 初始可写，但我们会设为只读
        )
        self.dna_text.grid(row=7, column=0, columnspan=2, pady=(0, 5), sticky="nsew")

        # ---- 第8行：统计信息（用标签显示） ----
        self.stats_label = ttk.Label(main_frame, text="", anchor=tk.W, justify=tk.LEFT)
        self.stats_label.grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=(0, 5))

        # 调整网格权重
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(7, weight=1)  # DNA文本框可扩展
        main_frame.rowconfigure(8, weight=0)  # 统计标签固定高度

    def on_translate(self):
        """按钮点击事件：收集输入 -> 调用翻译 -> 显示结果或错误"""
        # 1. 收集物种和蛋白质序列
        species = self.species_var.get()
        protein = self.protein_entry.get().strip()
        if not protein:
            messagebox.showerror("Input Error", "Please enter a protein sequence.")
            return
        if not species or species not in self.species_list:
            messagebox.showerror("Input Error", "Please select a valid species.")
            return

        # 2. 收集 GC 范围（整数转小数）
        try:
            gc_min = float(self.gc_min_entry.get()) / 100.0
            gc_max = float(self.gc_max_entry.get()) / 100.0
        except ValueError:
            messagebox.showerror("Input Error", "GC min and max must be numbers.")
            return

        # 3. 收集规避序列（列表）
        avoid_text = self.avoid_entry.get().strip()
        avoid_list = [m.strip() for m in avoid_text.split(",") if m.strip()]

        # 4. 调用核心翻译函数
        try:
            result = translate(species, protein, avoid_list, gc_min, gc_max)
        except ValueError as e:
            messagebox.showerror("Translation Error", str(e))
            return
        except Exception as e:
            messagebox.showerror("Unexpected Error", str(e))
            return

        # ---- 更新DNA序列显示（设为只读，防止误改） ----
        self.dna_text.config(state="normal")  # 临时启用编辑
        self.dna_text.delete(1.0, tk.END)
        self.dna_text.insert(tk.END, result["dna"])
        self.dna_text.config(state="disabled")  # 设置为只读，用户无法修改

        # ---- 更新统计信息（包含警告支持） ----
        stats_text = (
            f"Length: {result['length']} bp | "
            f"GC: {result['gc_percent']:.1f}% | "
            f"Compromises: {result['compromises']}"
        )

        # 如果有警告，附加到统计信息中
        if result['status'] == 'warning' and result.get('warnings'):
            stats_text += "\n⚠️ " + "; ".join(result['warnings'])
            self.stats_label.config(text=stats_text, foreground='orange')
        else:
            # 成功状态，显示正常颜色
            self.stats_label.config(text=stats_text, foreground='black')

    def run(self):
        self.root.mainloop()