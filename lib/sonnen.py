import requests
import json

class sonnen:
    def __init__(self, **kwargs):
        self.battery_capacity = 0
        self.url = kwargs.get("url", None)

    def get_status(self):
        self.session = requests.Session()
        response = self.session.get(f"{self.url}/api/v2/status", verify=False)
        self.response = json.loads(response.content)
        self.response_code = response.status_code
