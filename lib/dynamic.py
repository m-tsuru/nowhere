import json
import os
from pathlib import Path
import requests

import dotenv
from google.protobuf.json_format import MessageToDict
from google.transit import gtfs_realtime_pb2


def download_dynamic_files(url: str, dest_path: str) -> str | None:
    # Download the Files
    response = requests.get(url, timeout=10)
    response.raise_for_status()  # Raise an error for HTTP errors
    with Path(dest_path).open("wb") as f:
        f.write(response.content)
    return dest_path


def parse_gtfs_realtime(trip_updates_path: str) -> dict:
    feed = gtfs_realtime_pb2.FeedMessage()
    with Path(trip_updates_path).open("rb") as response:
        feed.ParseFromString(response.read())
        res = MessageToDict(feed, preserving_proto_field_name=True)
    return res


if __name__ == "__main__":
    dotenv.load_dotenv()
    gtfs_dynamic_url = os.getenv("GTFS_DYNAMIC_URL")
    download_dynamic_files(
        gtfs_dynamic_url,
        "trip_updates.bin",
    )
    result = parse_gtfs_realtime("trip_updates.bin")
    print(json.dumps(result, ensure_ascii=False, indent=4))
