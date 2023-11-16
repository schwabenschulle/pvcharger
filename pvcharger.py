import requests
import json
import logging
from sys import stdout

class wallbox:
    def __init__(self, **kwargs):
        self.charge_staus = False
        self.car_attach_status = None
        self.url = kwargs.get("url", None)
        self.sn = kwargs.get("sn", None)
        self.token = kwargs.get("token", None)
        self.charge_power = None
        self.charge_ampere = None

    def status(self):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        response = self.session.get(f"{self.url}/api/status", verify=False)
        self.status = json.loads(response.content)
        self.response_code = response.status_code
        self.charge_ampere = wallbox.status['amp']
        self.car_attach_status = wallbox.status['car']
        self.charge_staus = wallbox.status['frc']
        self.ampere_dict = {}
        for clp_item in wallbox.status['clp']:
            self.ampere_dict[clp_item] = (230*clp_item)*3

    def set_attr(self, attr, value):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        response = self.session.get(f'{self.url}/api/set?{attr}={value}', verify=False)
        self.response = json.loads(response.content)
        self.response_code = response.status_code
        print (response.url)
    def set_attr_cloud(self, attr, value):
        self.session = requests.Session()
        self.session.headers.update({'Accept': 'application/json'})
        self.session.headers.update({'Authorization': f'Bearer {self.token}'})
        response = self.session.get(f'https://{self.sn}.api.v3.go-e.io/api/set?{attr}={value}', verify=True)
        self.response = json.loads(response.content)
        self.response_code = response.status_code
        print (response.url)
        print (self.response_code)


'''Enable loging'''
logging.basicConfig(level=logging.INFO)
consoleHandler = logging.StreamHandler(stdout) #set streamhandler to stdout
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
consoleHandler.setFormatter(formatter)
logger = logging.getLogger('Main')
logger.addHandler(consoleHandler)
#logger.setLevel(logging.INFO)

url = "http://192.168.88.18"
sn = "068673"
token = "mtGKYCA3pTKH18O3rbOtXc9LQp094kb3"
wallbox = wallbox(**{"url" : url, "sn" : sn, "token" : token})
wallbox.status()
if wallbox.response_code == 200:
    logger.info(f"Ampere: {wallbox.charge_ampere}A Ampere_Dict: {wallbox.ampere_dict} http_code: {wallbox.response_code}")
else:
    logger.error(f"Get wallbox status {self.response}_code")    

print (f"{json.dumps(wallbox.status, sort_keys=True, indent=2, separators=(',', ':'))} {wallbox.response_code}")
solar_power = 1000
batterie_capacity = 60
logger.info(f"Solar Power: {solar_power}W Batterie: {batterie_capacity}%")

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

logger.info(f"Setting Index:{i} Amphere:{ampere_set}")

'''set color to Ampere in Wallbox and start or stop with frc setting'''
"""# in color string needs to be replaced by %23"""
if ampere_set == 0:
    wallbox.set_attr("cid", '"%23FF4B00"')
    if wallbox.response_code == 200:
        logger.info(f"set color red successful - Response:{wallbox.response_code}")
    else:
        logger.error(f"set color red - Response:{wallbox.response}")    

else:
    wallbox.set_attr("cid", '"%2319EA15"' )
    if wallbox.response_code == 200:
        logger.info(f"set color green {wallbox.response_code}")
    else:
        logger.error(f"set color green {wallbox.response}")    
    
'''set Ampere in Wallbox and start or stop with frc setting'''
if ampere_set == 0 and wallbox.car_attach_status == 2 and wallbox.charge_staus != 1:
    wallbox.set_attr("frc", 1 )
    if wallbox.response_code == 200:
        logger.info(f"Stop charging {wallbox.response_code}")
    else:
        logger.error(f"Stop charging {wallbox.response}")    
elif ampere_set > 0 and wallbox.car_attach_status == 4:
    wallbox.set_attr("frc", 2)
    if wallbox.response_code == 200:
        logger.info(f"Start charging {wallbox.response_code}")
    else:
        logger.error(f"Start charging {wallbox.response}")    

if wallbox.charge_ampere != ampere_set and ampere_set != 0: 
    wallbox.set_attr("amp", ampere_set)
    if wallbox.response_code == 200:
        logger.info(f"Set Amphere {wallbox.response_code}")
    else:
        logger.error(f"Set Amphere {wallbox.response}")    
    

'''write class for sonnen'''