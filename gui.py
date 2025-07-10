import os
import shutil
import pandas as pd
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
import tkinter as tk
from tkinter import filedialog, messagebox

# ------------------------------
# Corner GUI
# ------------------------------
def launch_corner_gui():
    root = tk.Tk()
    root.withdraw()

    excel_file = filedialog.askopenfilename(
        title="Select the Corner Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not excel_file:
        messagebox.showwarning("No File", "No Excel file selected.")
        return
    
    photo_directory = "T:/Imatges Concrete"
    destination_directory = "./foundPhotos"
    os.makedirs(destination_directory, exist_ok=True)

    # Check if folder is non-empty
    if os.listdir(destination_directory):
        clear = messagebox.askyesno("Folder Not Empty", "There are already images in the destination folder.\nDo you want to delete them and proceed?")
        if clear:
            for filename in os.listdir(destination_directory):
                file_path = os.path.join(destination_directory, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        else:
            messagebox.showinfo("Aborted", "Operation canceled. No files were copied.")
            return
        
    df = pd.read_excel(excel_file)
    codes_array = df.iloc[:, 4].astype(str).str.replace("-", "_").tolist()
    codes_array = list(set(codes_array))  # Remove duplicates
    print(codes_array)
    codesPhotos_array = os.listdir(photo_directory)

    matches = [code for code in codes_array if any(code in photo for photo in codesPhotos_array)]
    missing = [code for code in codes_array if not any(code in photo for photo in codesPhotos_array)]

    if missing and messagebox.askyesno("Missing Codes", f"{len(missing)} missing articles. Save to Excel?"):
        pd.DataFrame({"Missing Articles": missing}).drop_duplicates().to_excel("missing_articles.xlsx", index=False)
        messagebox.showinfo("Saved", "Missing articles saved as 'missing_articles.xlsx'.")

    priority_order = ["MOD", "ED", "FLATFRONT", "FLATBACK"]
    article_counters = defaultdict(int)

    def extract_article_color(photo_name):
        parts = photo_name.split("_")
        if len(parts) >= 5:
            article_color = "_".join(parts[:2])
            suffix = os.path.splitext(parts[4])[0]
            cleaned_suffix = next((p for p in priority_order if p in suffix), suffix)
            return article_color, cleaned_suffix
        return None, None

    sorted_photos = []
    for photo in codesPhotos_array:
        ac, suffix = extract_article_color(photo)
        if ac and suffix and ac in matches:
            sorted_photos.append((ac, suffix, photo))

    photos_by_color = defaultdict(list)
    for ac, suffix, photo in sorted_photos:
        photos_by_color[ac].append((suffix, photo))

    copy_tasks = []
    for ac, photos in photos_by_color.items():
        photos.sort(key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else float('inf'))
        article_counters[ac] = 0
        for suffix, photo in photos:
            article_counters[ac] += 1
            new_name = f"{ac}_{article_counters[ac]}{os.path.splitext(photo)[-1]}"
            src = os.path.join(photo_directory, photo)
            dst = os.path.join(destination_directory, new_name)
            if os.path.exists(src):
                copy_tasks.append((src, dst))

    # --- Progress Window ---
    progress = tk.Toplevel()
    progress.title("Working...")
    progress.geometry("300x100")
    progress.resizable(False, False)
    tk.Label(progress, text="Copying and renaming photos...", font=("Helvetica", 12)).pack(pady=25)
    progress.update()

    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(lambda task: shutil.copy(*task), copy_tasks)

    progress.destroy()
    messagebox.showinfo("Done", f"{len(copy_tasks)} photos copied to '{destination_directory}'.")


# ------------------------------
# B2B GUI
# ------------------------------
def launch_b2b_gui():
    root = tk.Tk()
    root.withdraw()

    excel_file = filedialog.askopenfilename(
        title="Select the B2B Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not excel_file:
        messagebox.showwarning("No File", "No Excel file selected.")
        return

    photo_directory = "T:/Imatges Concrete"
    destination_directory = "./foundPhotos"
    os.makedirs(destination_directory, exist_ok=True)

    # Check if folder is non-empty
    if os.listdir(destination_directory):
        clear = messagebox.askyesno("Folder Not Empty", "There are already images in the destination folder.\nDo you want to delete them and proceed?")
        if clear:
            for filename in os.listdir(destination_directory):
                file_path = os.path.join(destination_directory, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        else:
            messagebox.showinfo("Aborted", "Operation canceled. No files were copied.")
            return
        
    df = pd.read_excel(excel_file)
    codes_array = df.iloc[:, 28].dropna().astype(str).str.strip().tolist()
    unique_codes = list(set(codes_array))
    codes_array = [code[:-3] + "_" + code[-3:] for code in unique_codes]

    codesPhotos_array = os.listdir(photo_directory)

    matches = [code for code in codes_array if any(code in photo for photo in codesPhotos_array)]
    missing = [code for code in codes_array if not any(code in photo for photo in codesPhotos_array)]

    if missing and messagebox.askyesno("Missing Codes", f"{len(missing)} missing articles. Save to Excel?"):
        pd.DataFrame({"Missing Articles": missing}).drop_duplicates().to_excel("missing_articles.xlsx", index=False)
        messagebox.showinfo("Saved", "Missing articles saved as 'missing_articles.xlsx'.")

    priority_order = ["ED1", "FLATFRONT", "FLATBACK"]
    article_counters = defaultdict(int)

    def extract_article_color(photo_name):
        parts = photo_name.split("_")
        if len(parts) >= 5:
            article_color = "_".join(parts[:2])
            suffix = os.path.splitext(parts[4])[0]
            cleaned_suffix = next((p for p in priority_order if p in suffix), suffix)
            return article_color, cleaned_suffix
        return None, None

    sorted_photos = []
    for photo in codesPhotos_array:
        ac, suffix = extract_article_color(photo)
        if ac and suffix and ac in matches:
            sorted_photos.append((ac, suffix, photo))

    photos_by_color = defaultdict(list)
    for ac, suffix, photo in sorted_photos:
        photos_by_color[ac].append((suffix, photo))
        
    copy_tasks = []
    for ac, photos in photos_by_color.items():
        filtered = [(suf, ph) for suf, ph in photos if suf in priority_order or "FLAT" in suf or "FLATED" in suf]
        if not filtered:
            continue
        filtered.sort(key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else float('inf'))
        article_counters[ac] = 0
        for suffix, photo in filtered:
            article_counters[ac] += 1
            ac_clean = ac.replace("_", "")
            new_name = f"{ac_clean}-{article_counters[ac]}{os.path.splitext(photo)[-1]}"
            src = os.path.join(photo_directory, photo)
            dst = os.path.join(destination_directory, new_name)
            if os.path.exists(src):
                copy_tasks.append((src, dst))

    # --- Progress Window ---
    progress = tk.Toplevel()
    progress.title("Working...")
    progress.geometry("300x100")
    progress.resizable(False, False)
    tk.Label(progress, text="Copying and renaming photos...", font=("Helvetica", 12)).pack(pady=25)
    progress.update()

    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(lambda task: shutil.copy(*task), copy_tasks)

    progress.destroy()
    messagebox.showinfo("Done", f"{len(copy_tasks)} photos copied to '{destination_directory}'.")


def launch_excelClients_gui():
    root = tk.Tk()
    root.withdraw()

    excel_file = filedialog.askopenfilename(
        title="Select the Article-Color Excel File",
        filetypes=[("Excel files", "*.xlsx *.xls")]
    )
    if not excel_file:
        messagebox.showwarning("No File", "No Excel file selected.")
        return

    photo_directory = "T:/Imatges Concrete"
    destination_directory = "./foundPhotos"
    os.makedirs(destination_directory, exist_ok=True)

    # Check if folder is non-empty
    if os.listdir(destination_directory):
        clear = messagebox.askyesno("Folder Not Empty", "There are already images in the destination folder.\nDo you want to delete them and proceed?")
        if clear:
            for filename in os.listdir(destination_directory):
                file_path = os.path.join(destination_directory, filename)
                if os.path.isfile(file_path):
                    os.remove(file_path)
        else:
            messagebox.showinfo("Aborted", "Operation canceled. No files were copied.")
            return
        
    df = pd.read_excel(excel_file, skiprows=2)

    # Build codes_array from Column F and G
    df_filtered = df[[df.columns[5], df.columns[6]]].dropna()
    df_filtered = df_filtered.astype(str)
    codes_array = (df_filtered.iloc[:, 0] + "_" + df_filtered.iloc[:, 1]).str.strip().str.replace("-", "_").tolist()
    codes_array = list(set(codes_array))  # drop duplicates

    codesPhotos_array = os.listdir(photo_directory)

    matches = [code for code in codes_array if any(code in photo for photo in codesPhotos_array)]
    missing = [code for code in codes_array if not any(code in photo for photo in codesPhotos_array)]

    if missing and messagebox.askyesno("Articles no trobats", f"{len(missing)} articles no trobats. Desar la llista en Excel?"):
        pd.DataFrame({"Articles no trobats": missing}).drop_duplicates().to_excel("missing_articles.xlsx", index=False)
        messagebox.showinfo("Desat", "Articles no trobats desats com a 'missing_articles.xlsx'.")

    # Use same logic as in Corner function
    priority_order = ["MOD", "ED", "FLATFRONT", "FLATBACK"]
    article_counters = defaultdict(int)

    def extract_article_color(photo_name):
        parts = photo_name.split("_")
        if len(parts) >= 5:
            article_color = "_".join(parts[:2])
            suffix = os.path.splitext(parts[4])[0]
            cleaned_suffix = next((p for p in priority_order if p in suffix), suffix)
            return article_color, cleaned_suffix
        return None, None

    sorted_photos = []
    for photo in codesPhotos_array:
        ac, suffix = extract_article_color(photo)
        if ac and suffix and ac in matches:
            sorted_photos.append((ac, suffix, photo))

    photos_by_color = defaultdict(list)
    for ac, suffix, photo in sorted_photos:
        photos_by_color[ac].append((suffix, photo))

    copy_tasks = []
    for ac, photos in photos_by_color.items():
        photos.sort(key=lambda x: priority_order.index(x[0]) if x[0] in priority_order else float('inf'))
        article_counters[ac] = 0
        for suffix, photo in photos:
            article_counters[ac] += 1
            new_name = f"{ac}_{article_counters[ac]}{os.path.splitext(photo)[-1]}"
            src = os.path.join(photo_directory, photo)
            dst = os.path.join(destination_directory, new_name)
            if os.path.exists(src):
                copy_tasks.append((src, dst))

    # Progress window
    progress = tk.Toplevel()
    progress.title("Creant pantalla...")
    progress.geometry("300x100")
    tk.Label(progress, text="Copiant i renombrant fotos...", font=("Helvetica", 12)).pack(pady=25)
    progress.update()

    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(lambda task: shutil.copy(*task), copy_tasks)

    progress.destroy()
    messagebox.showinfo("Done", f"{len(copy_tasks)} photos copied to '{destination_directory}'.")

# ------------------------------
# Main App Window
# ------------------------------
def main_screen():
    root = tk.Tk()
    root.title("Photo Matcher Launcher")
    root.geometry("420x260")
    root.resizable(False, False)

    label = tk.Label(root, text="Select which matcher to run", font=("Helvetica", 16))
    label.pack(pady=20)

    corner_btn = tk.Button(root, text="🔷 Corner Digital", font=("Helvetica", 14), width=30, command=launch_corner_gui)
    corner_btn.pack(pady=12)

    b2b_btn = tk.Button(root, text="🔶Excel B2B", font=("Helvetica", 14), width=30, command=launch_b2b_gui)
    b2b_btn.pack(pady=12)

    third_btn = tk.Button(
        root,
        text="🟩 Excel Client",
        font=("Helvetica", 14),
        width=30,
        command=launch_excelClients_gui
    )
    third_btn.pack(pady=12)

    credits = tk.Label(root, text="Made with ❤️ by Selecciones + Copi", font=("Helvetica", 10), fg="gray")
    credits.pack(side="bottom", pady=10)

    root.protocol("WM_DELETE_WINDOW", root.quit)
    root.mainloop()


# ------------------------------
# Run the App
# ------------------------------
if __name__ == "__main__":
    main_screen()
   
