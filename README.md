# TAPFixer: Automatic Detection and Repair of Home Automation Vulnerabilities based on Negated-property Reasoning


# Introduction
TAPFixer is an automatic vulnerability detection and repair framework for TAP-based home automation systems. It can model TAP rules with practical latency and physical features to capture the accurate rule execution behaviors both in the logical and physical space and identify interaction vulnerabilities.



# Setting up TAPFixer
Open TAPFixer as a Python IDE (e.g., Pycharm) project and then run it.

Python interpreter used in TAPFixer is 3.8.


# Verify your HA system with predefined or customized corretness properties
TAPFixer uses correctness properties for vulnerability detection. A property is a criterion to describe what automation behavior is safe or not. Generally, it can be expressed in linear temporal logic (LTL) which describes the relative or absolute order of behaviors in the system (e.g., the next state denoted by X, the subsequent path denoted by F, and the entire path denoted by G). 

## Predefined properties
According to safety-sensitive and commonly used devices, we develop 53 properties for vulnerability detection and repair as shown below:

## Customized properties

--------------

# The user-study data
