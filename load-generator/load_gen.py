import math
import random
from datetime import datetime
from locust import HttpUser, task, between, LoadTestShape

HASH_HOST     = "http://hash-service.default.svc:80"
RANDOM_HOST   = "http://random-service.default.svc:80"

HASH_RATIO    = 0.5

MIN_RPS       = 1
MAX_RPS       = 10

PEAK_HOUR     = 14
MIN_HOUR      = PEAK_HOUR - 12
SHIFT_HOURS   = 6

PERIOD_SEC    = 24 * 3600
USERS_PER_RPS = 100

class WorkloadUser(HttpUser):
    host = RANDOM_HOST
    wait_time = between(
        USERS_PER_RPS * 0.5,
        USERS_PER_RPS * 1.5
    )

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

        t = ((now.hour - MIN_HOUR - SHIFT_HOURS) % 24) * 3600 + now.minute * 60 + now.second

        amplitude = (MAX_RPS - MIN_RPS) / 2
        midpoint  = (MAX_RPS + MIN_RPS) / 2

        rps = midpoint + amplitude * math.sin(2 * math.pi * t / PERIOD_SEC)

        user_count = max(1, round(rps * USERS_PER_RPS))
        spawn_rate = max(1, user_count // 20)
        return (user_count, spawn_rate)