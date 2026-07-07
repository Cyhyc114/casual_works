# main.py
import tkinter as tk
from src.gui import ProteinToDNAApp

def main():
    root = tk.Tk()
    app = ProteinToDNAApp(root)
    app.run()

if __name__ == "__main__":
    main()