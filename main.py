import dotenv
import os
import datetime

from lib.dynamic import (
    download_dynamic_files,
    parse_gtfs_realtime,
)
from lib.static import get_bus_schedule_flexible
from lib.merger import merge_gtfs_realtime

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()

dotenv.load_dotenv()
GTFS_DYNAMIC_URL = os.getenv("GTFS_DYNAMIC_URL")


@app.get("/api/")
async def api():
    try:
        eng = create_engine("sqlite:///nowhere.db")
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=eng)
        download_dynamic_files(
            GTFS_DYNAMIC_URL,
            "trip_updates.bin",
        )
        with SessionLocal() as session:
            dynamic_data = parse_gtfs_realtime("trip_updates.bin")
            static_data = get_bus_schedule_flexible(
                session,
                stop_ids=[
                    "22030 1",
                    "22030 2",
                    "22030 52",
                    "24140 1",
                    "24140 2",
                ],
                target_date=datetime.datetime(2025, 10, 22),  # noqa: DTZ001
                start_time="21:15:00",
                stop_time="22:00:00",
                limit=50,
            )
            merged_result = merge_gtfs_realtime(
                static_data,
                dynamic_data,
            )
            return {
                "status": True,
                "message": "Success",
                "result": merged_result,
            }
    except Exception as e:
        return {
            "status": False,
            "message": str(e),
            "result": {},
        }


@app.get("/")
async def root():
    return RedirectResponse("/view")


app.mount("/view", StaticFiles(directory="view", html=True), name="static")
