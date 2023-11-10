import requests
import json

class wallbox:
    def __init__(self, **kwargs):
        self.charge_staus = False
        self.car_attach_status = None
        self.url = kwargs.get("url", None)
        self.charge_power = None
        self.charge_ampere = None

    def status(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        response = self.session.get(f"{self.url}/api/status", verify=False)
        self.status = json.loads(response.content)
        self.response_code = response.status_code
        self.charge_ampere = wallbox.status['amp']

url = "http://192.168.88.18"
wallbox = wallbox(**{"url" : url})
wallbox.status()
#print (f"{json.dumps(wallbox.status, sort_keys=True, indent=2, separators=(',', ':'))} {wallbox.response_code}")
print (f"Ampere: {wallbox.charge_ampere}A http_code: {wallbox.response_code}")
