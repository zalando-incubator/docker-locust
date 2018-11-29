from locust import HttpLocust
from locust import TaskSet
from locust import task

# For HTML reporting
from locust.web import app
from src import report
app.add_url_rule('/htmlreport', 'htmlreport', report.download_report)

class SimpleBehavior(TaskSet):

    @task
    def index(self):
        self.client.get('/')


class MyLocust(HttpLocust):
    task_set = SimpleBehavior
    min_wait = 0
    max_wait = 0
