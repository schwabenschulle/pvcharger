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
        self.ampere_dict = {}
        for clp_item in wallbox.status['clp']:
            self.ampere_dict[clp_item] = (230*clp_item)*3
            
    def set_amp(self, ampere_set):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        response = self.session.get(f"{self.url}/api/set?amp={ampere_set}", verify=False)
        self.response = json.loads(response.content)
        self.response_code = response.status_code


url = "http://192.168.88.18"
wallbox = wallbox(**{"url" : url})
wallbox.status()
#print (f"{json.dumps(wallbox.status, sort_keys=True, indent=2, separators=(',', ':'))} {wallbox.response_code}")
print (f"Ampere: {wallbox.charge_ampere}A Ampere_Dict: {wallbox.ampere_dict} http_code: {wallbox.response_code}")
solar_power = 2000
batterie_capacity = 49

'''compare solar and batterie charge capacity against wallbox ampere setting'''
for i, (A, P) in enumerate(wallbox.ampere_dict.items()):
    if solar_power > P:
        previous_item = A
        if i == 4:
            ampere_set = A
            break
        continue
    if solar_power < P and i > 0:
        ampere_set = previous_item
        break
    elif batterie_capacity > 50:
        ampere_set = A
        break
    else: 
        ampere_set = 0
        break

print (f"{i} {ampere_set}")
'''set Ampere in Wallbox'''
if wallbox.charge_ampere != ampere_set: 
    wallbox.set_amp(ampere_set)
'''add logging and error handling in response code'''
'''attach car and compare status.json'''
'''try to start and stop charging with alw key'''
'''write class for sonnen'''