import tkinter as tk
from tkinter import messagebox
import subprocess
import sys
import os

def launch_imatges_gui():
    script_path = os.path.join(os.getcwd(), "./PhotoSearcher/sql.py")  # Adjust path if the script is elsewhere
    if os.path.exists(script_path):
        subprocess.Popen([sys.executable, script_path])  # Launches script in new process
    else:
        messagebox.showerror("File Not Found", f"'sql.py' not found at: {script_path}")

def launch_renombrar_script():
    script_path = os.path.join(os.getcwd(), "./gui.py")  # Adjust path if the script is elsewhere
    if os.path.exists(script_path):
        subprocess.Popen([sys.executable, script_path])  # Launches script in new process
    else:
        messagebox.showerror("File Not Found", f"'gui.py' not found at: {script_path}")

def main_screen():
    root = tk.Tk()
    root.title("Photo Matcher Launcher")
    root.geometry("400x250")
    root.resizable(False, False)

    label = tk.Label(root, text="Escull una funcionalitat", font=("Arial", 16))
    label.pack(pady=20)

    img_btn = tk.Button(root, text="🟦 Banc d'imatges", font=("Arial", 14), width=30, command=launch_imatges_gui)
    img_btn.pack(pady=10)

    other_btn = tk.Button(root, text="🟨 Renombrar Fotos", font=("Arial", 14), width=30, command=launch_renombrar_script)
    other_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main_screen()
