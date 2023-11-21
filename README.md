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
B[Sonnen API] -.->|PV data every min| A[Synology Docker Container]
A[Synology Docker Container] -->|API| C[Go-echarger API]
C[Go-echarger API] -.->|wallbox state every 15min| A[Synology Docker Container]
A[Synology Docker Container] -->|API| K[openhab API]
K[openhab API] -.->|Wallbox Automation Item ON/OFF| A[Synology Docker Container]
A[Synology Docker Container] -->D("Input Data
                PV_Production
                PV_Concumption
                Wallbox charging state
                Wallbox Ampere set
                Wallbox Automation Status")
D --> L{"Wallbox Automation
          ON or OFF"}
L -->|ON| M["wait 60 seconds"]
L -->|OFF| E("Caluclate PV Surplus and set Wallbox Charging
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
