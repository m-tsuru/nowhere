import datetime  # noqa: I001
import json
from collections import defaultdict

from sqlalchemy import and_, or_
from sqlalchemy.orm import Session

from .static_models import (
    Calendar,
    CalendarDates,
    Routes,
    Stops,
    StopTimes,
    Trips,
)

stops_ids = [
    "22030 1",
    "22030 2",
    "22030 52",
    "24140 1",
    "24140 2",
]


def get_bus_schedule_flexible(
    session: Session,
    stop_ids: list,
    target_date: str,
    limit: int = 100,
    start_time: str | None = "00:00:00",
    stop_time: str | None = "23:59:59",
) -> dict[str, dict[str, list[dict]]]:
    target_date_str = datetime.datetime.strftime(target_date, "%Y%m%d")
    day_of_week = target_date.strftime("%A").lower()

    # 通常運行サービス
    regular_services = (
        session.query(Calendar.service_id)
        .filter(getattr(Calendar, day_of_week) == "1")
        .filter(
            Calendar.service_id.notin_(
                session.query(CalendarDates.service_id).filter(
                    and_(
                        CalendarDates.date == target_date_str,
                        CalendarDates.exception_type == "2",
                    ),
                ),
            ),
        )
    )

    # 特別運行サービス
    special_services = session.query(CalendarDates.service_id).filter(
        and_(
            CalendarDates.date == target_date_str,
            CalendarDates.exception_type == "1",
        ),
    )

    # メインクエリ
    query = (
        session.query(
            StopTimes.trip_id,
            Trips.route_id,
            Trips.service_id,
            Routes.route_short_name,
            Routes.route_long_name,
            StopTimes.departure_time,
            StopTimes.stop_id,
            StopTimes.stop_headsign,
            Stops.stop_name,
        )
        .join(Trips, StopTimes.trip_id == Trips.trip_id)
        .join(Routes, Trips.route_id == Routes.route_id)
        .join(Stops, StopTimes.stop_id == Stops.stop_id)
        .filter(StopTimes.stop_id.in_(stop_ids))
        .filter(
            or_(
                Trips.service_id.in_(regular_services),
                Trips.service_id.in_(special_services),
            ),
        )
        .order_by(StopTimes.departure_time)
        .filter(StopTimes.departure_time >= start_time)
        .filter(StopTimes.departure_time <= stop_time)
        .limit(limit)
    )

    results = query.all()

    # UUIDでグループ化
    grouped_data = defaultdict(lambda: {"trip_info": {}, "stops": []})

    for result in results:
        trip_id = result[0]  # UUID

        # 便情報（最初のレコードで設定）
        if not grouped_data[trip_id]["trip_info"]:
            grouped_data[trip_id]["trip_info"] = {
                "trip_id": result[0],
                "route_id": result[1],
                "service_id": result[2],
                "route_short_name": result[3],
                "route_long_name": result[4],
            }

        # 停留所情報を追加
        grouped_data[trip_id]["stops"].append(
            {
                "departure_scheduled_time": result[5],
                "stop_id": result[6],
                "stop_name": result[8],
                "stop_headsign": result[7],
            }
        )

    return dict(grouped_data)


if __name__ == "__main__":
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    engine = create_engine("sqlite:///nowhere.db")
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    with SessionLocal() as session:
        results = get_bus_schedule_flexible(
            session=session,
            stop_ids=stops_ids,
            target_date=datetime.datetime(2025, 10, 22),  # noqa: DTZ001
            limit=1000,
            start_time="08:00:00",
            stop_time="09:00:00",
        )
        print(
            json.dumps(
                results,
                ensure_ascii=False,
                indent=4,
            ),
        )
