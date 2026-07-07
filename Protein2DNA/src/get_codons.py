import sys
import os
import json
import shutil


def get_base_dir():
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        return os.path.dirname(current_dir)


class CodonDatabase:
    def __init__(self):
        base_dir = get_base_dir()
        data_dir = os.path.join(base_dir, "data")
        main_file = os.path.join(data_dir, "all_codon_tables.json")
        backup_file = os.path.join(data_dir, ".all_codon_tables_bak.json")

        def is_valid_json(filepath):
            if not os.path.exists(filepath):
                return False
            try:
                with open(filepath, "r", encoding="utf-8") as f:
                    json.load(f)
                return True
            except (json.JSONDecodeError, IOError):
                return False

        if not is_valid_json(main_file):
            if os.path.exists(backup_file):
                try:
                    shutil.copy2(backup_file, main_file)
                except Exception as e:
                    raise RuntimeError(f"recovery failed:{e}")
            else:
                raise FileNotFoundError(f"{main_file} dont exist, and back-up file not found.")

        with open(main_file, "r", encoding="utf-8") as f:
            self.tables: dict[str, dict[str, dict[str, float]]] = json.load(f)
        self.json_path = main_file
        self.species_list = list(self.tables.keys())

    def add_new(self, taxid: str):
        pass
