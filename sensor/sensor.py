import time
import random
from datetime import datetime
import os
import json
import redis

REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", "6379"))
SENSOR_INTERVAL = int(os.getenv("SENSOR_INTERVAL", "2"))
TEMPERATURE_MIN = float(os.getenv("TEMPERATURE_MIN", "15.0"))
TEMPERATURE_MAX = float(os.getenv("TEMPERATURE_MAX", "30.0"))
HUMIDITY_MIN = float(os.getenv("HUMIDITY_MIN", "30.0"))
HUMIDITY_MAX = float(os.getenv("HUMIDITY_MAX", "80.0"))

LOG_DIR = "log"
LOG_FILE = os.path.join(LOG_DIR, "sensore.log")
os.makedirs(LOG_DIR, exist_ok=True)

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0, decode_responses=True)

while True:
    reading = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "temperatura": round(random.uniform(TEMPERATURE_MIN, TEMPERATURE_MAX), 2),
        "umidita": round(random.uniform(HUMIDITY_MIN, HUMIDITY_MAX), 2)
    }

    line = f"[{reading['timestamp']}] Temp: {reading['temperatura']} °C  Umidità: {reading['umidita']} %"
    print(line)

    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")

    payload = json.dumps(reading)
    r.set("ultima_lettura", payload)
    r.lpush("storico_letture", payload)

    time.sleep(SENSOR_INTERVAL)