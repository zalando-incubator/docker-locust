import json
import os
from random import randint

from locust import HttpLocust
from locust import TaskSet
from locust import task
from locust.web import app

from src import report

# For reporting
app.add_url_rule('/htmlreport', 'htmlreport', report.download_report)

# Read json file
json_file = os.path.join(os.path.dirname(__file__), 'payloads.json')


class SimplePostBehavior(TaskSet):

    def __init__(self, parent):
        super(SimplePostBehavior, self).__init__(parent)
        with open(json_file) as file:
            self.payloads = json.load(file, 'utf-8')
        self.length = len(self.payloads) - 1

    @task
    def post_random_payload(self):
        p = self.payloads[randint(0, self.length)]
        print(p)
        self.client.post('/', json={'name': p.get('name'), 'gender': p.get('gender')})


class MyLocust(HttpLocust):
    task_set = SimplePostBehavior
