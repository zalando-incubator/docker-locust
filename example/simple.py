from locust import HttpLocust
from locust import TaskSet
from locust import task
from locust.web import app


class SimpleBehavior(TaskSet):

    @task
    def index(self):
        self.client.get('/')


class MyLocust(HttpLocust):
    task_set = SimpleBehavior
    min_wait = 0
    max_wait = 0
