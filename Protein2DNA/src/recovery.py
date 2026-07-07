# src/recovery.py
import os
import json
import shutil
import python_codon_tables as pct
from get_codons import get_base_dir  # 复用路径获取函数


def regenerate_codon_tables():
    """
    从内置数据重新生成 all_codon_tables.json 并创建备份。
    返回成功信息或抛出异常。
    """
    base_dir = get_base_dir()
    data_dir = os.path.join(base_dir, "data")
    main_file = os.path.join(data_dir, "all_codon_tables.json")
    backup_file = os.path.join(data_dir, ".all_codon_tables_bak.json")

    os.makedirs(data_dir, exist_ok=True)

    all_tables = pct.get_all_available_codons_tables()

    with open(main_file, "w", encoding="utf-8") as f:
        json.dump(all_tables, f, indent=4, ensure_ascii=False)

    shutil.copy2(main_file, backup_file)

    return main_file
