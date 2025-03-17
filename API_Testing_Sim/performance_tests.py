from locust import HttpUser, task, between

class ApiUser(HttpUser):
    wait_time = between(1, 5)

    @task
    def process_youtube(self):
        self.client.post("/process-youtube", json={"url": "https://www.youtube.com/watch?v=jmmW0F0biz0"})