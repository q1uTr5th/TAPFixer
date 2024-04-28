
# 其中有些不会受设备影响，如下雨
EXTENDED_ENVIRONMENT = ['smokeDetector.smoke', 'rainSensor.rain', 'relativeHumidityMeasurement.humidity', 'temperatureMeasurement.temperature',
                        'carbonMonoxideDetector.carbonMonoxide', 'carbonDioxideMeasurement.carbonDioxide']
# smokeDetector.smoke可能不算，这类变量采用定期变化
# 不被设备影响的延时自然属性
UNAFFECTED_EXTENDED_ENVIRONMENT = ['rainSensor.rain']


NUMBER_ABSTRACT = ['relativeHumidityMeasurement.humidity', 'temperatureMeasurement.temperature',
                   'carbonDioxideMeasurement.carbonDioxide',
                   'lightSensor.illuminance', 'soundPressureLevel.soundPressureLevel']

AFFECTED_IMMEDIATE_ENVIRONMENT = ['lightSensor.illuminance', 'soundPressureLevel.soundPressureLevel']
UNAFFECTED_IMMEDIATE_ENVIRONMENT = ['presenceSensor.presence', 'voice.command', 'nearby.home']
LAST_STATE = '_last'
ENVIRONMENT_COUNT = '_count'
TAB = '    '
ITERATION_UPPER = 50
ROUND_UPPER = 15
NEW_RULE_AMOUNT = 1

class CHANNEL_INTERACTION_CONFIG(object):
    # config_list包括不处理，如果threshold恒定则[10,10]，否则[10,15]
    def __init__(self, name, config_list, threshold):
        self.name = name
        self.config_list = config_list
        self.threshold = threshold

# 如果不处理不变则['not_handle', 0]
# threshold控制在2-3个能处理
CHANNEL_INTERACTION_CONFIG_LIST = [CHANNEL_INTERACTION_CONFIG('smokeDetector.smoke', [['fan.switch = on', 6], ['valve.valve = open', 6], ['window.switch = on', 3], ['not_handle', 0]], [4, 8]),
CHANNEL_INTERACTION_CONFIG('carbonMonoxideDetector.carbonMonoxide', [['window.switch = on', 6], ['fan.switch = on', 6], ['not_handle', 0]], [4, 8]),
CHANNEL_INTERACTION_CONFIG('temperatureMeasurement.temperature', [['heater.switch = on', 4], ['window.switch = on', -4], ['thermostatMode.thermostatMode = heat', 6], ['thermostatMode.thermostatMode = cool', -6],
                                                                 ['airConditionerMode.airConditionerHeatMode = on', 4], ['airConditionerMode.airConditionerCoolMode = on', -4], ['not_handle', 0]], [4, 8, -8, -4]),
CHANNEL_INTERACTION_CONFIG('carbonDioxideMeasurement.carbonDioxide', [['window.switch = on', -4], ['fan.switch = on', -4], ['not_handle', 0]], [4, 8, -8, -4]),
CHANNEL_INTERACTION_CONFIG('relativeHumidityMeasurement.humidity',
                          [['sprinkler.switch = on', 4], ['fan.switch = on', -6], ['humidifier.switch = on', 4], ['dehumidifier.switch = on', -6], ['not_handle', 0]], [4, 8, -8, -4]),
CHANNEL_INTERACTION_CONFIG('soundPressureLevel.soundPressureLevel',
                          [['window.switch = on', 4], ['window.switch = off', -4], ['not_handle', 0]], [0]),
CHANNEL_INTERACTION_CONFIG('lightSensor.illuminance',
                          [['light.switch = on', 100], ['light.switch = off', -100], ['not_handle', 0]], [0])
                                   ]

# 单位时间提升或下降多少
CHANNEL_INTERACTION_CONFIG_PER_TIME = {'temperatureMeasurement.temperature': 1, 'soundPressureLevel.soundPressureLevel': 1,
                                       'lightSensor.illuminance': 1, 'relativeHumidityMeasurement.humidity': 1,
                                       'carbonDioxideMeasurement.carbonDioxide': 1}

# 单影响
# 应该定义为不安全状态，属于环境属性的，window.switch这类不用管，因为他们不影响smokeDetector.smoke_count
CHANNEL_INTERACTION_CONFIG_DICT = {'smokeDetector.smoke': 'detected', 'rainSensor.rain': 'raining', 'carbonMonoxideDetector.carbonMonoxide': 'detected'}

'''spec_list = [[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain != rainSensor.rain_last)->X(window.switch = close))', 'state-event'],
             [r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain = rainSensor.rain_last)->(window.switch = close))', 'state-state'],
             [r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(window.switch = open))', 'state-event'],
             [r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(window.switch = open))', 'state-state'],
             [r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(alarm.alarm = siren))', 'state-event'],
             [r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(alarm.alarm = siren))', 'state-state'],
             [r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(fan.switch = on))', 'state-event'],
             [r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(fan.switch = on))', 'state-state']]'''


SPEC_LIST_SITUATION = [
[[r'--LTLSPEC G((presenceSensor.presence = present & presenceSensor.presence != presenceSensor.presence_last)->X(light.switch = on))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = present & presenceSensor.presence != presenceSensor.presence_last)->X(garageDoorControl.door = open))', 'state-event']],

[[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(light.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(light.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(garageDoorControl.door = closed))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(garageDoorControl.door = closed))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(doorControl.door = closed))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(doorControl.door = closed))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(camera.switch = on))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(camera.switch = on))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(smartPlug.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(smartPlug.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(airConditioner.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(airConditioner.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(heater.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(heater.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(coffeMaker.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(coffeMaker.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(electricBlanket.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(electricBlanket.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(ovenMode.ovenMode = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(ovenMode.ovenMode = off))', 'state-state'],
[r'--LTLSPEC G((doorControl.door = open & doorControl.door != doorControl.door_last)->X(camera.switch = on))', 'state-event']],

[[r'--LTLSPEC G((temperatureMeasurement.temperature = 14 & temperatureMeasurement.temperature_last = 15)->X(airConditionerMode.airConditionerHeatMode = on))', 'state-event'],
[r'--LTLSPEC G((temperatureMeasurement.temperature = 26 & temperatureMeasurement.temperature_last = 25)->X(airConditionerMode.airConditionerCoolMode = on))', 'state-event'],
[r'--LTLSPEC G((temperatureMeasurement.temperature = 14 & temperatureMeasurement.temperature_last = 15)->X(heater.switch = on))', 'state-event'],
[r'--LTLSPEC G((temperatureMeasurement.temperature = 20 & temperatureMeasurement.temperature_last = 19)->X(heater.switch = off))', 'state-event'],
[r'--LTLSPEC G((heater.switch = on & heater.switch != heater.switch_last)->X(airConditioner.switch = off))', 'state-event'],
[r'--LTLSPEC G((airConditioner.switch = on & airConditioner.switch != airConditioner.switch_last)->X(heater.switch = off))', 'state-event']],

[[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(alarm.alarm = siren))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(alarm.alarm = siren))', 'state-state'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(fan.switch = on))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(fan.switch = on))', 'state-state'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(valve.valve = open))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(valve.valve = open))', 'state-state'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(window.switch = on))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(window.switch = on))', 'state-state']],

[[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(alarm.alarm = siren))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(alarm.alarm = siren))', 'state-state'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(hotwater.switch = off))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(hotwater.switch = off))', 'state-state'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(window.switch = on))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(window.switch = on))', 'state-state'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(valve.valve = closed))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(valve.valve = closed))', 'state-state'],
[r'--LTLSPEC G((carbonDioxideMeasurement.carbonDioxide = 6 & carbonDioxideMeasurement.carbonDioxide_last = 5)->X(window.switch = on))', 'state-event']],

[[r'--LTLSPEC G((relativeHumidityMeasurement.humidity = 13 & relativeHumidityMeasurement.humidity_last = 12)->X(fan.switch = on))', 'state-event'],
[r'--LTLSPEC G((relativeHumidityMeasurement.humidity = 7 & relativeHumidityMeasurement.humidity_last = 8)->X(sprinkler.switch = on))', 'state-event'],
[r'--LTLSPEC G((relativeHumidityMeasurement.humidity = 13 & relativeHumidityMeasurement.humidity_last = 12)->X(sprinkler.switch = off))', 'state-event']],

[[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain != rainSensor.rain_last)->X(sprinkler.switch = off))', 'state-event'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain = rainSensor.rain_last)->(sprinkler.switch = off))', 'state-state'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain != rainSensor.rain_last)->X(window.switch = off))', 'state-event'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain = rainSensor.rain_last)->(window.switch = off))', 'state-state']]
]


SPEC_LIST_NEARBY = [
[[r'--LTLSPEC G((home.mode = home & home.mode != home.mode_last)->X(light.switch = on))', 'state-event'],
[r'--LTLSPEC G((home.mode = home & home.mode != home.mode_last)->X(garageDoorControl.door = open))', 'state-event']],

[[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(light.switch = off))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(light.switch = off))', 'state-state'],
[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(garageDoorControl.door = closed))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(garageDoorControl.door = closed))', 'state-state'],
[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(doorControl.door = closed))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(doorControl.door = closed))', 'state-state'],
[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(camera.switch = on))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(camera.switch = on))', 'state-state'],
[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(smartPlug.switch = off))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(smartPlug.switch = off))', 'state-state'],
[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(airConditioner.switch = off))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(airConditioner.switch = off))', 'state-state'],
[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(heater.switch = off))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(heater.switch = off))', 'state-state'],
[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(coffeMaker.switch = off))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(coffeMaker.switch = off))', 'state-state'],
[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(electricBlanket.switch = off))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(electricBlanket.switch = off))', 'state-state'],
[r'--LTLSPEC G((home.mode = away & home.mode != home.mode_last)->X(ovenMode.ovenMode = off))', 'state-event'],
[r'--LTLSPEC G((home.mode = away & home.mode = home.mode_last)->(ovenMode.ovenMode = off))', 'state-state'],
[r'--LTLSPEC G((doorControl.door = open & doorControl.door != doorControl.door_last)->X(camera.switch = on))', 'state-event']],


[[r'--LTLSPEC G((temperatureMeasurement.temperature = 14 & temperatureMeasurement.temperature_last = 15)->X(airConditionerMode.airConditionerHeatMode = on))', 'state-event'],
[r'--LTLSPEC G((temperatureMeasurement.temperature = 26 & temperatureMeasurement.temperature_last = 25)->X(airConditionerMode.airConditionerCoolMode = on))', 'state-event'],
[r'--LTLSPEC G((temperatureMeasurement.temperature = 14 & temperatureMeasurement.temperature_last = 15)->X(heater.switch = on))', 'state-event'],
[r'--LTLSPEC G((temperatureMeasurement.temperature = 20 & temperatureMeasurement.temperature_last = 19)->X(heater.switch = off))', 'state-event'],
[r'--LTLSPEC G((heater.switch = on & heater.switch != heater.switch_last)->X(airConditioner.switch = off))', 'state-event'],
[r'--LTLSPEC G((airConditioner.switch = on & airConditioner.switch != airConditioner.switch_last)->X(heater.switch = off))', 'state-event']],


[[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(alarm.alarm = siren))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(alarm.alarm = siren))', 'state-state'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(fan.switch = on))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(fan.switch = on))', 'state-state'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(valve.valve = open))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(valve.valve = open))', 'state-state'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(window.switch = on))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(window.switch = on))', 'state-state']],

[[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(alarm.alarm = siren))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(alarm.alarm = siren))', 'state-state'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(hotwater.switch = off))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(hotwater.switch = off))', 'state-state'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(window.switch = on))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(window.switch = on))', 'state-state'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(valve.valve = closed))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(valve.valve = closed))', 'state-state'],
[r'--LTLSPEC G((carbonDioxideMeasurement.carbonDioxide = 6 & carbonDioxideMeasurement.carbonDioxide_last = 5)->X(window.switch = on))', 'state-event']],


[[r'--LTLSPEC G((relativeHumidityMeasurement.humidity = 13 & relativeHumidityMeasurement.humidity_last = 12)->X(fan.switch = on))', 'state-event'],
[r'--LTLSPEC G((relativeHumidityMeasurement.humidity = 7 & relativeHumidityMeasurement.humidity_last = 8)->X(sprinkler.switch = on))', 'state-event'],
[r'--LTLSPEC G((relativeHumidityMeasurement.humidity = 13 & relativeHumidityMeasurement.humidity_last = 12)->X(sprinkler.switch = off))', 'state-event']],


[[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain != rainSensor.rain_last)->X(sprinkler.switch = off))', 'state-event'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain = rainSensor.rain_last)->(sprinkler.switch = off))', 'state-state'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain != rainSensor.rain_last)->X(window.switch = off))', 'state-event'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain = rainSensor.rain_last)->(window.switch = off))', 'state-state']]
]



SPEC_LIST_PRIORITY = [
[[r'--LTLSPEC G((presenceSensor.presence = present & presenceSensor.presence != presenceSensor.presence_last)->X(light.switch = on))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(light.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(light.switch = off))', 'state-state']],

[[r'--LTLSPEC G((presenceSensor.presence = present & presenceSensor.presence != presenceSensor.presence_last)->X(garageDoorControl.door = open))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(garageDoorControl.door = closed))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(garageDoorControl.door = closed))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(doorControl.door = closed))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(doorControl.door = closed))', 'state-state']],

[[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(camera.switch = on))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(camera.switch = on))', 'state-state'],
[r'--LTLSPEC G((doorControl.door = open & doorControl.door != doorControl.door_last)->X(camera.switch = on))', 'state-event']],

[[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(smartPlug.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(smartPlug.switch = off))', 'state-state']],

[[r'--LTLSPEC G((temperatureMeasurement.temperature = 14 & temperatureMeasurement.temperature_last = 15)->X(airConditionerMode.airConditionerHeatMode = on))', 'state-event'],
[r'--LTLSPEC G((temperatureMeasurement.temperature = 26 & temperatureMeasurement.temperature_last = 25)->X(airConditionerMode.airConditionerCoolMode = on))', 'state-event'],
[r'--LTLSPEC G((heater.switch = on & heater.switch != heater.switch_last)->X(airConditioner.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(airConditioner.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(airConditioner.switch = off))', 'state-state']],

[[r'--LTLSPEC G((temperatureMeasurement.temperature = 14 & temperatureMeasurement.temperature_last = 15)->X(heater.switch = on))', 'state-event'],
[r'--LTLSPEC G((temperatureMeasurement.temperature = 20 & temperatureMeasurement.temperature_last = 19)->X(heater.switch = off))', 'state-event'],
[r'--LTLSPEC G((airConditioner.switch = on & airConditioner.switch != airConditioner.switch_last)->X(heater.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(heater.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(heater.switch = off))', 'state-state']],

[[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(coffeMaker.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(coffeMaker.switch = off))', 'state-state']],
#26
[[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(electricBlanket.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(electricBlanket.switch = off))', 'state-state']],

[[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(alarm.alarm = siren))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(alarm.alarm = siren))', 'state-state'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(alarm.alarm = siren))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(alarm.alarm = siren))', 'state-state']],


[[r'--LTLSPEC G((relativeHumidityMeasurement.humidity = 13 & relativeHumidityMeasurement.humidity_last = 12)->X(fan.switch = on))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(fan.switch = on))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(fan.switch = on))', 'state-state']],

[[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(ovenMode.ovenMode = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(ovenMode.ovenMode = off))', 'state-state']],


[[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(hotwater.switch = off))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(hotwater.switch = off))', 'state-state']],


[[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(valve.valve = open))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(valve.valve = open))', 'state-state'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(valve.valve = closed))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(valve.valve = closed))', 'state-state']],


[[r'--LTLSPEC G((relativeHumidityMeasurement.humidity = 7 & relativeHumidityMeasurement.humidity_last = 8)->X(sprinkler.switch = on))', 'state-event'],
[r'--LTLSPEC G((relativeHumidityMeasurement.humidity = 13 & relativeHumidityMeasurement.humidity_last = 12)->X(sprinkler.switch = off))', 'state-event'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain != rainSensor.rain_last)->X(sprinkler.switch = off))', 'state-event'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain = rainSensor.rain_last)->(sprinkler.switch = off))', 'state-state']],

[[r'--LTLSPEC G((carbonDioxideMeasurement.carbonDioxide = 6 & carbonDioxideMeasurement.carbonDioxide_last = 5)->X(window.switch = on))', 'state-event'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain != rainSensor.rain_last)->X(window.switch = off))', 'state-event'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain = rainSensor.rain_last)->(window.switch = off))', 'state-state']],
    # 50
[[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(window.switch = on))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(window.switch = on))', 'state-state'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide != carbonMonoxideDetector.carbonMonoxide_last)->X(window.switch = on))', 'state-event'],
[r'--LTLSPEC G((carbonMonoxideDetector.carbonMonoxide = detected & carbonMonoxideDetector.carbonMonoxide = carbonMonoxideDetector.carbonMonoxide_last)->(window.switch = on))', 'state-state']]
]


SPEC_LIST_COMPARE = [
[[r'--LTLSPEC G((presenceSensor.presence = present & presenceSensor.presence != presenceSensor.presence_last)->X(light.switch = on))', 'state-event']],

[[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(light.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(light.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(camera.switch = on))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(camera.switch = on))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(smartPlug.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(smartPlug.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(airConditioner.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(airConditioner.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(coffeMaker.switch = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(coffeMaker.switch = off))', 'state-state'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence != presenceSensor.presence_last)->X(ovenMode.ovenMode = off))', 'state-event'],
[r'--LTLSPEC G((presenceSensor.presence = not_present & presenceSensor.presence = presenceSensor.presence_last)->(ovenMode.ovenMode = off))', 'state-state']],

[[r'--LTLSPEC G((temperatureMeasurement.temperature = 26 & temperatureMeasurement.temperature_last = 25)->X(airConditionerMode.airConditionerCoolMode = on))', 'state-event']],


[[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(alarm.alarm = siren))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(alarm.alarm = siren))', 'state-state'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(window.switch = on))', 'state-event'],
[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(window.switch = on))', 'state-state']],

[[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain != rainSensor.rain_last)->X(window.switch = off))', 'state-event'],
[r'--LTLSPEC G((rainSensor.rain = detected & rainSensor.rain = rainSensor.rain_last)->(window.switch = off))', 'state-state']]
]


