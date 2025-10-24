import datetime
import json
import os
from copy import deepcopy

from dotenv import load_dotenv
from .dynamic import download_dynamic_files, parse_gtfs_realtime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from .static import get_bus_schedule_flexible

eng = create_engine("sqlite:///nowhere.db")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)

stops_ids = [
    "22030 1",
    "22030 2",
    "22030 52",
    "24140 1",
    "24140 2",
]


def merge_gtfs_realtime(static_data: dict, dynamic_data: dict) -> dict:
    """
    静的な GTFS データにリアルタイムの TripUpdate 情報を結合する関数。

    Args:
        static_data: 静的時刻表情報を含む辞書。キーは trip_id。
        dynamic_data: GTFS-Realtime の TripUpdate を含む辞書。

    Returns:
        リアルタイム情報が統合された新しい辞書。
    """

    # static データを変更しないようにディープコピーを作成
    merged_data = deepcopy(static_data)

    # dynamic_data から entity リストを取得
    if "entity" not in dynamic_data:
        # entity がない場合は静的データをそのまま返す
        return merged_data

    static_keys = list(static_data.keys())

    for i in dynamic_data["entity"]:
        reading_static_key = i["trip_update"]["trip"]["trip_id"]
        if reading_static_key in static_keys:
            # 該当する静的データのtrip情報を取得
            trip_data = merged_data[reading_static_key]

            # stop_time_update を取得
            stop_time_updates = i["trip_update"].get("stop_time_update", [])

            # stop_time_update を stop_id でインデックス化
            realtime_stops = {}
            for stop_update in stop_time_updates:
                stop_id = stop_update.get("stop_id")
                if stop_id:
                    realtime_stops[stop_id] = stop_update

            # 静的データの stops に対してリアルタイム情報を差し込む
            for stop in trip_data.get("stops", []):
                stop_id = stop.get("stop_id")
                if stop_id in realtime_stops:
                    realtime_info = realtime_stops[stop_id]

                    # departure 情報を追加
                    if "departure" in realtime_info:
                        stop["actual_departure"] = realtime_info["departure"]
                        if "time" in realtime_info["departure"]:
                            stop["actual_departure"]["time"] = (
                                datetime.datetime.strftime(
                                    datetime.datetime.fromtimestamp(
                                        int(realtime_info["departure"]["time"]),
                                    ),
                                    "%H:%M:%S",
                                )
                            )

                    # arrival 情報を追加
                    if "arrival" in realtime_info:
                        stop["realtime_arrival"] = realtime_info["arrival"]
                        if "time" in realtime_info["arrival"]:
                            stop["realtime_arrival"]["time"] = (
                                datetime.datetime.strftime(
                                    datetime.datetime.fromtimestamp(
                                        int(realtime_info["arrival"]["time"]),
                                    ),
                                    "%H:%M:%S",
                                )
                            )

                    # stop_sequence と schedule_relationship を追加
                    if "stop_sequence" in realtime_info:
                        stop["stop_sequence"] = realtime_info["stop_sequence"]
                    if "schedule_relationship" in realtime_info:
                        stop["schedule_relationship"] = realtime_info[
                            "schedule_relationship"
                        ]

    return merged_data


if __name__ == "__main__":
    load_dotenv()
    GTFS_DYNAMIC_URL = os.getenv("GTFS_DYNAMIC_URL")
    download_dynamic_files(
        GTFS_DYNAMIC_URL,
        "trip_updates.bin",
    )
    with SessionLocal() as session:
        st = get_bus_schedule_flexible(
            session,
            stop_ids=stops_ids,
            target_date=datetime.datetime(2025, 10, 24),
            start_time="22:00:00",
            stop_time="23:00:00",
        )
        re = parse_gtfs_realtime("trip_updates.bin")
        merged = merge_gtfs_realtime(st, re)
        print(json.dumps(merged, ensure_ascii=False, indent=4))
