// APIからバス時刻表データを取得して表示
async function fetchBusSchedule() {
    try {
        const response = await fetch('/api');
        const data = await response.json();

        if (data.status && data.result) {
            displayBusSchedule(data.result);
        } else {
            console.error('APIエラー:', data.message);
        }
    } catch (error) {
        console.error('データ取得エラー:', error);
    }
}

// バス時刻表を表示
function displayBusSchedule(scheduleData) {
    const tbody = document.querySelector('.timetable tbody');
    if (!tbody) return;

    // テーブルをクリア
    tbody.innerHTML = '';

    // 各trip_idのデータを処理して配列に格納
    const tripRows = [];

    for (const [tripId, tripData] of Object.entries(scheduleData)) {
        const tripInfo = tripData.trip_info;
        const stops = tripData.stops || [];

        // 停留所データがない場合はスキップ
        if (stops.length === 0) continue;

        // 沼田料金所前と市立大学前の時刻を取得
        let numataTime = '—';
        let numataTimeRaw = null;
        let shidaiTime = '—';
        let destination = '';
        let currentLocation = '情報なし';
        let delayInfo = '';

        for (const stop of stops) {
            // 沼田料金所前 (24140 1 または 24140 2)
            if (stop.stop_id.startsWith('24140')) {
                numataTime = formatTime(stop.departure_scheduled_time);
                numataTimeRaw = stop.departure_scheduled_time;
                if (stop.actual_departure) {
                    const delay = calculateDelay(stop);
                    delayInfo = formatDelay(delay);
                    currentLocation = `${stop.stop_name} を通過`;
                }
            }
            // 市立大学前 (22030 1 または 22030 2)
            else if (stop.stop_id.startsWith('22030')) {
                shidaiTime = formatTime(stop.departure_scheduled_time);
                if (stop.actual_departure) {
                    const delay = calculateDelay(stop);
                    if (!delayInfo) {
                        delayInfo = formatDelay(delay);
                    }
                    currentLocation = `${stop.stop_name} を通過`;
                }
            }

            // 行先を取得
            if (stop.stop_headsign) {
                destination = stop.stop_headsign;
            }
        }

        // テーブル行データを配列に追加
        tripRows.push({
            numataTime,
            numataTimeRaw,
            shidaiTime,
            routeNumber: tripInfo.route_short_name,
            destination,
            currentLocation,
            delayInfo
        });
    }

    // 時刻順にソート（沼田料金所前の時刻で）
    tripRows.sort((a, b) => {
        if (!a.numataTimeRaw) return 1;
        if (!b.numataTimeRaw) return -1;
        return a.numataTimeRaw.localeCompare(b.numataTimeRaw);
    });

    // 上位3件のみ表示
    const topThree = tripRows.slice(0, 3);

    for (const rowData of topThree) {
        const row = createTableRow(
            rowData.numataTime,
            rowData.shidaiTime,
            rowData.routeNumber,
            rowData.destination,
            rowData.currentLocation,
            rowData.delayInfo
        );
        tbody.appendChild(row);
    }

    // 現在時刻を更新
    updateClock();
}

// 時刻をフォーマット (HH:MM)
function formatTime(timeString) {
    if (!timeString) return '—';
    const parts = timeString.split(':');
    return `${parts[0]}:${parts[1]}`;
}

// 遅延を計算（秒単位）
function calculateDelay(stop) {
    if (!stop.actual_departure || !stop.actual_departure.delay) {
        return 0;
    }
    return stop.actual_departure.delay;
}

// 遅延情報をフォーマット
function formatDelay(delaySeconds) {
    if (delaySeconds === 0) {
        return '';
    }

    const delayMinutes = Math.floor(delaySeconds / 60);

    if (delayMinutes < 1) {
        return '<span class="red">まもなく</span>';
    } else if (delayMinutes < 3) {
        return `${delayMinutes}分`;
    } else {
        return `${delayMinutes}分遅れ`;
    }
}

// テーブル行を作成
function createTableRow(numataTime, shidaiTime, routeNumber, destination, currentLocation, delayInfo) {
    const row = document.createElement('tr');

    row.innerHTML = `
        <td>${numataTime}</td>
        <td>${shidaiTime}</td>
        <td>${routeNumber}</td>
        <td class="content">
            <span>${destination}</span>
            <span>${currentLocation}</span>
        </td>
        <td>${delayInfo}</td>
    `;

    return row;
}

// 現在時刻を更新
function updateClock() {
    const clockElement = document.querySelector('.status-clock span');
    if (!clockElement) return;

    const now = new Date();
    const hours = String(now.getHours()).padStart(2, '0');
    const minutes = String(now.getMinutes()).padStart(2, '0');
    clockElement.textContent = `${hours}:${minutes}`;
}

// 定期的にデータを更新
function startAutoRefresh(intervalSeconds = 30) {
    // 初回実行
    fetchBusSchedule();

    // 定期実行
    setInterval(() => {
        fetchBusSchedule();
    }, intervalSeconds * 1000);

    // 時計を毎秒更新
    setInterval(updateClock, 1000);
}

// ページ読み込み時に開始
document.addEventListener('DOMContentLoaded', () => {
    startAutoRefresh(30); // 30秒ごとに更新
});
