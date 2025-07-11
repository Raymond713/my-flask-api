from flask import Flask, jsonify, request, render_template_string, Response
import threading
import time
import os
from collections import OrderedDict
from datetime import datetime
import json

app = Flask(__name__)

# Global parking data with config as a list
parking_data = OrderedDict({
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
                        [-87.61580976746095, 41.83922812004734],
                        [-87.6158117863599, 41.83944109051658],
                        [-87.61496272942144, 41.839451141999724],
                        [-87.61496093504843, 41.83934004160383],
                        [-87.61541670605679, 41.83933362228489],
                        [-87.61541490221879, 41.839232942338654],
                        [-87.61580976746095, 41.83922812004734]
                    ]
                ]
            }
        }
    ],
    "config": [
        {
            "config_version": "2025.07.09-00:00",
            "update_required": True,
            "apply_on_next_boot": False,
            "parameters": {
                "api_key": "https://guidance.streetline.com/v3/guidance/by-customer?customer=api_demo_1&api_key=XXXXXXXXXXXXXXXXXX",
                "uid": 0,               
                "interval": 15,
                "front_light_level": 10,
            }
        }
    ]
})

# Background thread to simulate changing estimated_spaces
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

# Start background thread
threading.Thread(target=update_spaces, daemon=True).start()

# API endpoint to get data
@app.route('/api/data')
def get_data():
    result = OrderedDict([
        ("on_street", parking_data["on_street"]),
        ("off_street", parking_data["off_street"]),
        ("config", parking_data["config"])
    ])
    return Response(json.dumps(result, separators=(',', ':')), mimetype='application/json')

# Update config via API
@app.route('/api/update_config', methods=['POST'])
def update_config():
    data = request.json
    config_block = parking_data["config"][0]
    for key in ["api_key", "uid", "interval", "front_light_level"]:
        if key in data:
            config_block["parameters"][key] = data[key]
    config_block["apply_on_next_boot"] = data.get("apply_on_next_boot", config_block["apply_on_next_boot"])
    config_block["update_required"] = data.get("update_required", config_block["update_required"])
    config_block["config_version"] = datetime.now().strftime("%Y.%m.%d-%H:%M")
    return jsonify({"status": "updated", "config": config_block})

# Frontend form to edit config
@app.route('/')
def index():
    config_block = parking_data["config"][0]
    params = config_block["parameters"]
    form_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Update Parking Config</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <style>
            body { padding: 30px; }
            .form-container { max-width: 700px; margin: auto; }
        </style>
    </head>
    <body>
    <div class="form-container">
        <h2 class="mb-4">Update Parking Config</h2>
        <form action="/update" method="post">
            <div class="mb-3">
                <label class="form-label">API Key:</label>
                <input type="text" class="form-control" name="api_key" value="{{params['api_key']}}">
            </div>
            <div class="mb-3">
                <label class="form-label">UID:</label>
                <input type="number" class="form-control" name="uid" value="{{params['uid']}}">
            </div>
            <div class="mb-3">
                <label class="form-label">Interval:</label>
                <input type="number" class="form-control" name="interval" value="{{params['interval']}}" min="10">
            </div>
            <div class="mb-3">
                <label class="form-label">Front Light Level:</label>
                <input type="number" class="form-control" name="front_light_level" value="{{params['front_light_level']}}" min="1" max="12">
            </div>
                        <div class="mb-3">
                <label class="form-label">Update Required:</label>
                <select class="form-select" name="update_required">
                    <option value="true" {% if config['update_required'] %}selected{% endif %}>True</option>
                    <option value="false" {% if not config['update_required'] %}selected{% endif %}>False</option>
                </select>
            </div>
            <div class="mb-3">
                <label class="form-label">Apply On Next Boot:</label>
                <select class="form-select" name="apply_on_next_boot">
                    <option value="true" {% if config['apply_on_next_boot'] %}selected{% endif %}>True</option>
                    <option value="false" {% if not config['apply_on_next_boot'] %}selected{% endif %}>False</option>
                </select>
            </div>
            <button type="submit" class="btn btn-primary">Update</button>
        </form>
    </div>
    </body>
    </html>
    """
    return render_template_string(form_html, config=config_block, params=params)

@app.route('/update', methods=['POST'])
def update():
    config_block = parking_data["config"][0]
    params = config_block["parameters"]
    for key in ["api_key", "uid", "interval", "front_light_level"]:
        if key in request.form:
            val = request.form[key]
            params[key] = int(val) if key in ["uid", "interval", "front_light_level"] else val
    config_block["update_required"] = request.form.get("update_required", "false") == "true"
    config_block["apply_on_next_boot"] = request.form.get("apply_on_next_boot", "false") == "true"
    config_block["config_version"] = datetime.now().strftime("%Y.%m.%d-%H:%M:%S")
    return "<p>Config Updated</p><a href='/'>Back</a>"

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
