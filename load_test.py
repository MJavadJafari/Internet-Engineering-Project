import random
from locust import HttpUser, task, between


class MyUser(HttpUser):
    wait_time = between(1, 2)

    @task
    def my_task(self):
        book_id = random.choices(range(1, 1001), weights=range(1, 1001))[0]
        with self.client.get(f"/book/info-suggestion/{book_id}/", catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure("Got wrong response code")
