import os
import shutil
import pandas as pd
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict
from tkinter import Tk, filedialog

def b2b():
    # Load Excel data
    file_path = "./B2BExample.xlsx"
    df = pd.read_excel(file_path)

    codes_array = df.iloc[:, 28].dropna().astype(str).str.strip().tolist()
    unique_codes = list(set(codes_array))
    codes_array = [code[:len(code)-3] + "_" + code[len(code)-3:] for code in unique_codes]

    print("Extracted codes:", codes_array)

    # Extract the names of the photos
    photo_directory = "T:/Imatges Concrete"
    destination_directory = "./foundPhotos"

    # Ensure the destination folder exists
    os.makedirs(destination_directory, exist_ok=True)

    codesPhotos_array = [entry for entry in os.listdir(photo_directory)]  # Cached for fast lookup

    # Check which photos exist in the directory
    matches = [code for code in codes_array if any(code in photo for photo in codesPhotos_array)]
    print("Matches found:", matches)

    # Find missing codes
    missing_codes = [code for code in codes_array if not any(code in photo for photo in codesPhotos_array)]
    print("Missing codes:", missing_codes)

    # Ask user if they want to download missing articles
    if missing_codes:
        user_choice = input("Do you want to download missing articles? (y/n): ").strip().lower()
        if user_choice == "y":
            missing_df = pd.DataFrame({"Missing Articles": missing_codes}).drop_duplicates()
            missing_df.to_excel("missing_articles.xlsx", index=False)
            print("Missing articles saved as 'missing_articles.xlsx'.")
        else:
            print("No file downloaded.")
    else:
        print("No missing codes detected.")

    # Define suffix priority
    priority_order = ["ED1", "FLATFRONT", "FLATBACK"]

    # Track numbering for each ARTICLE_COLOR
    article_counters = defaultdict(int)

    # Function to extract ARTICLE_COLOR and suffix
    def extract_article_color(photo_name):
        parts = photo_name.split("_")
        if len(parts) >= 5:
            article_color = "_".join(parts[:2])  # First two parts form ARTICLE_COLOR
            suffix = os.path.splitext(parts[4])[0]  # Remove file extension
            cleaned_suffix = next((order for order in priority_order if order in suffix), suffix)
            return article_color, cleaned_suffix
        return None, None

    # Collect and sort photos
    sorted_photos = []
    for photo in codesPhotos_array:
        article_color, suffix = extract_article_color(photo)
        if article_color and suffix and article_color in matches:
            sorted_photos.append((article_color, suffix, photo))

    # Step 1: Group by ARTICLE_COLOR
    photos_by_color = defaultdict(list)
    for article_color, suffix, photo in sorted_photos:
        photos_by_color[article_color].append((suffix, photo))

    # Step 2: Filter necessary photos
    copy_tasks = []
    for article_color, photos in photos_by_color.items():
        filtered_photos = [(suffix, photo) for suffix, photo in photos if suffix in priority_order or "FLAT" in suffix or "FLATED" in suffix]
        
        if not filtered_photos:
            continue  # Skip processing if no valid photos

        # Sort by priority
        filtered_photos.sort(key=lambda x: (priority_order.index(x[0]) if x[0] in priority_order else float('inf')))
        article_counters[article_color] = 0  # Reset numbering

        # Prepare copy tasks for multithreading
        for suffix, photo in filtered_photos:
            article_counters[article_color] += 1
            articlecolor = article_color.replace("_", "")  
            new_filename = f"{articlecolor}-{article_counters[article_color]}{os.path.splitext(photo)[-1]}"

            source_path = os.path.join(photo_directory, photo)
            destination_path = os.path.join(destination_directory, new_filename)

            if os.path.exists(source_path):  # Ensure file exists before copying
                copy_tasks.append((source_path, destination_path))

    # Step 3: Optimize File Copying with Buffered Reads & Multithreading
    def copy_file(src, dst):
        shutil.copy(src, dst)

    with ThreadPoolExecutor(max_workers=8) as executor:
        executor.map(lambda task: copy_file(*task), copy_tasks)

    print(f"✅ Optimized copying complete for {len(copy_tasks)} photos!")

def corner():
    # Load the Excel file
    file_path = "./CornerDigitalExample.xlsx"  # Update this with the actual file path
    df = pd.read_excel(file_path)

    # Extract column E values and replace '-' with '_'
    codes_array = df.iloc[:, 4].astype(str).str.replace("-", "_").tolist()  # Column E is index 4 (zero-based)

    # Extract the names of the photos
    photo_directory = "T:/Imatges Concrete"
    codesPhotos_array = [entry for entry in os.listdir(photo_directory)]  # List comprehension for cleaner code
    print(codesPhotos_array)
    #check which photos exist in directory:

    matches = [code for code in codes_array if any(code in photo for photo in codesPhotos_array)]
    print("matches: ", matches)
    # Find missing codes (not found in any photo filenames)
    missing_codes = [code for code in codes_array if not any(code in photo for photo in codesPhotos_array)]
    print("missing codes: ", missing_codes)

    # Ask user if they want to download missing articles
    user_choice = input("Do you want to download missing articles? (y/n): ").strip().lower()

    if user_choice == "y":
        missing_df = pd.DataFrame({"Missing Articles": missing_codes}).drop_duplicates()
        missing_df.to_excel("missing_articles.xlsx", index=False, )
        print("Missing articles saved as 'missing_articles.xlsx'.")
    else:
        print("No file downloaded.")

    # Define source and destination directories
    # photo_directory = "./fototest"
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
        if article_color and suffix and article_color in matches:
            sorted_photos.append((article_color, suffix, photo))

    # Step 1: Group by ARTICLE_COLOR
    photos_by_color = defaultdict(list)
    for article_color, suffix, photo in sorted_photos:
        photos_by_color[article_color].append((suffix, photo))

    copy_tasks = []
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
            if os.path.exists(source_path):
                copy_tasks.append((source_path, destination_path))
        
        def copy_file(src_dst):
            src, dst = src_dst
            shutil.copy(src, dst)

        with ThreadPoolExecutor(max_workers=8) as executor:
            executor.map(copy_file, copy_tasks)

    print(f"Matching photos copied and renamed in '{destination_directory}' with correct ordering!")

print("Select file type: \n 1 - Corner digital \n 2 - B2B")

options = {
    "1": corner,
    "2": b2b
}

excel_type = input("Enter your choice: ").strip()

if excel_type in options:
    options[excel_type]()  # Calls the corresponding function
else:
    print("Not a valid option. Please enter 1 or 2.")

