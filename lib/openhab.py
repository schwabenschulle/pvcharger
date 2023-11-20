import requests
import json

class openhab:
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", None)

    def get_items(self, item):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        response = self.session.get(f"{self.url}:8080/rest/items/{item}?recursive=false", verify=False)
        self.response = json.loads(response.content)
        self.response_code = response.status_code
