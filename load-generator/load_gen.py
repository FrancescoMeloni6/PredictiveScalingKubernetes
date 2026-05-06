import math
import random
from locust import HttpUser, task, constant, LoadTestShape

HASH_HOST   = "http://hash-service.default.svc:80"
RANDOM_HOST = "http://random-service.default.svc:80"
HASH_RATIO  = 0.5
MIN_RPS        = 1
MAX_RPS        = 10
PERIOD_SECONDS = 60 * 60 * 24 

class WorkloadUser(HttpUser):
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
        run_time  = self.get_run_time()
        amplitude = (MAX_RPS - MIN_RPS) / 2
        midpoint  = (MAX_RPS + MIN_RPS) / 2
        rps       = midpoint + amplitude * math.sin(2 * math.pi * run_time / PERIOD_SECONDS)

        user_count  = max(1, round(rps))
        spawn_rate  = max(1, user_count // 5)
        return (user_count, spawn_rate)