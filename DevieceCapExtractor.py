import json
import os
import sys



class DevieceCapExtractor(object):
    def __init__(self):
        self.data_dic = {}
        self.extra_dic = {'window.switch': ['on', 'off'],
                          'fan.switch': ['on', 'off'],
                          'refrigerator.switch': ['on', 'off'],
                          'airPurifier.switch': ['on', 'off'],
                          'camera.switch': ['on', 'off'],
                          'TV.switch': ['on', 'off'],
                          'coffeMaker.switch': ['on', 'off'],
                          'sprinkler.switch': ['on', 'off'],
                          'lightSensor.illuminance': '0..400',
                          'radio.switch': ['on', 'off'],
                          'scary.switch': ['on', 'off'],
                          'hairStraightener.switch': ['on', 'off'],
                          'bubblers.switch': ['on', 'off'],
                          'humidifier.switch': ['on', 'off'],
                          'dehumidifier.switch': ['on', 'off'],
                          'colorloop.switch': ['on', 'off'],
                          'christmasTree.switch': ['on', 'off'],
                          'stuff.switch': ['on', 'off'],
                          'hue.switch': ['on', 'off', 'onExtend'],
                          'electricBlanket.switch': ['on', 'off'],
                          'Water.switch': ['on', 'off'],
                          'sumppump.switch': ['on', 'off'],
                          'cooler.switch': ['on', 'off'],
                          'HRV.switch': ['on', 'off'],
                          'gasDryer.switch': ['on', 'off'],
                          'router.switch': ['on', 'off'],
                          'homeboy.switch': ['on', 'off'],
                          'smapper.switch': ['on', 'off'],
                          'chirp.switch': ['on', 'off'],
                          'adapter.switch': ['on', 'off'],
                          'security.switch': ['on', 'off'],
                          'relay.switch': ['on', 'off'],
                          'devices.switch': ['on', 'off'],
                          'rainMachine.switch': ['on', 'off'],
                          'light.level': '0..10',
                          'emergencySwitch.switch': ['on', 'off'],
                          'fireplace.switch': ['on', 'off'],
                          'hotwater.switch': ['on', 'off'],
                          'phoneNFC.switch': ['on', 'off'],
                          'microBees.switch': ['on', 'off'],
                          'regulator.switch': ['on', 'off'],
                          'boiler.switch': ['on', 'off'],
                          'extendedSwitch.switch': ['on_1', 'off'],
                          'securitysystem.switch': ['on', 'off'],
                          'thermometer.switch': ['on', 'off'],
                          'alarm.switch': ['on', 'off'],
                          'schedule.time': '0..24',
                          'ignition.switch': ['on', 'off'],
                          'carStatus.switch': ['on', 'off'],
                          'state.vacation': 'boolean',
                          'vacation.switch': ['on', 'off'],
                          'state.newEvent': 'boolean',
                          'homeboyLocation.switch': ['on', 'off'],
                          'belkin.switch': ['on', 'off'],
                          'spa.switch': ['on', 'off'],
                          'presenceSensor.presence': ['not_present', 'present'],
                          'airConditionerMode.airConditionerHeatMode': ['on', 'off'],
                          'airConditionerMode.airConditionerCoolMode': ['on', 'off'],
                          'airConditionerMode.airConditionerDryMode': ['on', 'off'],
                          'smokeDetector.smoke': ['clear', 'detected'],
                          'lock.lock': ['locked', 'unlocked'],
                          'relativeHumidityMeasurement.humidity': '0..20', #从100映射到20,5为单位
                          'soundPressureLevel.soundPressureLevel':'0..20', #从100映射到20,5为单位
                          'carbonMonoxideDetector.carbonMonoxide': ['clear', 'detected'],
                          'alarm.alarm': ['off', 'siren'],
                          'doorControl.door': ['closed', 'open'],
                          'rainSensor.rain':['detected', 'not_detected'],
                          'voice.command': ['on', 'off'],
                          'nearby.home': ['on', 'off'],
                          'home.mode': ['away', 'home'],
                          'sleep.mode': ['on', 'off'],
                          'specified.clock': ['on', 'off'], # 11:00
                          'contact.sensor': ['on', 'off'],
                          'attatck.mode': ['on', 'off'],
                          'app.initialize': ['on', 'off'],
                          'bedroom.switch': ['on', 'off'],
                          'location.mode': ['home_day', 'home_night', "away_day", "away_night"],
                          'motionSensor.motion': ['active', "inactive"],
                          'bulb.if_bright': ['on', 'off'],
                          'light1.switch': ['on', 'off'],
                          'light2.switch': ['on', 'off'],
                          'curlingiron.switch': ['on', 'off'],

                          # user study
                          'bathroom.mirrorSensor.presence': ['active', 'inactive'],
                          'rangeHood.switch': ['on', 'off'],
                          'co2Sensor.mode': ['monitor', 'not_monitor'],
                          'smartSpeaker.speak': ['co2Sensor.co2', 'alarm'],
                          'message.send': ['owner', 'off'],
                          'camera.face': ['unknown', 'known'],
                          'xiaoAi.sendMessage':['warning', 'weather', 'music', 'notify'],
                          'smartBasin.use':['true', 'false'],
                          'sleepDetection.sleep':['true', 'false'],
                          'curtain.switch':['open', 'close'],
                          'dryer.switch': ['on', 'off'],
                          'handSensor.hand':['true', 'false'],
                          'speaker.switch':['on','off'],
                          'earthquakeSensor.alarm': ['true', 'false'],
                          'robotCleaner.switch':['on','off'],


                          # SmartThing
                          'state.alarmActive': 'boolean',
                          'state.residentsAreUp': 'boolean',
                          'msgSend': 'boolean',
                          'state.inactiveAt': ['cloke.timer', 'null'],
                          'state.lastClosed': ['cloke.timer', 'null'],
                          'state.lastStatus': ['on', 'off'],
                          'state.wasOn': 'boolean',
                          'state.motionStoppedAt': ['cloke.timer', 'null', 'threshold'],
                          'trigger.switch': ['on', 'off'],
                          'check.switch': ['on', 'off'],
                          'state.lastIntruderMotion': ['cloke.timer', 'null'],
                          'state.ShouldCheckForKnock': 'boolean',
                          'state.DoorWasOpened': 'boolean',
                          'state.doorTrigger': 'boolean',
                          'state.status': ['waiting', 'pending', 'complete', 'null'],
                          'state.turnOffTime': ['cloke.timer', 'null'],
                          'state.litUp': 'boolean',
                          'state.lightMap': ['map', 'null'],
                          'state.offTime': 'boolean',
                          'state.lastSwitchStatus': ['on', 'off'],
                          'state.lastHumidity': ['currentHumidity', 'null'],
                          'state.modeStartTime': ['0..24', 'null']
                          }
        self.collect_deviece_cap()

    def collect_deviece_cap(self):
        path = './DeviceCapabilities/'
        file_list = os.listdir(path)
        for i in file_list:
            with open(path + i, 'r', encoding='utf-8') as fp:
                obj = json.load(fp)
                attr = obj['attributes'][0]
                name = attr['name']
                id = obj['id']
                if attr['type'] == 'ENUM':
                    self.data_dic.update({id + '.' + name: attr['value']})
                elif attr['type'] == 'NUMBER':
                    if attr['value'][1] != '':
                        self.data_dic.update({id + '.' + name: attr['value'][0] + '..' + attr['value'][1]})
                    # 'power' 'energy' 'airQuality' 'humidity' 默认100
                    else:
                        self.data_dic.update({id + '.' + name: attr['value'][0] + '..' + '100'})
                elif attr['type'] == 'boolean':
                    self.data_dic.update({id + '.' + name: 'boolean'})
            fp.close()
        self.data_dic.update(self.extra_dic)


# 自然属性要自己加
#print(set(entity_attribute_list.keys()) & set(dce.data_dic.keys()))
