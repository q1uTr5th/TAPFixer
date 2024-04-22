# TAPFixer: Automatic Detection and Repair of Home Automation Vulnerabilities based on Negated-property Reasoning


# Introduction
TAPFixer is an automatic vulnerability detection and repair framework for TAP-based home automation systems. It can model TAP rules with practical latency and physical features to capture the accurate rule execution behaviors both in the logical and physical space and identify interaction vulnerabilities.



# Setting up TAPFixer
Open TAPFixer as a Python IDE (e.g., Pycharm) project and then run it.

Python interpreter used in TAPFixer is 3.8.

# Define TAP rules


# Verify HA system with predefined or customized corretness properties
TAPFixer uses correctness properties for vulnerability detection. A property is a criterion to describe what automation behavior is safe or not. Generally, it can be expressed in linear temporal logic (LTL) which describes the relative or absolute order of behaviors in the system (e.g., the next state denoted by X, the subsequent path denoted by F, and the entire path denoted by G). 

## Predefined properties
According to safety-sensitive and commonly used devices, we develop 53 properties for vulnerability detection and repair as shown below:

|-|-|
|Property|Description|
|P.1|IF the user arrives home, the light should be turned on.|
|P.2|IF the user is not at home / not nearby-home, the light should be turned off.|
|P.3|WHEN the user is not at home / not nearby-home, the light should be off.|
|P.4|IF the user arrives home, the garage door should be opened.|
|P.5|IF the user leaves home, the garage door should be closed.|
|P.6|WHEN the user leaves home, the garage door should be closed.|
|P.7|IF the user is not at home / not nearby-home, the door should be locked.|
|P.8|WHEN the user is not at home / not nearby-home, the door should be locked.|
|P.9|IF the user is not at home / not nearby-home, the security camera should be turned on.|
|P.10|WHEN the user is not at home / not nearby-home, the security camera should be on.|
|P.11|IF the door opens while the user is not at home / not nearby-home, the security camera should take pictures.|
|P.12|IF the user is not at home / not nearby-home, the switch should be turned off.|
|P.13|WHEN the user is not at home / not nearby-home, the switch should be off.|
|P.14|IF the temperature is below 15℃ and someone is at home, the AC should be in heating mode.|
|P.15|IF the temperature rises above 25℃, the AC should be in cooling mode.|
|P.16|WHEN the heater is on, the AC should be off.|
|P.17|IF the user is not at home / not nearby-home, the AC should be turned off.|
|P.18|WHEN the user is not at home / not nearby-home, the AC should be off.|
|P.19|IF the temperature is below 15℃ while someone is at home, the heater should be turned on.|
|P.20|IF the temperature rises above 19℃, the heater should be turned off.|
|P.21|WHEN the AC is on, the heater should be off.|
|P.22|IF the user is not at home / not nearby-home, the heater should be turned off.|
|P.23|WHEN the user is not at home / not nearby-home, the heater should be off.|
|P.24|IF the user is not at home / not nearby-home, the coffee machine should be turned off.|
|P.25|WHEN the user is not at home / not nearby-home, the coffee machine should be off.|
|P.26|IF the user is not at home / not nearby-home, the electric blanket should be turned off.|
|P.27|WHEN the user is not at home / not nearby-home, the electric blanket should be off.|
|P.28|IF the smoke is detected, the alarm should be activated.|
|P.29|WHEN there is smoke, the alarm should be activated.|
|P.30|IF CO is detected, the alarm should be activated.|
|P.31|WHEN CO is detected, the alarm should be activated.|
|P.32|IF humidity is greater than a predefined value, the ventilating fan should be turned on.|
|P.33|IF CO2 is greater than a predefined value, the ventilating fan should be turned on.|
|P.34|\revise{WHEN CO2 remains greater than a predefined value, the ventilating fan should be on for at least the permitted time}.|
|P.35|IF the user is not at home / not nearby-home, the oven should be turned off.|
|P.36|WHEN the user is not at home / not nearby-home, the oven should be off.|
|P.37|IF CO is detected, the natural gas hot water heater should be turned off.|
|P.38|WHEN CO is detected, the natural gas hot water heater should be off.|
|P.39|IF CO is detected, the gas valve should shut off.|
|P.40|WHEN CO is detected, the gas valve should be closed.|
|P.41|IF the smoke is detected, the water valve should be turned on.|
|P.42|WHEN there is smoke, the water valve should be on.|
|P.43|IF the soil moisture sensor is below a predefined value, the sprinkler system should be turned on.|
|P.44|\revise{When the soil moisture sensor is below a predefined value, the sprinkler system should be on for at least the permitted time}.|
|P.45|IF the weather is raining, the sprinkler should be turned off.|
|P.46|WHEN the weather is raining, the sprinkler should be off.|
|P.47|IF CO2 is greater than a predefined value, the window should be opened.|
|P.48|IF the weather is raining, the window should be closed.|
|P.49|WHEN the weather is raining, the window should be closed.|
|P.50|IF the smoke is detected, the window should be opened.|
|P.51|WHEN there is smoke, the window should be opened.|
|P.52|IF CO is detected, the window should be opened.|
|P.53|WHEN CO is detected, the window should be opened.|



## Customized properties

--------------

# The user-study data
