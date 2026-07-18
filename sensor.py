import time
import random
from datetime import datetime
import os
import redis

LOG_DIR = "log"
LOG_FILE = os.path.join(LOG_DIR, "sensore.log")
os.makedirs(LOG_DIR, exist_ok=True)

r = redis.Redis(host="redis", port=6379, db=0, decode_responses=True)

while True:
    temperatura = round(random.uniform(15.0, 30.0), 2)
    umidita = round(random.uniform(30.0, 80.0), 2)
    timestamp = datetime.now().isoformat(timespec="seconds")
    line = f"[{timestamp}] Temp: {temperatura} °C  Umidità: {umidita} %"
    print(line)

    with open(LOG_FILE, "a") as f:
        f.write(line + "\n")

    r.set("ultima_lettura", line)
    r.lpush("storico_letture", line)

    time.sleep(2)