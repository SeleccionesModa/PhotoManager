import sqlite3
import os
from datetime import datetime

DATABASE_PATH = "./PhotoSearcher/photos.db"
PHOTO_DIRECTORY = "T:/Imatges Concrete"

def update_database():
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    for photo in os.listdir(PHOTO_DIRECTORY):
        filepath = os.path.join(PHOTO_DIRECTORY, photo)
        upload_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("""
            INSERT OR IGNORE INTO images (filename, filepath, upload_date)
            VALUES (?, ?, ?)
        """, (photo, filepath, upload_date))
    
    conn.commit()
    conn.close()
    print("Database updated!")

update_database()
