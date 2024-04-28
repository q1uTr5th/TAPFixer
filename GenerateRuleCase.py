import random
from RuleExtractor import RuleExtractor
from DevieceCapExtractor import DevieceCapExtractor
import re

# dce = DevieceCapExtractor()
# device_capbilities = dce.data_dic
# res = extract_IFTTT_rule('./rule/all_in_dict.txt', device_capbilities)
def extract_IFTTT_rule(path, device_capbilities):
    # print(rule)
    rule = {}
    for key, value in device_capbilities.items():
        rule.update({key.replace(' ', '').replace('\n', ''): []})
    f = open(path, 'r', encoding='utf-8')
    lines = f.readlines()
    # 提取T,C,A
    for single_rule in lines:
        extract_rule = []
        single_rule = single_rule.replace(' ', '').replace(',', '')

        trigger, action = '', ''
        if 'AND' not in single_rule:
            re1 = 'IF(.*?)THEN'
            trigger = re.findall(re1, single_rule)[0].split('&')
            # print(trigger)
            re3 = 'THEN(.*?)\n'
            action = re.findall(re3, single_rule)[0].split('&')
            extract_rule.append(trigger)
            extract_rule.append(['none'])
            extract_rule.append([action[0].split('=')[1]])
            extract_rule.append([0, 'none'])
        else:
            re1 = 'IF(.*?)AND'
            trigger = re.findall(re1, single_rule)[0].split('&')
            print(trigger)
            re2 = 'AND(.*?)THEN'
            condition = re.findall(re2, single_rule)[0].split('&')
            print(condition)
            # print(trigger)
            re3 = 'THEN(.*?)\n'
            action = re.findall(re3, single_rule)[0].split('&')
            extract_rule.append(trigger)
            extract_rule.append([condition])
            extract_rule.append([action[0].split('=')[1]])
            extract_rule.append([0, 'none'])
            print(action)
        # print(action[0].split('=')[0])
        try:
            # print(rule[action[0].split('=')[0]])
            rule[action[0].split('=')[0]].append(extract_rule)
        except:
            print(single_rule)
    return rule

def generate_single_rule_case():
    # 暂时不选 soundSensor.sound, lightSensor.illuminance
    sensor = ['presenceSensor.presence','temperatureMeasurement.temperature','smokeDetector.smoke',
              'carbonMonoxideDetector.carbonMonoxide','carbonDioxideMeasurement.carbonDioxide','rainSensor.rain','relativeHumidityMeasurement.humidity']

    # smokeDetector.smoke

    actuator = [['light.switch'],
    ['garageDoorControl','doorControl.door','camera.switch'],
    ['airConditionerMode.airConditionerMode','heater.switch','airConditioner.switch','electricBlanket.switch'],
    ['fan.switch','window.switch','sprinkler.switch','valve.valve','hotwater.switch','alarm.alarm'],
    ['refrigerator.switch','smartPlug.switch','coffeMaker.switch','ovenMode.ovenMode']]


    entity_rule_list_append = {'light.switch': [['presenceSensor.presence=present'], ['none'], ['on'], [0, 'none']],
        'alarm.alarm': [[['smokeDetector.smoke=detected'], ['none'], ['siren'], [0, 'none']]],
        'window.switch': [[['temperatureMeasurement.temperature>20'], ['none'], ['on'], [0, 'none']],
                          #[['smokeDetector.smoke=detected'], ['none'], ['on', 'off'], [5, 0, 'none']],
                          [['temperatureMeasurement.temperature<18'], ['none'], ['off'], [0, 'none']],
                          [['temperatureMeasurement.temperature>27'], ['none'], ['on'], [0, 'none']],
                          [['temperatureMeasurement.temperature<16'], ['none'], ['off'], [0, 'none']]],
        'fan.switch': [[['smokeDetector.smoke=detected'], ['none'], ['on', 'off'], [5, 0, 'none']],
                       [['rainSensor.rain=detected'], ['none'], ['on', 'off'], [4, 0, 'none']],
                        #[['waterSensor.water=wet'], ['none'], ['on', 'off'], [4, 0, 'none']],
                        [['presenceSensor.presence=present'], ['none'], ['on', 'off'], [3, 0, 'none']]],
        'heater.switch': [[['temperatureMeasurement.temperature<16'], ['none'], ['on'], [0, 'none']],
                          [['temperatureMeasurement.temperature<18'], ['presenceSensor.presence=present'], ['on'], [0, 'none']],
                          #[['temperatureMeasurement.temperature>25'], ['presenceSensor.presence=present', 'window.switch=off'], ['off'], [0, 'none', 'trigger_delay 5']],
                          [['temperatureMeasurement.temperature>24'], ['none'], ['off'], [0, 'none']],
                          [['presenceSensor.presence=present'], ['none'], ['on'], [0, 'none']],
                          [['presenceSensor.presence=present'], ['none'], ['off'], [0, 'none']]],
                          #[['presenceSensor.presence=present'], ['none'], ['none', 'on'], [5, 0, 'none']]],
       'airConditioner.switch': [[['presenceSensor.presence=not_present'], ['none'], ['off'], [0, 'none']]]}
          # [['presenceSensor.presence=present'], ['none'], ['none', 'on'], [5, 0, 'none']]]}

    path = r'.\rule\all_in_dict.txt'
    rule_extractor = RuleExtractor(path)
    entity_attribute_list = rule_extractor.get_device_capbilities()
    entity_rule_list = rule_extractor.get_rules()
    #print(entity_attribute_list)
    #print(entity_rule_list)
    for key, value in entity_rule_list_append.items():
        #print(len(entity_rule_list[key]))
        for i in entity_rule_list_append[key]:
            entity_rule_list[key].append(i)
        #print(len(entity_rule_list[key]))
    #print(entity_rule_list)

    # 最少四个通道,包含4和len(sensor)
    sensor_choice = random.randint(4, len(sensor))
    selected_sensor = random.choices(sensor, k=sensor_choice)
    #print('selected_sensor')
    #print(selected_sensor)
    sensor_related_rule = {}
    for eitity_attribute, tap_set in entity_rule_list.items():
        sensor_related_rule.update({eitity_attribute: []})
    # 获得T为它的所有备选项
    for eitity_attribute, tap_set in entity_rule_list.items():
        for single_rule in tap_set:
            if len(single_rule) == 4:
                trigger = single_rule[0][0]
                sign = ''
                if '>=' in trigger:
                    sign = '>='
                elif '<=' in trigger:
                    sign = '<='
                elif '<' in trigger:
                    sign = '<'
                elif '>' in trigger:
                    sign = '>'
                elif '=' in trigger:
                    sign = '='
                trigger_attribute = trigger.split(sign)[0]
                if trigger_attribute in selected_sensor:
                    sensor_related_rule[eitity_attribute].append(single_rule)
    #print('sensor_related_rule')
    #print(sensor_related_rule)
    sensor_related_rule_amount = 0
    for eitity_attribute, tap_set in sensor_related_rule.items():
        if len(tap_set) > 0 and [] not in tap_set:
            sensor_related_rule_amount += len(tap_set)
    #print(sensor_related_rule_amount)


    # 最少两类设备
    actuator_choice = random.randint(2, len(actuator))
    tmp = random.choices(actuator, k=actuator_choice)
    selected_actuator = []
    for single_category in tmp:
        for j in single_category:
            selected_actuator.append(j)
    #print('selected_actuator')
    #print(selected_actuator)
    actuator_related_rule = {}
    for eitity_attribute, tap_set in entity_rule_list.items():
        actuator_related_rule.update({eitity_attribute: []})
    # 获得ACTION为它的所有备选项
    for eitity_attribute, tap_set in entity_rule_list.items():
        if eitity_attribute in selected_actuator:
            for single_rule in tap_set:
                if len(single_rule) == 4:
                    actuator_related_rule[eitity_attribute].append(single_rule)
    #print('actuator_related_rule')
    #print(actuator_related_rule)
    actuator_related_rule_amount = 0
    for eitity_attribute, tap_set in actuator_related_rule.items():
        if len(tap_set) > 0 and [] not in tap_set:
            actuator_related_rule_amount += len(tap_set)
    #print(actuator_related_rule_amount)

    total_related_rule = {}
    for eitity_attribute, tap_set in entity_rule_list.items():
        total_related_rule.update({eitity_attribute: []})
    # 总备选规则暂时放sensor_related_rule
    for eitity_attribute, tap_set in actuator_related_rule.items():
        for single_rule in tap_set:
            if len(single_rule) == 4:
                sensor_related_rule[eitity_attribute].append(single_rule)
    sensor_related_rule_amount = 0
    for eitity_attribute, tap_set in sensor_related_rule.items():
        sensor_related_rule_amount += len(tap_set)
    #print(sensor_related_rule_amount)
    # 去重
    for eitity_attribute, tap_set in sensor_related_rule.items():
        tmp = []
        for single_rule in tap_set:
            if single_rule not in tmp:
                tmp.append(single_rule)
        for i in tmp:
            total_related_rule[eitity_attribute].append(i)
    total_related_rule_amount = 0
    for eitity_attribute, tap_set in total_related_rule.items():
        if len(tap_set) > 0 and [] not in tap_set:
            total_related_rule_amount += len(tap_set)
    #print('# 去重后的总备选规则')
    #print(total_related_rule_amount)

    # 范围大于20
    # 获得每个entity的规则数，让它们每个的随机之和在25-35之间
    total_related_rule_list = []
    if total_related_rule_amount >= 25:
        for eitity_attribute, tap_set in total_related_rule.items():
            if len(tap_set) > 0 and [] not in tap_set:
                for single_rule in tap_set:
                    total_related_rule_list.append([eitity_attribute, single_rule])
        #print(len(total_related_rule_list))
        choice = random.randint(15, 30)
        selected_rule = random.choices(total_related_rule_list, k=choice)
        #print(len(selected_rule))
        selected_dict = {}
        for i in selected_rule:
            selected_dict.update({i[0]: []})
        for i in selected_rule:
            selected_dict[i[0]].append(i[1])

        #print(selected_dict)
        #print(len(selected_dict))
        amount = 0
        for eitity_attribute, tap_set in selected_dict.items():
            if len(tap_set) > 0 and [] not in tap_set:
                amount += len(tap_set)
        #print(amount)
        return selected_dict, amount



'''foo = range(0, 10 + 1)  # 0,10之间生成12个数,和等于60
str1 = []  # 目标列表
i = 0  # 生成次数
while sum(str1) != 60:
    i += 1
    str1 = random.choices(foo, k=12)

print(str1)'''