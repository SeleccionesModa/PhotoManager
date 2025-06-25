import tkinter as tk
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk
import subprocess
import time
import threading
import os
import shutil
from datetime import datetime
import glob  # ✅ Helps scan directories

DATABASE_PATH = "./PhotoSearcher/photos.db"
PAGE_SIZE = 9  # Load images in blocks of 9

class ImageSearchApp:
    def threaded_database_update(self):
        """Threaded function to sync images directory with the SQLite database."""
        self.search_status.config(text="Updating database... ⏳")
        self.root.update()

        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()

            # ✅ Fetch all stored file paths FIRST
            cursor.execute("SELECT filepath FROM images")
            stored_files = set(row[0] for row in cursor.fetchall())

            existing_files = set()
            new_files = []

            # ✅ Scan folder and detect new files
            for entry in os.scandir("T:/Imatges Concrete"):
                if entry.is_file():
                    file_path = os.path.join("T:/Imatges Concrete", entry.name)
                    existing_files.add(file_path)

                    if file_path not in stored_files:
                        new_files.append((
                            entry.name,
                            file_path,
                            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        ))

            # ✅ Detect deleted files
            deleted_files = stored_files - existing_files

            # ✅ Remove deleted files from database
            if deleted_files:
                cursor.execute("BEGIN")
                cursor.executemany(
                    "DELETE FROM images WHERE filepath = ?",
                    [(fp,) for fp in deleted_files]
                )
                cursor.execute("COMMIT")
                self.search_status.config(text=f"❌ Deleted {len(deleted_files)} missing images.")

            # ✅ Insert new files into database
            if new_files:
                cursor.execute("BEGIN")
                cursor.executemany(
                    "INSERT INTO images (filename, filepath, upload_date) VALUES (?, ?, ?)",
                    new_files
                )
                cursor.execute("COMMIT")
                self.search_status.config(text=f"✅ Added {len(new_files)} new images!")

            conn.close()

        except Exception as e:
            self.search_status.config(text=f"❌ Error: {str(e)}")

        self.root.after(5000, lambda: self.search_status.config(text=""))

    def update_database(self):
        """Starts database update in a separate thread to prevent UI freeze."""
        threading.Thread(target=self.threaded_database_update, daemon=True).start()
    
    def __init__(self, root):
        self.root = root
        self.root.title("Image Search")
        self.root.attributes('-fullscreen', True)  # Enable fullscreen

        self.selected_files = []
        self.selection_states = {}  # Stores {file_path: BooleanVar()}
        self.selected_data = {}  # Stores {filepath: filename}

    # ✅ Ensure temp folder is reset
        temp_folder = os.path.join(os.getenv("USERPROFILE"), "Downloads\\TempPhotos")
        if os.path.exists(temp_folder):
            shutil.rmtree(temp_folder)  # ✅ Deletes all previous images
        os.makedirs(temp_folder)  # ✅ Recreate empty temp folder

        ttk.Button(root, text="Exit Fullscreen", command=self.exit_fullscreen).pack(anchor='ne', padx=10, pady=10)

        ttk.Button(root, text="Update Database", command=lambda: threading.Thread(target=self.update_database).start()).pack(pady=10)

        ttk.Label(root, text="Selected Photos").pack(anchor='ne', padx=10, pady=5)
        self.selected_dropdown = ttk.Combobox(root, values=[], state="readonly")
        self.selected_dropdown.pack(anchor='ne', padx=10)

        ttk.Label(root, text="Search Image:").pack(pady=10)
        self.search_entry = ttk.Entry(root, width=40)  # Define search_entry first!
        self.search_entry.pack()
        self.search_entry.bind("<Return>", self.search_images)  # ✅ Move binding after definition

        self.search_status = ttk.Label(root, text="", font=("Arial", 12))  
        self.search_status.pack(pady=5)

        self.download_status = ttk.Label(root, text="", font=("Arial", 12), foreground="green")
        self.download_status.pack(pady=5)  # Positioned below download button

        self.image_frames = []
        self.image_frame_container = tk.Frame(root)
        self.image_frame_container.pack(pady=20)

        for i in range(PAGE_SIZE):
            frame = tk.Label(self.image_frame_container)
            frame.grid(row=i // 3, column=i % 3, padx=10, pady=10)
            self.image_frames.append(frame)

        ttk.Button(root, text="Download Selected", command=self.run_download_script).pack(pady=10)
   
        self.nav_frame = tk.Frame(root)
        self.nav_frame.pack()

        self.prev_button = ttk.Button(self.nav_frame, text="Previous", command=self.previous_page)
        self.prev_button.pack(side="left", padx=20, pady=10)

        self.page_var = tk.StringVar()
        self.page_selector = ttk.Combobox(self.nav_frame, textvariable=self.page_var, state="readonly")
        self.page_selector.pack(side="left", padx=20)
        self.page_selector.bind("<<ComboboxSelected>>", self.jump_to_page)
        
        self.next_button = ttk.Button(self.nav_frame, text="Next", command=self.next_page)
        self.next_button.pack(side="right", padx=20, pady=10)

        # Image Data
        self.image_paths = []
        self.current_page = 0

    def exit_fullscreen(self):
        self.root.attributes('-fullscreen', False)

    def search_images(self, event=None):
        self.search_status.config(text="Searching...")
        self.root.update()

        query = self.search_entry.get()
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        # ✅ Fetch all matching images (removes `LIMIT`)
        cursor.execute("SELECT filepath, filename FROM images WHERE filename LIKE ?", ('%' + query + '%',))
        data = cursor.fetchall()
        
        self.image_paths = [row[0] for row in data]
        self.image_names = [row[1] for row in data]
        
        conn.close()

        self.current_page = 0  # ✅ Always start on the first page
        self.update_page_selector()
        self.selection_states = {path: False for path in self.image_paths}
        self.display_images()

        self.search_status.config(text="")

    def update_page_selector(self):
        total_pages = max(1, (len(self.image_paths) + PAGE_SIZE - 1) // PAGE_SIZE)  # ✅ Calculates total pages
        self.page_selector["values"] = [str(i + 1) for i in range(total_pages)]
        self.page_selector.current(self.current_page)

    def display_images(self):
        # ✅ Remove previous images
        for frame in self.image_frames:
            frame.destroy()

        self.image_frames = []

        for i, image_path in enumerate(self.image_paths[self.current_page * PAGE_SIZE : (self.current_page + 1) * PAGE_SIZE]):
            img_frame = tk.Frame(self.image_frame_container)
            img_frame.grid(row=i // 3, column=i % 3, padx=10, pady=10)

            # ✅ Lazy load images in a separate thread
            threading.Thread(target=self.load_image, args=(img_frame, image_path)).start()

            # Restore selection state
            var = tk.BooleanVar(value=self.selection_states.get(image_path, False))
            checkbox = ttk.Checkbutton(img_frame, variable=var, command=lambda path=image_path, var=var: self.toggle_selection(path, var))
            checkbox.pack(side="bottom")

            self.image_frames.append(img_frame)

        #pagination display
        self.page_selector.current(self.current_page)

    def load_image(self, frame, image_path):
        img = Image.open(image_path)
        img.thumbnail((100, 100))
        img = ImageTk.PhotoImage(img)

        img_label = tk.Label(frame, image=img)
        img_label.image = img
        img_label.pack(side="top")

    def show_full_image(self, image_path):
        top = tk.Toplevel(self.root)
        top.title("Image Preview")
        
        img = Image.open(image_path)
        img.thumbnail((500, 500))
        img = ImageTk.PhotoImage(img)

        label = ttk.Label(top, image=img)
        label.image = img  # Keep reference
        label.pack()

    def update_selected_dropdown(self):
        selected_names = list(self.selected_data.values())  # ✅ Get filenames from stored selections
        self.selected_dropdown["values"] = selected_names
        
        if selected_names:
            self.selected_dropdown.set(selected_names[0])  # ✅ Keep first item intact
        else:
            self.selected_dropdown.set("No files selected")  # ✅ Show default message

    def toggle_selection(self, path, var):
        self.selection_states[path] = var.get()
        
        if var.get():  # ✅ Selected
            if path not in self.selected_files:
                self.selected_files.append(path)
            self.selected_data[path] = self.image_names[self.image_paths.index(path)]  # ✅ Store correct filename
        else:  # ❌ Deselected
            if path in self.selected_files:
                self.selected_files.remove(path)
            self.selected_data.pop(path, None)  # ✅ Remove from stored selections
        
        self.update_selected_dropdown()

    def save_selection(self):
        with open("selected_files.txt", "w") as f:
            for file in self.selected_files:
                f.write(file + "\n")

    def execute_download_script(self):
        script_path = "./PhotoSearcher/download_photos.bat"
        subprocess.run(script_path, shell=True)  # ✅ Run synchronously now

        # ✅ Update message once copying is done
        self.download_status.config(text="Download complete! Check folder.")
        self.root.after(3000, lambda: self.download_status.config(text=""))  # Remove after 3 sec

    def run_download_script(self):
        if not self.selected_files:  # ✅ Check if selection is empty
            self.download_status.config(text="Nothing selected")  # ✅ Show error message
            return
        
        self.download_status.config(text="Downloading...")
        self.root.update()  # ✅ Refresh UI immediately

        self.generate_batch_script()  # ✅ Create batch script with bulk-copy method

        # ✅ Run script without freezing UI
        threading.Thread(target=self.execute_download_script).start()

    def execute_download_script(self):
        script_path = "./PhotoSearcher/download_photos.bat"
        subprocess.run(script_path, shell=True)  # ✅ Run batch script synchronously

        self.download_status.config(text="Download complete! Check folder.")
        self.root.after(3000, lambda: self.download_status.config(text=""))

    def generate_batch_script(self):
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        user_folder = os.getenv("USERPROFILE")  # ✅ Get correct user folder
        destination_folder = os.path.join(user_folder, f"Downloads\\Photos_{timestamp}")
        temp_folder = os.path.join(user_folder, "Downloads\\TempPhotos")  # ✅ No permission issues

        # ✅ Create temp folder if it doesn't exist
        os.makedirs(temp_folder, exist_ok=True)

        # ✅ Copy selected files into temp folder first
        for file_path in self.selected_files:
            shutil.copy(file_path, temp_folder)

        # ✅ Write batch script for bulk copying
        with open("./PhotoSearcher/download_photos.bat", "w") as f:
            f.write(f"@echo off\nmkdir \"{destination_folder}\"\n")
            f.write(f"xcopy \"{temp_folder}\\*\" \"{destination_folder}\" /Q /Y /C /E\n")  # ✅ Fast bulk-copy
            f.write("echo Download complete!")

    def next_page(self):
        if (self.current_page + 1) * PAGE_SIZE < len(self.image_paths):
            self.current_page += 1
            # ✅ Preload images while updating UI
            threading.Thread(target=self.display_images).start()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            # ✅ Preload images while updating UI
            threading.Thread(target=self.display_images).start()

    def jump_to_page(self, event):
        selected_page = int(self.page_var.get()) - 1  # Convert dropdown selection to index
        
        if 0 <= selected_page < ((len(self.image_paths) + PAGE_SIZE - 1) // PAGE_SIZE):  # ✅ Ensure valid page
            self.current_page = selected_page
            threading.Thread(target=self.display_images).start()  # ✅ Load images without freezing UI

# Run the App
root = tk.Tk()
app = ImageSearchApp(root)
root.mainloop()
