import os
import tkinter 
from tkinter import ttk
from tkinter.filedialog import askdirectory
import pandas as pd
import shutil 

# Load the Excel file
file_path = "./CornerDigitalExample.xlsx"  # Update this with the actual file path
df = pd.read_excel(file_path)

# Extract column E values and replace '-' with '_'
codes_array = df.iloc[:, 4].astype(str).str.replace("-", "_").tolist()  # Column E is index 4 (zero-based)

# Extract the names of the photos
photo_directory = "./fototest"
codesPhotos_array = [entry for entry in os.listdir(photo_directory)]  # List comprehension for cleaner code

#check which photos exist in directory:

matches = [code for code in codes_array if any(code in photo for photo in codesPhotos_array)]

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

from collections import defaultdict

# Define source and destination directories
photo_directory = "./fototest"
destination_directory = "./foundPhotos"

# Ensure the destination directory exists
os.makedirs(destination_directory, exist_ok=True)

# Define the priority order
priority_order = ["MOD", "ED", "FLATFRONT", "FLATBACK"]

# Dictionary to track numbering for each ARTICLE_COLOR
article_counters = defaultdict(int)

# Function to extract ARTICLE_COLOR and suffix from filename
def extract_article_color(photo_name):
    parts = photo_name.split("_")
    if len(parts) >= 5:
        article_color = "_".join(parts[:2])  # First two parts form ARTICLE_COLOR
        suffix = os.path.splitext(parts[4])[0]  # Remove file extensions (e.g., "jpg")
        # Ensure the suffix matches priority_order
        cleaned_suffix = next((order for order in priority_order if order in suffix), suffix)
        return article_color, cleaned_suffix
    return None, None


# Collect and sort photos by priority
sorted_photos = []
for photo in codesPhotos_array:
    article_color, suffix = extract_article_color(photo)
    if article_color and suffix:
        sorted_photos.append((article_color, suffix, photo))

# Step 1: Group by ARTICLE_COLOR
photos_by_color = defaultdict(list)
for article_color, suffix, photo in sorted_photos:
    photos_by_color[article_color].append((suffix, photo))

# Step 2: Sort within each ARTICLE_COLOR group by priority
for article_color, photos in photos_by_color.items():
    photos.sort(key=lambda x: (priority_order.index(x[0]) if x[0] in priority_order else float('inf')))
    article_counters[article_color] = 0  # Reset numbering for each group
    
    # Rename and copy files
    for suffix, photo in photos:
        article_counters[article_color] += 1
        new_filename = f"{article_color}_{article_counters[article_color]}{os.path.splitext(photo)[-1]}"
        source_path = os.path.join(photo_directory, photo)
        destination_path = os.path.join(destination_directory, new_filename)
        shutil.copy(source_path, destination_path)

print(f"Matching photos copied and renamed in '{destination_directory}' with correct ordering!")


