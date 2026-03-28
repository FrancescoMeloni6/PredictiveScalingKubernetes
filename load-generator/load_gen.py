import os
import time
import math
import random
import requests

TARGET_RANDOM  = os.getenv("TARGET_RANDOM",  "http://random-service.default.svc:80")
TARGET_HASH    = os.getenv("TARGET_HASH",    "http://hash-service.default.svc:80")
MIN_RPS        = float(os.getenv("MIN_RPS",  "1"))
MAX_RPS        = float(os.getenv("MAX_RPS",  "10"))
PERIOD_SECONDS = float(os.getenv("PERIOD_SECONDS", "1800"))
HASH_RATIO     = float(os.getenv("HASH_RATIO", "0.5"))

_start_time   = time.time()

def rps_sinusoidal(t: float) -> float:
    amplitude = (MAX_RPS - MIN_RPS) / 2
    midpoint  = (MAX_RPS + MIN_RPS) / 2
    return midpoint + amplitude * math.sin(2 * math.pi * t / PERIOD_SECONDS)

def send_request(url: str, service: str):
    t0 = time.time()
    if service == "hash":
        payload = {"input_text": f"load-test-{random.randint(0, 999999)}"}
        requests.post(url, data=payload, timeout=10)
    else:
        requests.get(url, timeout=10)

def main():
        while True:
            elapsed = time.time() - _start_time
            rps = max(0.1, rps_sinusoidal(elapsed))

            n_requests = max(1, round(rps))

            for _ in range(n_requests):
                if random.random() < HASH_RATIO:
                    send_request(TARGET_HASH, "hash")
                else:
                    send_request(TARGET_RANDOM, "random")

            time.sleep(1.0)

if __name__ == "__main__":
    main()