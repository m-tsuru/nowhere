SELECT
    stop_times.trip_id,
    trips.route_id,
    trips.service_id,
    routes.route_short_name,
    routes.route_long_name,
    departure_time,
    stop_id,
    stop_headsign
FROM
    stop_times
    INNER JOIN
        trips
    ON  stop_times.trip_id = trips.trip_id
    INNER JOIN
        routes
    ON  trips.route_id = routes.route_id
WHERE
    (
    -- 22030 広島市立大学前
        stop_id = '22030 1'
    OR  stop_id = '22030 2'
    OR  stop_id = '22030 52'
    -- 24140 沼田料金所前
    --  OR  stop_id = '24140 1'
    --  OR  stop_id = '24140 2'
    )
AND (
        (trips.service_id IN(
                SELECT
                    service_id
                FROM
                    calendar
                WHERE
                    calendar.saturday = '1'
                AND service_id NOT IN (
                        SELECT
                            service_id
                        FROM
                            calendar_dates
                        WHERE
                            date = '20250405'
                        AND exception_type = 2
                    )
            ))
    OR  (trips.service_id IN(
                SELECT
                    service_id
                FROM
                    calendar_dates
                WHERE
                    date = '20250405'
                AND exception_type = 1
            ))
    )
LIMIT 1000
