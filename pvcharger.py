import requests
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import time
import lib.goecharger as goe
import lib.sonnen as solar
import lib.openhab as ohab


'''Enable loging'''
logging.basicConfig(level=logging.INFO)
#logfh  = logging.FileHandler(os.path.join(f'/var/log/containers','main.log'))
logfh = RotatingFileHandler(f'/var/log/containers/main.log', maxBytes=200000, backupCount=10)
logger = logging.getLogger('Main')
logger.addHandler(logfh)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logfh.setFormatter(formatter)

def ampere_set_check(ampere_dict, solar_power_average, batterie_capacity, battery_status):
    '''compare solar and batterie charge capacity against wallbox ampere setting'''
    for i, (A, P) in enumerate(ampere_dict.items()):
        if solar_power_average > P:
            previous_item = A
            if i == 10:
                ampere_set = A
                break
            continue
        if solar_power_average < P and i > 0:
            ampere_set = previous_item
            return ampere_set, i
        if battery_status is True:
            ampere_set = A
            return ampere_set, i
        elif battery_status is False:
            ampere_set = 0
            return ampere_set, i
        else: 
            ampere_set = battery_status
            return ampere_set, i

def set_color(color):
    '''set color to Ampere in Wallbox and start or stop with frc setting'''
    """# in color string needs to be replaced by %23"""
    wallbox.set_attr("cid", color)
    if wallbox.response_code == 200:
        logger.info(f"set color {color} successful - Response:{wallbox.response_code}")
    else:
        logger.error(f"set color {color} - Response:{wallbox.response}")    

def pv_surplus_calc(sonnen, wallbox):
        if wallbox.charge_staus == 0:   
            solar_power = int((sonnen.response['Production_W'])) - (int((sonnen.response['Consumption_W'])) - wallbox.charge_power)
        else:
            solar_power = int((sonnen.response['Production_W'])) - int(sonnen.response['Consumption_W'])
        return solar_power

def check_battery(batterie_capacity):
    if batterie_capacity > 70:
        return True
    if 50 <= int(batterie_capacity) <= 70:
        return None
    else: return False

if __name__ == '__main__':
#    url_wallbox = os.environ['url_wallbox']
#    url_sonnen = os.environ['url_sonnen']
#    url_openhab = os.environ["url_openhab"]
    url_wallbox = "http://192.168.88.18"
    url_sonnen = "http://192.168.88.6"
    url_openhab = "http://192.168.88.42"
    '''sn and token are needed to use cloud API. Currently not used in this code'''
    sn = ""
    token = ""

    '''iniate class for wallbox and Sonnen Battery'''
    wallbox = goe.wallbox(**{"url" : url_wallbox, "sn" : sn, "token" : token})
    sonnen = solar.sonnen(**{"url" : url_sonnen})
    openhab = ohab.openhab(**{"url" : url_openhab})
    
    solar_power_list = [] 
    count = 0
    battery_status = False
    while True:
        try:
            openhab.get_items("Wallbox")
            if openhab.response['state'] == "OFF":
                logger.info("Automation Admin disabled")
                set_color('"%2319EA15"')
                time.sleep(60)
                continue

            count = count + 1
            '''Pull infos from Sonnen battery API and preserv battery capacity in a varaible'''
            '''Sonnen API documentaion http://{IP}/api/doc.html'''
            sonnen.get_status()
            batterie_capacity = int((sonnen.response['USOC']))
            wallbox.get_attr('frc')
            wallbox.response = json.loads(wallbox.response.content)
            wallbox.charge_staus = wallbox.response['frc'] 
            wallbox.get_status()
            if wallbox.response_code == 200:
                logger.info(f"Ampere: {wallbox.charge_ampere}A Ampere_Dict: {wallbox.ampere_dict} http_code: {wallbox.response_code}")
            else:
                logger.error(f"Get wallbox status {wallbox.response}_code")    
            if wallbox.charge_staus == 0:
                wallbox.charge_power = wallbox.ampere_dict[str(wallbox.charge_ampere)]
            else:
                wallbox.charge_power = 0
            '''Calculate PV Surplus - Logic: PV Surplus is Solar-Inputv - house_usage - charge power  '''
            solar_power = pv_surplus_calc(sonnen, wallbox)

            '''add caculated solar_power to a list which is after 15 loop interactions get used to calclulate the average'''
            solar_power_list.append(solar_power)
            logger.info(f"Solar_Surplus:{solar_power} Charge_Power: {wallbox.charge_power}")

            '''calulate average solar_power surplus and decide wallbox charge power setting under consideration of battery capacity'''
            if count == 10:
                count = 0
                wallbox.get_status()
                if wallbox.response_code == 200:
                    logger.info(f"Ampere: {wallbox.charge_ampere}A Ampere_Dict: {wallbox.ampere_dict} http_code: {wallbox.response_code}")
                else:
                    logger.error(f"Get wallbox status {wallbox.response}_code")    
        #        print (f"{json.dumps(wallbox.status, sort_keys=True, indent=2, separators=(',', ':'))} {wallbox.response_code}")

                solar_power_average = sum(solar_power_list) / len(solar_power_list)
                solar_power_list = []
                logger.info(f"Solar Power Average: {solar_power_average}W Battery Capacity {batterie_capacity}%")
                battery_status = check_battery(batterie_capacity)
                ampere_set, i = ampere_set_check(wallbox.ampere_dict, solar_power_average, batterie_capacity, battery_status)
                if ampere_set is None:
                    logger.info(f"battery in of 50% - 70% coninue")
                    continue    
                logger.info(f"Setting Index:{i} Amphere:{ampere_set}")

                '''set color in Wallbox amber for not enough charging energy and green for charging possible'''
                """# in color string needs to be replaced by %23"""
                if ampere_set == 0:
                    set_color('"%23FF4B00"')
                else:
                    set_color('"%2319EA15"')
                    
                '''set Ampere in Wallbox and start or stop with frc setting'''
                
                if ampere_set == 0 and wallbox.car_attach_status == 2 and wallbox.charge_staus != 1:
                    wallbox.charge_power = 0
                    wallbox.set_attr("frc", 1 )
                    if wallbox.response_code == 200:
                        logger.info(f"Stop charging {wallbox.response_code}")
                    else:
                        logger.error(f"Stop charging {wallbox.response}")
                            
                elif ampere_set > 0 and wallbox.car_attach_status == 4:
                    wallbox.charge_power = wallbox.ampere_dict[ampere_set]
                    wallbox.set_attr("frc", 0)
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
            time.sleep(60)    
        except Exception as e:
            logger.error(f'Fatal:{e}')
            time.sleep(60)



