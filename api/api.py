from flask import Flask, jsonify, request
import redis
import time
import json
import os

app = Flask(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))

def get_redis_client():
    retries = 10
    while retries > 0:
        try:
            client = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)
            client.ping()
            return client
        except redis.exceptions.ConnectionError:
            retries -= 1
            time.sleep(1)
    raise Exception("Redis non raggiungibile")

@app.route("/api")
def home():
    return "API sensore attiva"

@app.route("/api/health")
def health():
    try:
        r = get_redis_client()
        r.ping()
        return jsonify({
            "status": "ok",
            "redis": "ok"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "redis": "unreachable",
            "message": str(e)
        }), 503

@app.route("/api/last-reading")
def last_reading():
    r = get_redis_client()
    value = r.get("ultima_lettura")

    if not value:
        return jsonify({"ultima_lettura": None})

    return jsonify(json.loads(value))

@app.route("/api/history")
def history():
    r = get_redis_client()

    limit = request.args.get("limit", default=20, type=int)
    if limit is None or limit < 1:
        limit = 20
    if limit > 100:
        limit = 100

    values = r.lrange("storico_letture", 0, limit - 1)
    parsed = [json.loads(item) for item in values]
    parsed.reverse()

    return jsonify({
        "count": len(parsed),
        "limit": limit,
        "storico_letture": parsed
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)