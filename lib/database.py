import csv
import os
import sqlite3
import zipfile
from pathlib import Path

import dotenv
import requests

insertable: list[str] = [
    "agency",
    # "agency_jp",
    "calendar",
    "calendar_dates",
    # "fare_attributes",
    # "fare_rules",
    "feed_info",
    "routes",
    "routes_jp",
    # "shapes",
    "stop_times",
    "stops",
    "trips",
]


def initialize_database(path: str = "./lib/database.sql") -> None:
    with sqlite3.connect("nowhere.db") as conn:
        cursor = conn.cursor()
        with Path(path).open("r") as f:
            sql_script = f.read()
        cursor.executescript(sql_script)
        conn.commit()


def insert_static() -> None:
    allowed_tables = set(insertable)
    with sqlite3.connect("nowhere.db") as conn:
        cursor = conn.cursor()
        for table in insertable:
            if table not in allowed_tables:
                msg = f"Unexpected table name: {table!r}"
                raise ValueError(msg)
            safe_table = '"' + table.replace('"', '""') + '"'
            with Path(f"static/{table}.txt").open("r") as f:
                csv_reader = csv.reader(f)
                headers = next(csv_reader)
                for row in csv_reader:
                    placeholders = ",".join("?" for _ in row)
                    cursor.execute(
                        f"INSERT INTO {safe_table} ({','.join(headers)}) VALUES ({placeholders})",
                        row,
                    )
        conn.commit()


def download_static_files(url: str, dest_path: str) -> bool:
    try:
        # Download the Files
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Raise an error for HTTP errors
        with Path(dest_path).open("wb") as f:
            f.write(response.content)
        print(f"Downloaded static files to {dest_path}")
        with zipfile.ZipFile(dest_path, "r") as zip_ref:
            zip_ref.extractall("static")
        print("Extracted static files to 'static' directory")
    except Exception as e:
        print(f"Error downloading static files: {e}")


if __name__ == "__main__":
    dotenv.load_dotenv()
    gtfs_static_url = os.getenv("GTFS_STATIC_URL")
    initialize_database()
    download_static_files(gtfs_static_url, "static.zip")
    insert_static()
