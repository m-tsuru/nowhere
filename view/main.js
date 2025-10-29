// APIからバス時刻表データを取得して表示
async function fetchBusSchedule() {
  try {
    const response = await fetch("/api/");

    if (!response.ok) {
      throw new Error(`HTTPエラー: ${response.status}`);
    }

    const data = await response.json();

    if (data.status && data.result) {
      displayBusSchedule(data.result);
      clearErrorMessage();
    } else {
      console.error("APIエラー:", data.message);
      showErrorMessage(
        "データの取得に失敗しました。しばらくしてから再度お試しください。"
      );
    }
  } catch (error) {
    console.error("データ取得エラー:", error);
    showErrorMessage(
      "接続エラーが発生しました。ネットワーク接続を確認してください。"
    );
  }
}

// エラーメッセージを表示
function showErrorMessage(message) {
  const tbody = document.querySelector(".timetable tbody");
  if (!tbody) return;

  tbody.innerHTML = `
        <tr>
            <td colspan="5" style="text-align: center; padding: 40px 20px; color: #e74c3c;">
                <div style="font-size: 18px; margin-bottom: 10px;">⚠️ ${message}</div>
                <div style="font-size: 14px; color: #7f8c8d;">自動で再接続を試みています...</div>
            </td>
        </tr>
    `;
}

// エラーメッセージをクリア
function clearErrorMessage() {
  // 正常なデータが表示されればエラーメッセージは自動的に上書きされる
}

// バス時刻表を表示
function displayBusSchedule(scheduleData) {
  const tbody = document.querySelector(".timetable tbody");
  if (!tbody) return;

  // テーブルをクリア
  tbody.innerHTML = "";

  // 各trip_idのデータを処理して配列に格納
  const tripRows = [];

  for (const [tripId, tripData] of Object.entries(scheduleData)) {
    const tripInfo = tripData.trip_info;
    const stops = tripData.stops || [];

    // 停留所データがない場合はスキップ
    if (stops.length === 0) continue;

    // 沼田料金所前と市立大学前の時刻を取得
    let numataTime = "—";
    let numataTimeRaw = null;
    let numataActualTime = null;
    let numataActualTimeRaw = null;
    let numataDelay = 0;
    let shidaiTime = "—";
    let shidaiActualTime = null;
    let shidaiActualTimeRaw = null;
    let shidaiDelay = 0;
    let destination = "";
    let currentLocation = tripInfo.route_long_name || "情報なし";

    for (const stop of stops) {
      // 沼田料金所前 (24140 1 または 24140 2)
      if (stop.stop_id.startsWith("24140")) {
        numataTime = formatTime(stop.departure_scheduled_time);
        numataTimeRaw = stop.departure_scheduled_time;
        if (stop.actual_departure) {
          numataDelay = calculateDelay(stop);
          if (stop.actual_departure.time) {
            numataActualTime = formatTime(stop.actual_departure.time);
            numataActualTimeRaw = stop.actual_departure.time;
          }
        }
      }
      // 市立大学前 (22030 1 または 22030 2)
      else if (stop.stop_id.startsWith("22030")) {
        shidaiTime = formatTime(stop.departure_scheduled_time);
        if (stop.actual_departure) {
          shidaiDelay = calculateDelay(stop);
          if (stop.actual_departure.time) {
            shidaiActualTime = formatTime(stop.actual_departure.time);
            shidaiActualTimeRaw = stop.actual_departure.time;
          }
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
      numataActualTime,
      numataActualTimeRaw,
      numataDelay,
      shidaiTime,
      shidaiActualTime,
      shidaiActualTimeRaw,
      shidaiDelay,
      routeNumber: tripInfo.route_short_name,
      destination,
      currentLocation,
    });
  }

  // 時刻順にソート（沼田料金所前の時刻で）
  tripRows.sort((a, b) => {
    if (!a.numataTimeRaw) return 1;
    if (!b.numataTimeRaw) return -1;
    return a.numataTimeRaw.localeCompare(b.numataTimeRaw);
  });

  // 上位3件のみ表示
  const topThree = tripRows.slice(0, 5);

  for (const rowData of topThree) {
    const row = createTableRow(
      rowData.numataTime,
      rowData.numataActualTime,
      rowData.numataActualTimeRaw,
      rowData.numataDelay,
      rowData.shidaiTime,
      rowData.shidaiActualTime,
      rowData.shidaiActualTimeRaw,
      rowData.shidaiDelay,
      rowData.routeNumber,
      rowData.destination,
      rowData.currentLocation
    );
    tbody.appendChild(row);
  }

  // 現在時刻を更新
  updateClock();
}

// 時刻をフォーマット (HH:MM)
function formatTime(timeString) {
  if (!timeString) return "—";
  const parts = timeString.split(":");
  return `${parts[0]}:${parts[1]}`;
}

// 遅延を計算（秒単位）
function calculateDelay(stop) {
  if (!stop.actual_departure || !stop.actual_departure.delay) {
    return 0;
  }
  return stop.actual_departure.delay;
}

// 到着予定時間までの残り時間を計算
function calculateTimeUntilArrival(actualTimeString) {
  if (!actualTimeString) return null;

  const now = new Date();
  const [hours, minutes, seconds] = actualTimeString.split(":").map(Number);

  const arrivalTime = new Date();
  arrivalTime.setHours(hours);
  arrivalTime.setMinutes(minutes);
  arrivalTime.setSeconds(seconds || 0);

  // 翌日の時刻の場合（24時を超える場合）
  if (hours >= 24) {
    arrivalTime.setDate(arrivalTime.getDate() + 1);
    arrivalTime.setHours(hours - 24);
  }

  const diffMs = arrivalTime - now;
  const diffMinutes = Math.floor(diffMs / 1000 / 60);

  return diffMinutes;
}

// 残り時間をフォーマット
function formatTimeUntilArrival(minutesUntil) {
  if (minutesUntil === null || minutesUntil < 0) {
    return "";
  }

  if (minutesUntil <= 1) {
    return '<span class="red">まもなく</span>';
  } else {
    return `<span>あと${minutesUntil}分</span>`;
  }
}

// テーブル行を作成
function createTableRow(
  numataTime,
  numataActualTime,
  numataActualTimeRaw,
  numataDelay,
  shidaiTime,
  shidaiActualTime,
  shidaiActualTimeRaw,
  shidaiDelay,
  routeNumber,
  destination,
  currentLocation
) {
  const row = document.createElement("tr");

  // 沼田料金所前の時刻表示（遅延がある場合は予想時刻も表示）
  let numataDisplay = numataTime;
  if (numataActualTime && numataDelay !== 0) {
    numataDisplay = `<span style="text-decoration: line-through; color: #999;">${numataTime}</span> <span style="color: #e74c3c; font-weight: bold;">${numataActualTime}</span>`;
  }

  // 市立大学前の時刻表示（遅延がある場合は予想時刻も表示）
  let shidaiDisplay = shidaiTime;
  if (shidaiActualTime && shidaiDelay !== 0) {
    shidaiDisplay = `<span style="text-decoration: line-through; color: #999;">${shidaiTime}</span> <span style="color: #e74c3c; font-weight: bold;">${shidaiActualTime}</span>`;
  }

  // 到着予定時間までの残り時間を計算（沼田料金所前を優先、なければ市立大学前）
  let timeUntilArrival = "";
  if (numataActualTimeRaw) {
    const minutes = calculateTimeUntilArrival(numataActualTimeRaw);
    timeUntilArrival = formatTimeUntilArrival(minutes);
  } else if (shidaiActualTimeRaw) {
    const minutes = calculateTimeUntilArrival(shidaiActualTimeRaw);
    timeUntilArrival = formatTimeUntilArrival(minutes);
  }

  row.innerHTML = `
        <td>${numataDisplay}</td>
        <td>${shidaiDisplay}</td>
        <td>${routeNumber}</td>
        <td class="content">
            <span>${destination}</span>
            <span>${currentLocation}</span>
        </td>
        <td>${timeUntilArrival}</td>
    `;

  return row;
}

// 現在時刻を更新
function updateClock() {
  const clockElement = document.querySelector(".status-clock span");
  if (!clockElement) return;

  const now = new Date();
  const hours = String(now.getHours()).padStart(2, "0");
  const minutes = String(now.getMinutes()).padStart(2, "0");
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

  // status-text を定期的に更新
  reloadTextile();
  setInterval(reloadTextile, 60000); // 60秒ごとに更新
}

// status-text.json からテキストを取得して更新
async function reloadTextile() {
  try {
    const response = await fetch("./view/status-text.json");

    if (!response.ok) {
      throw new Error(`HTTPエラー: ${response.status}`);
    }

    const texts = await response.json();

    if (Array.isArray(texts) && texts.length > 0) {
      const statusTextElement = document.querySelector(".status-text p");
      if (statusTextElement) {
        // 配列からランダムにテキストを選択
        const randomText = texts[Math.floor(Math.random() * texts.length)];
        statusTextElement.textContent = randomText;
      }
    }
  } catch (error) {
    console.error("status-text取得エラー:", error);
  }
}

// ページ読み込み時に開始
document.addEventListener("DOMContentLoaded", () => {
  startAutoRefresh(30); // 30秒ごとに更新
});
