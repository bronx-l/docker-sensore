from flask import Flask, jsonify
import redis
import time

app = Flask(__name__)

def get_redis_client():
    retries = 10
    while retries > 0:
        try:
            return redis.Redis(host="redis", port=6379, db=0, decode_responses=True)
        except redis.exceptions.ConnectionError:
            retries -= 1
            time.sleep(1)
    raise Exception("Redis non raggiungibile")

@app.route("/")
def home():
    return "API sensore attiva"

@app.route("/last-reading")
def last_reading():
    r = get_redis_client()
    value = r.get("ultima_lettura")
    return jsonify({"ultima_lettura": value})

@app.route("/history")
def history():
    r = get_redis_client()
    values = r.lrange("storico_letture", 0, 9)
    return jsonify({"storico_letture": values})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)