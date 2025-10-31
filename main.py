import dotenv
import os
import sys
import datetime

from lib.dynamic import (
    download_dynamic_files,
    parse_gtfs_realtime,
)
from lib.static import get_bus_schedule_flexible
from lib.merger import merge_gtfs_realtime
from lib.database import (
    initialize_database,
    download_static_files,
    insert_static,
)

from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

app = FastAPI()

dotenv.load_dotenv()
GTFS_DYNAMIC_URL = os.getenv("GTFS_DYNAMIC_URL")
GTFS_STATIC_URL = os.getenv("GTFS_STATIC_URL")

global is_ready
is_ready = False

try:
    print("Downloading Static Information and Initializing Database...")
    initialize_database()
    download_static_files(GTFS_STATIC_URL, "static.zip")
    insert_static()
    is_ready = True
except Exception as e:
    print(f"Error during initialization: {e}")
    sys.exit(1)


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
                target_date=datetime.datetime.today(),  # noqa: DTZ001
                start_time=datetime.datetime.strftime(
                    datetime.datetime.now(), "%H:%M:%S"
                ),
                stop_time=datetime.datetime.strftime(
                    datetime.datetime.now() + datetime.timedelta(minutes=60), "%H:%M:%S"
                ),
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


@app.get("/api/health", status_code=status.HTTP_200_OK)
async def health_check():
    """
    Readiness Probe/Liveness Probe 用のヘルスチェックエンドポイント。
    is_ready が False の場合は HTTP 503 を返す。
    """
    if not is_ready:
        # HTTP 503 Service Unavailable を返すことで、
        # ホスト（ロードバランサーやK8sなど）に「まだ準備ができていない」と伝える
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service is starting up. Please wait.",
        )
    # is_ready が True の場合は HTTP 200 OK を返す
    return {"status": "ok", "message": "Service is ready to handle requests."}


@app.get("/")
async def root():
    return RedirectResponse("/view")


app.mount("/view", StaticFiles(directory="view", html=True), name="static")
