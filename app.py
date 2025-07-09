from flask import Flask, jsonify
import threading
import time
import os

app = Flask(__name__)

# 初始 JSON 結構
parking_data = {
    "on_street": [],
    "off_street": [
        {
            "uid": "1107-offstreetGE",
            "name": "Demo Lot 1",
            "kind": "OffStreet",
            "min_hourly_rate": None,
            "max_hourly_rate": None,
            "max_duration_mins": None,
            "consumer_parking_allowed": None,
            "until": None,
            "next_disallowed_type": None,
            "availability_state": "high",
            "capacity": 60,
            "estimated_spaces": 0,
            "estimated_full_time": None,
            "distance_from_center": None,
            "geojson_center": {
                "type": "Point",
                "coordinates": [-87.6154528659257, 41.839345214735]
            },
            "geojson_geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [-87.615809767461, 41.8392281200473],
                        [-87.6158117863599, 41.8394410905166],
                        [-87.6149627294214, 41.8394511419997],
                        [-87.6149609350484, 41.8393400416038],
                        [-87.6154167060568, 41.8393336222849],
                        [-87.6154149022188, 41.8392329423387],
                        [-87.615809767461, 41.8392281200473]
                    ]
                ]
            }
        }
    ]
}

# 背景執行：每 2 分鐘變動 estimated_spaces
def update_spaces():
    value = 0
    direction = 1
    while True:
        parking_data["off_street"][0]["estimated_spaces"] = value
        time.sleep(120)
        value += direction
        if value == 60:
            direction = -1
        elif value == 0:
            direction = 1

# 啟動背景執行緒
threading.Thread(target=update_spaces, daemon=True).start()

# API 路由
@app.route('/api/data')
def get_parking_data():
    return jsonify(parking_data)

# 啟動伺服器（本地或 Railway 用）
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
