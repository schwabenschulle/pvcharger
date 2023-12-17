# go-eCharger PV Surplus Controller
# Overview
This is a privat project provides a solution for intelligently managing the charging of a go-eCharger wallbox by considering the surplus power generated from photovoltaic (PV) systems. It's designed to integrate with a Sonnen PV battery and can be used in conjunction with OpenHAB for home automation.

# Features
PV Surplus Calculation: Continuously monitors PV power generation and calculates surplus by accounting for current household usage.
Smart Charging: Adjusts the charging power of the go-eCharger wallbox based on real-time calculations, ensuring optimal use of surplus PV energy.
Battery Capacity Consideration: Takes into account the capacity of the connected Sonnen PV battery to maximize efficiency.
Frequent Updates: The system checks the PV power every minute and makes adjustments accordingly.

# Requirements
go-eCharger Wallbox
Sonnen PV Battery System
OpenHAB Home Automation Setup

# How It Works
PV Power Monitoring: The script checks the PV power output every minute.
Calculating Surplus: By subtracting current household usage from the PV output, it calculates the surplus power.
Loop Interaction: After 15 iterations, it calculates the average PV surplus.
Adjusting Charge Power: Based on the average surplus and battery capacity, it adjusts the charge power of the go-eCharger wallbox and LEd color to visualize the charge capability.

```mermaid
graph TD
A[Synology Docker Container] -->|API| B[Sonnen API]

A[Synology Docker Container] -->|API| C[Go-echarger API]
A[Synology Docker Container] -->|API| K[openhab API]
B[Sonnen API] -.->|PV data every min|D("Input Data
                PV_Production
                PV_Concumption
                Wallbox charging state
                Wallbox Ampere set
                Wallbox Automation Status")
K[openhab API] -.->|Wallbox Automation Item ON/OFF| D
C[Go-echarger API] -.->|wallbox state every 15min| D
D --> L{"Wallbox Automation
          ON or OFF"}
L -->|OFF| M["wait 60 seconds"]
M --> A[Synology Docker Container]
L -->|ON| E("Caluclate PV Surplus and set Wallbox Charging
         Ampere for next 15 min
        PV Surplus = PV Produnction - House consumption")
E --> F{"PV Surplus > Charge min Power"}
F -->|no| G{"If battery > 50%"}
G --> |no| H["wallbox stop charging
             set LED color to red"]
G -->|yes| I["wallbox start charging
              set 6A charge power
              set LED color to green"]
F -->|yes| J["Set best Ampere set depending
              on average PV Surplus in last 15 min
              Set LED color to green"]

```
# Build Image (optional)
acme@nadine-PC:/mnt/c/Users/nadine/Documents/Container$ 
docker build --no-cache -t pvcharger:RC17 .
docker image tag pvcharger:RC17 schwabenschulle/pvcharger:1.1
docker push schwabenschulle/pvcharger:1.1

# Start Docker Container:

Open the Docker application on your Synology NAS.
Navigate to the 'Image' tab.
Select the option to add an image from a URL.
Download the Container:

In the URL field, enter schwabenschulle/pvcharger. This should allow you to download the container from DockerHub.
![image](https://github.com/schwabenschulle/pvcharger/assets/39119520/32153408-c761-4283-8d62-6560d4f8e6c7)

Container Configuration:

Once the container is downloaded, click 'Start' to initiate the container setup.
You will need to adjust the Volume and Environment Variables as part of the setup.

Set Volume
You need to mount a host folder to /var/log/containers
![image](https://github.com/schwabenschulle/pvcharger/assets/39119520/5bf8ec5b-cce4-4295-87b3-d4d724307e6e)

Set Environment Variables:

In the environment variables section, you need to add the URLs for your wallbox, Sonnen battery, and OpenHAB. These URLs are essential for the container to communicate with your devices.

e.g.
url_wallbox = "http://192.168.8.18"
url_sonnen = "http://192.168.8.6"
url_openhab = "http://192.168.8.42"

for testing:
export url_wallbox="http://192.168.88.18"
export url_sonnen="http://192.168.88.6"
export url_openhab="http://192.168.88.42"

![image](https://github.com/schwabenschulle/pvcharger/assets/39119520/88d51371-a605-4d9a-b63f-3ce73ae18309)

# Verify Successful Start:
After setting up the Docker container, you can confirm that it has started successfully by opening the 'Detail' tab in the Docker application.
Within the 'Detail' tab, click on 'Protocol'. This should display logs.
![image](https://github.com/schwabenschulle/pvcharger/assets/39119520/421cd49c-0b5c-479a-a1f9-dcf1f0da21cf)
