import requests
import json

'''https://github.com/goecharger/go-eCharger-API-v2'''
class wallbox:
    def __init__(self, **kwargs):
        self.charge_staus = False
        self.car_attach_status = None
        self.url = kwargs.get("url", None)
        self.sn = kwargs.get("sn", None)
        self.token = kwargs.get("token", None)
        self.charge_power = 0
        self.charge_ampere = None

    def get_status(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        response = self.session.get(f"{self.url}/api/status", verify=False)
        self.status = json.loads(response.content)
        self.response_code = response.status_code
        self.charge_ampere = self.status['amp']
        self.car_attach_status = self.status['car']
        self.charge_staus = self.status['frc']
        self.ampere_dict = {}
        self.ampere_dict = { "6":2560,
                             "7":2980,
                             "8":3370,
                             "9":3780,
                             "10":4210,
                             "11":4640,
                             "12":5030,
                             "13":5460,
                             "14":5900,
                             "15":6290,
                             "16":6740}
    def get_attr(self, attr):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.response = self.session.get(f"{self.url}/api/status?filter={attr}", verify=False)


    def set_attr(self, attr, value):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        response = self.session.get(f'{self.url}/api/set?{attr}={value}', verify=False)
        self.response = json.loads(response.content)
        self.response_code = response.status_code

    def set_attr_cloud(self, attr, value):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})
        response = self.session.get(f'https://{self.sn}.api.v3.go-e.io/api/set?{attr}={value}', verify=True)
        self.response = json.loads(response.content)
        self.response_code = response.status_code
