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
                          'securitysystem.switch': ['on', 'off'],
                          'thermometer.switch': ['on', 'off'],
                          'alarm.switch': ['on', 'off'],
                          'schedule.time': '0..24',
                          'ignition.switch': ['on', 'off'],
                          'carStatus.switch': ['on', 'off'],
                          'state.vacation': ['TRUE', 'FALSE'],
                          'state.newEvent': ['TRUE', 'FALSE'],
                          'homeboyLocation.switch': ['on', 'off'],
                          'belkin.switch': ['on', 'off'],
                          'spa.switch': ['on', 'off'],
                          'state.alarmActive': ['TRUE', 'FALSE'],
                          'state.residentsAreUp': ['TRUE', 'FALSE'],
                          'msgSend': ['TRUE', 'FALSE'],
                          'state.inactiveAt': ['cloke.timer', 'null'],
                          'state.lastClosed': ['cloke.timer', 'null'],
                          'state.lastStatus': ['on', 'off'],
                          'state.wasOn': ['TRUE', 'FALSE'],
                          'state.motionStoppedAt': ['cloke.timer', 'null', 'threshold'],
                          'trigger.switch': ['on', 'off'],
                          'check.switch': ['on', 'off'],
                          'state.lastIntruderMotion': ['cloke.timer', 'null'],
                          'state.ShouldCheckForKnock': ['TRUE', 'FALSE'],
                          'state.DoorWasOpened': ['TRUE', 'FALSE'],
                          'state.doorTrigger': ['TRUE', 'FALSE'],
                          'state.status': ['waiting', 'pending', 'complete', 'null'],
                          'state.turnOffTime': ['cloke.timer', 'null'],
                          'state.litUp': ['TRUE', 'FALSE'],
                          'state.lightMap': ['map', 'null'],
                          'state.offTime': ['TRUE', 'FALSE'],
                          'state.lastSwitchStatus': ['on', 'off'],
                          'state.lastHumidity': ['currentHumidity', 'null'],
                          'state.modeStartTime': ['0..24', 'null'],
                          }

    def collect_deviece_cap(self):
        path = '/Users/bin/Downloads/Task/Smartapp_get_rules/DeviceCapabilities/'
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


def check_dict(dict):
    # 打开txt文件
    with open("/Users/bin/Downloads/Task/Smartapp_get_rules/smarts_not_in_dict_3.txt", "r") as f:
        # 创建一个新的txt文件
        with open("/Users/bin/Downloads/Task/Smartapp_get_rules/smarts_not_in_dict_4.txt", "w") as g:
            # 逐行读取文件
            for line in f:
                # 去掉换行符
                line = line.strip()
                # 如果行为空，跳过
                if not line:
                    continue
                # 使用字符串分割提取data1和data2
                parts = line.split(",")
                if len(parts) == 2:
                    data1 = parts[0].split(" ")[1]
                    data2 = parts[1].split(" ")[1]
                    # 去掉等号或小于号或大于号及其之后的值
                    data1 = data1.split("=")[0].split("<")[0].split(">")[0]
                    data2 = data2.split("=")[0].split("<")[0].split(">")[0]
                    # 检查data1和data2是否在字典中
                    if data1 not in dict or data2 not in dict:
                        # 如果不在，将该行写入新的txt文件
                        g.write(line + "\n")
                    else:
                        with open("/Users/bin/Downloads/Task/Smartapp_get_rules/smarts_in_dict_4.txt", "a") as h:
                            h.write(line + "\n")
    print("处理完成！")


dce = DevieceCapExtractor()
dce.collect_deviece_cap()
print(dce.data_dic)
print(len(dce.data_dic))

check_dict(dce.data_dic)


# 自然属性要自己加
#print(set(entity_attribute_list.keys()) & set(dce.data_dic.keys()))
