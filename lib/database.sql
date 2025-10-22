--
-- GTFS Relational Database Schema
-- Original: https://github.com/ValLaboratory/advcal/blob/master/2019/gw/docker_env/docker/gtfs_db/script/gtfs_reference.sql
-- License: MIT License
-- (C) 2019 ValLaboratory, valsitoh
--
-- MODIFY: Adapt to SQlite
-- (C) 2025 Michiru Tsurumaru
--

PRAGMA foreign_keys = OFF;

-- テーブルの削除
DROP TABLE IF EXISTS fare_rules ;
DROP TABLE IF EXISTS trips ;
DROP TABLE IF EXISTS routes_jp ;
DROP TABLE IF EXISTS routes ;
DROP TABLE IF EXISTS agency_jp ;
DROP TABLE IF EXISTS agency ;
DROP TABLE IF EXISTS calendar_dates ;
DROP TABLE IF EXISTS calendar ;
DROP TABLE IF EXISTS fare_attributes ;
DROP TABLE IF EXISTS feed_info ;
DROP TABLE IF EXISTS frequencies ;
DROP TABLE IF EXISTS office_jp ;
DROP TABLE IF EXISTS shapes ;
DROP TABLE IF EXISTS stop_times ;
DROP TABLE IF EXISTS stops ;
DROP TABLE IF EXISTS transfers ;
DROP TABLE IF EXISTS translations ;

PRAGMA foreign_keys = ON;

-- 事業者情報
CREATE TABLE agency (
	agency_id	VARCHAR(64) PRIMARY KEY,	-- 事業者ID
	agency_name	TEXT NOT NULL,			-- 事業者名称
	agency_url	TEXT NOT NULL,			-- 事業者URL
	agency_timezone	VARCHAR(32) NOT NULL,		-- タイムゾーン(Asia/Tokyo固定)
	agency_lang	VARCHAR(32) NOT NULL,		-- 言語(日本の場合は"ja"を設定)
	agency_phone	VARCHAR(32),			-- 電話番号
	agency_fare_url	TEXT,				-- オンライン購入URL
	agency_email	TEXT				-- 事業者Eメール
);

-- 事業者情報(GTFS-JP)
CREATE TABLE agency_jp (
	agency_id		VARCHAR(64) PRIMARY KEY,	-- 事業者ID
	agency_official_name	TEXT,				-- 事業者正式名称
	agency_zip_number	VARCHAR(32),			-- 事業者郵便番号
	agency_address		TEXT,				-- 事業者住所
	agency_president_pos	TEXT,				-- 代表者肩書
	agency_president_name	TEXT,			-- 代表者氏名
	FOREIGN KEY (agency_id)
	REFERENCES agency (agency_id)
);

-- 経路情報
CREATE TABLE routes (
	route_id		VARCHAR(64) PRIMARY KEY,	-- 経路ID
	agency_id		VARCHAR(64) NOT NULL,		-- 事業者ID
	route_short_name	VARCHAR(64),			-- 経路略称
	route_long_name		TEXT,				-- 経路名
	route_desc		TEXT,				-- 経路情報
	route_type		VARCHAR(32) NOT NULL,		-- 経路タイプ(バス事業者は「3」固定)
	route_url		TEXT,				-- 経路URL
	route_color		VARCHAR(8),			-- 経路色
	route_text_color	VARCHAR(8),			-- 経路文字色
	-- jp_parent_route_id	VARCHAR(64),		-- 路線ID
	FOREIGN KEY (agency_id)
	REFERENCES agency (agency_id)
);

-- 経路情報(GTFS-JP)
CREATE TABLE routes_jp (
	route_id		VARCHAR(64),	-- 経路ID
	route_update_date	VARCHAR(32),	-- ダイヤ改正日
	origin_stop		TEXT,		-- 起点
	via_stop		TEXT,		-- 経過地
	destination_stop	TEXT,		-- 終点
	jp_parent_route_id TEXT,
	FOREIGN KEY (route_id)
	REFERENCES routes (route_id)
);

-- 運行区分情報
CREATE TABLE calendar (
	service_id	VARCHAR(64) PRIMARY KEY,	-- 運行日ID
	monday		VARCHAR(2),			-- 月曜日
	tuesday		VARCHAR(2),			-- 火曜日
	wednesday	VARCHAR(2),			-- 水曜日
	thursday	VARCHAR(2),			-- 木曜日
	friday		VARCHAR(2),			-- 金曜日
	saturday	VARCHAR(2),			-- 土曜日
	sunday		VARCHAR(2),			-- 日曜日
	start_date	VARCHAR(16),			-- サービス開始日
	end_date	VARCHAR(16)			-- サービス終了日
);

-- 運行日情報
CREATE TABLE calendar_dates (
	service_id	VARCHAR(64),	-- サービスID
	date		VARCHAR(16),	-- 日付
	exception_type	VARCHAR(2)	-- 利用タイプ
);

-- 便情報
CREATE TABLE trips (
	trip_id			VARCHAR(64) PRIMARY KEY,	-- 便ID
	route_id		VARCHAR(64),			-- 経路ID
	service_id		VARCHAR(64),			-- 運行日ID
	trip_headsign		TEXT,				-- 便行先
	trip_short_name		TEXT,				-- 便名称
	direction_id		VARCHAR(2),			-- 上下区分
	block_id		TEXT,				-- 便結合区分
	shape_id		VARCHAR(64),			-- 描画ID
	wheelchair_accessible	VARCHAR(2),			-- 車いす利用区分
	bikes_allowed		VARCHAR(2),			-- 自転車持込区分
	jp_trip_desc		TEXT,				-- 便情報
	jp_trip_desc_symbol	TEXT,				-- 便記号
	jp_office_id		VARCHAR(64),			-- 営業所ID
	FOREIGN KEY (route_id)
	REFERENCES routes (route_id)
	FOREIGN KEY (service_id)
	REFERENCES calendar (service_id)
	FOREIGN KEY (jp_office_id)
	REFERENCES office_jp (office_id)
	FOREIGN KEY (shape_id)
	REFERENCES shapes (shape_id)
);

-- 営業所情報
CREATE TABLE office_jp (
	office_id	VARCHAR(64) PRIMARY KEY,	-- 営業所ID
	office_name	TEXT,				-- 営業所名
	office_url	TEXT,				-- 営業所URL
	office_phone	VARCHAR(32)			-- 営業所電話番号
);

-- 運行間隔情報
CREATE TABLE frequencies (
	trip_id		VARCHAR(64),	-- 便ID
	start_time	VARCHAR(12),	-- 開始時刻(HH:MM:SS形式)
	end_time	VARCHAR(12),	-- 開始時刻(HH:MM:SS形式)
	headway_secs	INT,		-- 運行間隔(秒)
	exact_times	INT,		-- 案内精度
	FOREIGN KEY (trip_id)
	REFERENCES trips (trip_id)
);

-- 通過時刻情報
CREATE TABLE stop_times (
	trip_id			VARCHAR(64),	-- 便ID
	arrival_time		VARCHAR(12),	-- 到着時刻(HH:MM:SS形式)
	departure_time		VARCHAR(12),	-- 出発時刻(HH:MM:SS形式)
	stop_id			VARCHAR(64),	-- 標柱ID
	stop_sequence		INT,		-- 通過順位
	stop_headsign		TEXT,		-- 停留所行先
	pickup_type		VARCHAR(2),	-- 乗車区分
	drop_off_type		VARCHAR(2),	-- 降車区分
	shape_dist_traveled	INT,		-- 通算距離(単位はメートル(m))
	timepoint		INT,	-- 発着時間精度(日本では使用しない)
	FOREIGN KEY (stop_id)
	REFERENCES stops (stop_id)
);

-- 停留所・標柱情報
CREATE TABLE stops (
	stop_id			VARCHAR(64) PRIMARY KEY,	-- 停留所・標柱ID
	stop_code		VARCHAR(64),			-- 停留所・標柱番号
	stop_name		TEXT,				-- 停留所・標柱名称
	stop_desc		TEXT,				-- 停留所・標柱付加情報
	stop_lat		VARCHAR(16),			-- 緯度
	stop_lon		VARCHAR(16),			-- 経度
	zone_id			VARCHAR(64),			-- 運賃エリアID
	stop_url		TEXT,				-- 停留所・標柱URL
	location_type		VARCHAR(2),			-- 停留所・標柱区分(0:標柱, 1:停留所)
	parent_station		VARCHAR(64),			-- 親駅情報
	stop_timezone		VARCHAR(32),			-- タイムゾーン(日本は設定しない)
	wheelchair_boarding	VARCHAR(2),			-- 車椅子情報(日本は設定しない)
	platform_code		TEXT				-- のりば情報
);


-- 乗換情報
CREATE TABLE transfers (
	from_stop_id		VARCHAR(64),	-- 乗継元標柱ID
	to_stop_id		VARCHAR(64),	-- 乗継先標柱ID
	transfer_type		VARCHAR(2),	-- 乗継ぎタイプ
	min_transfer_type	INT UNSIGNED	-- 乗継時間
);

-- 運賃属性情報
CREATE TABLE fare_attributes (
	fare_id			VARCHAR(64) PRIMARY KEY,	-- 運賃ID
	price			INT UNSIGNED,			-- 運賃
	currency_type		VARCHAR(16),			-- 通貨
	payment_method		VARCHAR(2),			-- 支払いタイミング
	transfers		VARCHAR(2),			-- 乗換
	transfer_duration	INT UNSIGNED,			-- 乗換有効期限(秒)
	agency_id		VARCHAR(64),			-- 事業者ID
	FOREIGN KEY (agency_id)
	REFERENCES agency (agency_id)
);

-- 運賃定義情報
CREATE TABLE fare_rules (
	fare_id		VARCHAR(64),	-- 運賃ID
	route_id	VARCHAR(64),			-- 経路ID
	origin_id	VARCHAR(64),			-- 乗車地ゾーン
	destination_id	VARCHAR(64),			-- 降車地ゾーン
	contains_id	VARCHAR(64),	-- 通過ゾーン(使用しない)
	FOREIGN KEY (route_id)
	REFERENCES routes (route_id)
);

-- 描画情報
CREATE TABLE shapes (
	shape_id		VARCHAR(64),	-- 描画ID
	shape_pt_lat		VARCHAR(16),			-- 描画緯度
	shape_pt_lon		VARCHAR(16),			-- 描画経度
	shape_pt_sequence	INT UNSIGNED,			-- 描画順序
	shape_dist_traveled	INT UNSIGNED			-- 描画距離(使用しない)
);

-- 提供情報
CREATE TABLE feed_info (
	feed_publisher_name	TEXT NOT NULL,		-- 提供組織名
	feed_publisher_url	TEXT NOT NULL,		-- 提供組織URL
	feed_lang		VARCHAR(16) NOT NULL,	-- 提供言語
	feed_start_date		VARCHAR(12),		-- 到着時刻(HH:MM:SS形式)
	feed_end_date		VARCHAR(12),		-- 到着時刻(HH:MM:SS形式)
	feed_version		TEXT			-- 提供データバージョン
);

-- 翻訳情報
CREATE TABLE translations (
	trans_id	TEXT NOT NULL,		-- 翻訳元文字列
	lang		VARCHAR(8) NOT NULL,	-- 言語
	translation	TEXT NOT NULL		-- 翻訳先言語
);
