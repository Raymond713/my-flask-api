from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/api/data')
def data():
    return jsonify({"message": "Hello from Railway!"})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))  # <-- 預設用 5000，但線上用 Railway 分配的
    app.run(host='0.0.0.0', port=port)
