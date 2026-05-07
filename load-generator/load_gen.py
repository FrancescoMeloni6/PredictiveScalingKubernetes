import math
import random
from datetime import datetime
from locust import HttpUser, task, constant, LoadTestShape

HASH_HOST   = "http://hash-service.default.svc:80"
RANDOM_HOST = "http://random-service.default.svc:80"
HASH_RATIO  = 0.5

MIN_RPS     = 1
MAX_RPS     = 10
PEAK_HOUR   = 18
MIN_HOUR    = PEAK_HOUR - 12
PERIOD_SEC  = 24 * 3600

class WorkloadUser(HttpUser):
    host = RANDOM_HOST
    wait_time = constant(1)

    @task
    def generate_load(self):
        if random.random() < HASH_RATIO:
            payload = {"input_text": f"load-test-{random.randint(0, 999999)}"}
            self.client.post(HASH_HOST, data=payload, name="hash-service", timeout=10)
        else:
            self.client.get(RANDOM_HOST, name="random-service", timeout=10)

class SinusoidalLoad(LoadTestShape):
    def tick(self):
        now = datetime.now()

        t = ((now.hour - MIN_HOUR - 6) % 24) * 3600 + now.minute * 60 + now.second

        amplitude = (MAX_RPS - MIN_RPS) / 2
        midpoint  = (MAX_RPS + MIN_RPS) / 2

        rps = midpoint + amplitude * math.sin(
            2 * math.pi * t / PERIOD_SEC
        )

        user_count = max(1, round(rps))
        spawn_rate = max(1, user_count // 5)
        return (user_count, spawn_rate)