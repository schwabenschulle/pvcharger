import requests
import json
import logging
import os
import time
import lib.goecharger as goe
import lib.sonnen as solar


'''Enable loging'''
logging.basicConfig(level=logging.INFO)
logfh  = logging.FileHandler(os.path.join(f'/var/log/containers','main.log'))
logger = logging.getLogger('Main')
logger.addHandler(logfh)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
logfh.setFormatter(formatter)

def ampere_set_check(ampere_dict, solar_power_average, batterie_capacity):
    '''compare solar and batterie charge capacity against wallbox ampere setting'''
    for i, (A, P) in enumerate(ampere_dict.items()):
        if solar_power_average > P:
            previous_item = A
            if i == 4:
                ampere_set = A
                break
            continue
        if solar_power_average < P and i > 0:
            ampere_set = previous_item
            return ampere_set, i 
        elif batterie_capacity > 50:
            ampere_set = A
            return ampere_set, i
        else: 
            ampere_set = 0
            return ampere_set, i

def set_color(color):
    '''set color to Ampere in Wallbox and start or stop with frc setting'''
    """# in color string needs to be replaced by %23"""
    wallbox.set_attr("cid", color)
    if wallbox.response_code == 200:
        logger.info(f"set color {color} successful - Response:{wallbox.response_code}")
    else:
        logger.error(f"set color {color} - Response:{wallbox.response}")    

    

if __name__ == '__main__':
    url = "http://192.168.88.18"
    url_sonnen = "http://192.168.88.6"
    sn = "068673"
    token = "mtGKYCA3pTKH18O3rbOtXc9LQp094kb3"

    '''iniate classes'''
    wallbox = goe.wallbox(**{"url" : url, "sn" : sn, "token" : token})
    sonnen = solar.sonnen(**{"url" : url_sonnen})
    count = 0
    while True:
        count = count + 1
        solar_power_list = [] 
        wallbox.get_status()
        if wallbox.response_code == 200:
            logger.info(f"Ampere: {wallbox.charge_ampere}A Ampere_Dict: {wallbox.ampere_dict} http_code: {wallbox.response_code}")
        else:
            logger.error(f"Get wallbox status {wallbox.response}_code")    

        #print (f"{json.dumps(wallbox.status, sort_keys=True, indent=2, separators=(',', ':'))} {wallbox.response_code}")

        sonnen.get_status()
        print (sonnen.response)
        house_usage = int((sonnen.response['Consumption_W']))
        solar_power = int((sonnen.response['Production_W']))
        batterie_capacity = int((sonnen.response['USOC']))
        solar_power_list.append(solar_power)
        #solar_power = 5000
        #batterie_capacity = 20
        logger.info(f"Solar Power: {solar_power}W Batterie: {batterie_capacity}% Cunsption_cur: {house_usage}W")

        '''compare solar and batterie charge capacity against wallbox ampere setting'''
        if count == 15:
            count = 0
            solar_power_average = sum(solar_power_list) / len(solar_power_list)
            solar_power_list = []
            logger.info(f"Solar Power Averafe: {solar_power_average}W")
            ampere_set, i = ampere_set_check(wallbox.ampere_dict, solar_power_average, batterie_capacity)
            logger.info(f"Setting Index:{i} Amphere:{ampere_set}")

            '''set color to Ampere in Wallbox and start or stop with frc setting'''
            """# in color string needs to be replaced by %23"""
            if ampere_set == 0:
                set_color('"%23FF4B00"')
            else:
                set_color('"%2319EA15"')
                
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
        time.sleep(10)    

'''Sonnen API documentaion http://192.168.88.6/api/doc.html'''
"""attach car and read charfing power """