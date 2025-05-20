import tkinter as tk
from tkinter import ttk
import sqlite3
from PIL import Image, ImageTk

DATABASE_PATH = "photos.db"
PAGE_SIZE = 9  # Load images in blocks of 9

class ImageSearchApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Search")
        self.root.attributes('-fullscreen', True)  # Enable fullscreen

        # Create a close button for exiting fullscreen
        ttk.Button(root, text="Exit Fullscreen", command=self.exit_fullscreen).pack(anchor='ne', padx=10, pady=10)

        # Search Field
        ttk.Label(root, text="Search Image:").pack(pady=10)
        self.search_entry = ttk.Entry(root, width=40)
        self.search_entry.pack()
        ttk.Button(root, text="Search", command=self.search_images).pack(pady=5)

        # Image Grid
        self.image_frames = []
        self.image_frame_container = tk.Frame(root)
        self.image_frame_container.pack(pady=20)

        for i in range(PAGE_SIZE):
            frame = tk.Label(self.image_frame_container)
            frame.grid(row=i // 3, column=i % 3, padx=10, pady=10)
            self.image_frames.append(frame)

        # Navigation Buttons
        self.nav_frame = tk.Frame(root)
        self.nav_frame.pack()

        self.prev_button = ttk.Button(self.nav_frame, text="Previous", command=self.previous_page)
        self.prev_button.pack(side="left", padx=20, pady=10)

        # **Dropdown for Page Selection**
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

    def search_images(self):
        query = self.search_entry.get()
    
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT filepath FROM images WHERE filename LIKE ?", ('%' + query + '%',))
        self.image_paths = [row[0] for row in cursor.fetchall()]
        conn.close()

        self.current_page = 0
        self.update_page_selector()  # ✅ Update dropdown values
        self.display_images()


    def update_page_selector(self):
        total_pages = max(1, (len(self.image_paths) + PAGE_SIZE - 1) // PAGE_SIZE)
        self.page_selector["values"] = [str(i + 1) for i in range(total_pages)]
        self.page_selector.current(self.current_page)

    def display_images(self):
        # Clear previous images
        for frame in self.image_frames:
            frame.config(image="", text="")
        
        # Display images
        for i, image_path in enumerate(self.image_paths[self.current_page * PAGE_SIZE : (self.current_page + 1) * PAGE_SIZE]):
            img = Image.open(image_path)
            img.thumbnail((150, 150))
            img = ImageTk.PhotoImage(img)

            self.image_frames[i].config(image=img)
            self.image_frames[i].image = img  # Keep reference
            self.image_frames[i].bind("<Button-1>", lambda e, path=image_path: self.show_full_image(path))

        #pagination display
        self.page_selector.current(self.current_page)

    def show_full_image(self, image_path):
        top = tk.Toplevel(self.root)
        top.title("Image Preview")
        
        img = Image.open(image_path)
        img.thumbnail((500, 500))
        img = ImageTk.PhotoImage(img)

        label = ttk.Label(top, image=img)
        label.image = img  # Keep reference
        label.pack()


    def next_page(self):
        if (self.current_page + 1) * PAGE_SIZE < len(self.image_paths):
            self.current_page += 1
            self.display_images()

    def previous_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.display_images()

    def jump_to_page(self, event):
        selected_page = int(self.page_var.get()) - 1
        self.current_page = selected_page
        self.display_images()

# Run the App
root = tk.Tk()
app = ImageSearchApp(root)
root.mainloop()
