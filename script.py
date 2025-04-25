import os
import tkinter 
from tkinter import ttk
from tkinter.filedialog import askdirectory
import pandas as pd
import shutil 

#ask user where the photos are

'''def askpath():
    path = askdirectory(title='Select Folder') # shows dialog box and return the path
    print(path)
    entries = os.listdir(path)
    for entry in entries:
        print(entry)
        
root = tkinter.Tk()
root.config(width=500, height=300)
root.title("Botón en Tk")
boton = ttk.Button(text="Selecciona la carpeta con fotos", command=askpath)
boton.place(x=50, y=50)
root.mainloop()'''

# Load the Excel file
file_path = "./CornerDigitalExample.xlsx"  # Update this with the actual file path
df = pd.read_excel(file_path)

# Extract column E values and replace '-' with '_'
codes_array = df.iloc[:, 4].astype(str).str.replace("-", "_").tolist()  # Column E is index 4 (zero-based)

print(codes_array)

# Extract the names of the photos
photo_directory = "./fototest"
codesPhotos_array = [entry for entry in os.listdir(photo_directory)]  # List comprehension for cleaner code

print("Codes from photos:", codesPhotos_array)

#check which photos exist in directory:

matches = [code for code in codes_array if any(code in photo for photo in codesPhotos_array)]

print("Matching codes found in photos:", matches)

# Find missing codes (not found in any photo filenames)
missing_codes = [code for code in codes_array if not any(code in photo for photo in codesPhotos_array)]

# Ask user if they want to download missing articles
user_choice = input("Do you want to download missing articles? (y/n): ").strip().lower()

if user_choice == "y":
    missing_df = pd.DataFrame({"Missing Articles": missing_codes}).drop_duplicates()
    missing_df.to_excel("missing_articles.xlsx", index=False, )
    print("Missing articles saved as 'missing_articles.xlsx'.")
else:
    print("No file downloaded.")

import shutil
import os
from collections import defaultdict

# Define source and destination directories
photo_directory = "./fototest"
destination_directory = "./foundPhotos"

# Ensure the destination directory exists
os.makedirs(destination_directory, exist_ok=True)

# Dictionary to track how many times each ARTICLE_COLOR appears
counter = defaultdict(int)

# Move and rename photos that match codes in codes_array
for photo in codesPhotos_array:
    for code in codes_array:
        if code in photo:  # Check if ARTICLE_COLOR exists in filename
            counter[code] += 1  # Increment count for this ARTICLE_COLOR
            
            # Generate new filename with numbering
            new_filename = f"{code}_{counter[code]}{os.path.splitext(photo)[-1]}"  # Preserve file extension
            
            source_path = os.path.join(photo_directory, photo)
            destination_path = os.path.join(destination_directory, new_filename)
            
            shutil.copy(source_path, destination_path)
            break  # Stop checking once we find a match

print(f"Matching photos copied and renamed in '{destination_directory}' successfully!")


'''
import shutil
import os
from collections import defaultdict

# Define source and destination directories
photo_directory = "./fototest"
destination_directory = "./foundPhotos"

# Ensure the destination directory exists
os.makedirs(destination_directory, exist_ok=True)

# Define the priority order
priority_order = ["MOD", "FLATFRONT", "FLATBACK", "ED1"]

# Dictionary to track numbering for each ARTICLE_COLOR
article_counters = defaultdict(int)

# Function to extract ARTICLE_COLOR and suffix from filename
def extract_article_color(photo_name):
    parts = photo_name.split("_")
    if len(parts) >= 2:
        article_color = "_".join(parts[:2])  # First two parts form ARTICLE_COLOR
        suffix = parts[-1]  # Last part determines priority
        return article_color, suffix
    return None, None

# Collect and sort photos by priority
sorted_photos = []
for photo in codesPhotos_array:
    article_color, suffix = extract_article_color(photo)
    if article_color and suffix:
        sorted_photos.append((article_color, suffix, photo))

# Sort by ARTICLE_COLOR and then by priority order
sorted_photos.sort(key=lambda x: (x[0], priority_order.index(x[1]) if x[1] in priority_order else float("inf")))

# Process photos and rename them
for article_color, suffix, photo in sorted_photos:
    article_counters[article_color] += 1
    new_filename = f"{article_color}_{article_counters[article_color]}{os.path.splitext(photo)[-1]}"  # Preserve file extension
    
    source_path = os.path.join(photo_directory, photo)
    destination_path = os.path.join(destination_directory, new_filename)
    
    shutil.copy(source_path, destination_path)

print(f"Matching photos copied and renamed in '{destination_directory}' with correct ordering!")

✅ Extracts ARTICLE_COLOR correctly from filenames ✅ Sorts photos based on priority (MOD → FLATFRONT → FLATBACK → ED1) ✅ Numbers correctly within each ARTICLE_COLOR group ✅ Preserves original file extensions
'''

