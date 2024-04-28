from CONST import EXTENDED_ENVIRONMENT, LAST_STATE, ENVIRONMENT_COUNT, \
    CHANNEL_INTERACTION_CONFIG_LIST, CHANNEL_INTERACTION_CONFIG_DICT, CHANNEL_INTERACTION_CONFIG_DICT, CHANNEL_INTERACTION_CONFIG_PER_TIME, NUMBER_ABSTRACT, AFFECTED_IMMEDIATE_ENVIRONMENT
import os
from itertools import combinations
import re


def assign_trigger_delay(trigger_delay_record, entity_attribute_list):
    # j: ['heater.switch_trigger_delay1', ['temperatureMeasurement.temperature>25 5']]
    for j in trigger_delay_record:
        j_attribute = j[0].split('_')[0]
        j_cnt = j[0].split('_')[-1][-1]
        j_trigger = j[1][0].split(' ')[0]
        j_original_trigger = j_trigger
        j_trigger_delay = j[1][0].split(' ')[1]
        sign = ''
        j_trigger_attribute = ''
        j_trigger_attribute_value = ''

        different_str = '('
        different_list = []
        if '>=' in j_trigger:
            sign = '>='
            j_trigger_attribute = j_trigger.split(sign)[0]
            j_trigger_attribute_value = j_trigger.split(sign)[1]
            j_trigger = j_trigger_attribute + '=' + str(
                int(j_trigger_attribute_value) + CHANNEL_INTERACTION_CONFIG_PER_TIME[j_trigger_attribute]) \
                        + '&' + j_trigger_attribute + LAST_STATE + '=' + j_trigger_attribute_value
            different_str += j_trigger_attribute + '<' + j_trigger_attribute_value
            different_str += ')'
        elif '<=' in j_trigger:
            sign = '<='
            j_trigger_attribute = j_trigger.split(sign)[0]
            j_trigger_attribute_value = j_trigger.split(sign)[1]
            j_trigger = j_trigger_attribute + '=' + str(
                int(j_trigger_attribute_value) - CHANNEL_INTERACTION_CONFIG_PER_TIME[j_trigger_attribute]) \
                        + '&' + j_trigger_attribute + LAST_STATE + '=' + j_trigger_attribute_value
            different_str += j_trigger_attribute + '>' + j_trigger_attribute_value
            different_str += ')'
        elif '<' in j_trigger:
            sign = '<'
            j_trigger_attribute = j_trigger.split(sign)[0]
            j_trigger_attribute_value = j_trigger.split(sign)[1]
            j_trigger = j_trigger_attribute + '=' + str(
                int(j_trigger_attribute_value) - CHANNEL_INTERACTION_CONFIG_PER_TIME[j_trigger_attribute]) \
                        + '&' + j_trigger_attribute + LAST_STATE + '=' + j_trigger_attribute_value
            different_str += j_trigger_attribute + '>=' + j_trigger_attribute_value
            different_str += ')'
        elif '>' in j_trigger:
            sign = '>'
            j_trigger_attribute = j_trigger.split(sign)[0]
            j_trigger_attribute_value = j_trigger.split(sign)[1]
            j_trigger = j_trigger_attribute + '=' + str(
                int(j_trigger_attribute_value) + CHANNEL_INTERACTION_CONFIG_PER_TIME[j_trigger_attribute]) \
                        + '&' + j_trigger_attribute + LAST_STATE + '=' + j_trigger_attribute_value
            different_str += j_trigger_attribute + '<=' + j_trigger_attribute_value
            different_str += ')'
        elif '=' in j_trigger:
            sign = '='
            j_trigger_attribute = j_trigger.split(sign)[0]
            j_trigger_attribute_value = j_trigger.split(sign)[1]
            j_trigger += j_trigger_attribute + '!=' + j_trigger_attribute + LAST_STATE
            for key, value in entity_attribute_list.items():
                if j_trigger_attribute == key:
                    # print('j_trigger_attribute')
                    # print(j_trigger_attribute)
                    # print(value)
                    for v in value:
                        if j_trigger_attribute_value != v:
                            different_list.append(v)
                    different_list_len = len(different_list)
                    for v in range(different_list_len):
                        if (different_list_len > 1 and v == different_list_len - 1) or (different_list_len == 1):
                            different_str += j_trigger_attribute + '=' + different_list[v]
                        else:
                            different_str += j_trigger_attribute + '=' + different_list[v] + '|'
                    different_str += ')'

        trigger_delay_str = '''\n    init(%s_trigger_delay%s):=-1;
        next(%s_trigger_delay%s):=
              case
                %s & %s_trigger_delay%s=-1:0;
                -- 如果计时期间出现不一样的状态，就归-1
                %s & %s_trigger_delay%s>=0 & %s_trigger_delay%s<%s:-1;
                -- 否则进行加1
                %s & %s_trigger_delay%s>=0 & %s_trigger_delay%s<%s:%s_trigger_delay%s+1;
                -- 如果到界限，则重新归-1
                %s_trigger_delay%s=%s:-1;
                TRUE:%s_trigger_delay%s;
              esac;\n''' % (j_attribute, j_cnt, j_attribute, j_cnt,
                                    j_trigger, j_attribute, j_cnt,
                                    different_str, j_attribute, j_cnt, j_attribute, j_cnt, j_trigger_delay,
                                    j_original_trigger, j_attribute, j_cnt, j_attribute, j_cnt, j_trigger_delay,
                                    j_attribute, j_cnt,
                                    j_attribute, j_cnt, j_trigger_delay,
                                    j_attribute, j_cnt)
        return trigger_delay_str
    return ''


def generate_channel_based_config(enviroment_var, entity_attribute_list):
    # channel-based interaction config
    assign_value = []
    # smoke一种物理影响类别还是temperature两物理影响类别
    category = ''
    # 应该只找CHANNEL_INTERACTION_CONFIG_LIST和目前属性的交集 交集 交集
    for cb in CHANNEL_INTERACTION_CONFIG_LIST:
        if enviroment_var == cb.name:
            for i in cb.config_list:
                if i[0] != 'not_handle':
                    assign_value.append(i[0])
            if len(cb.threshold) == 2:
                category += 'one'
            elif len(cb.threshold) == 4:
                category += 'two'
            break
    # 结果为全部能影响该environment变量的设备动作
    #assign_value.remove('not_handle')
    '''    print('enviroment_var')
        print(enviroment_var)
        print('assign_value')
        print(assign_value)
        print('category')
        print(category)'''

    # 求在目前规则集合中，能影响该environment变量的设备动作
    attribute_in_now = []
    for key, value in entity_attribute_list.items():
        attribute_in_now.append(key)
    #print('attribute_in_now')
    #print(attribute_in_now)
    delete = []
    for i in assign_value:
        compare = i.split('=')[0].replace(' ', '')
        flag = 0
        for j in attribute_in_now:
            if compare == j:
                flag = 1
                break
        if not flag:
            delete.append(i)
    # 结果为和目前属性的交集 交集 交集
    assign_value = list(set(assign_value).difference(delete))
    #print('selected_assign_value')
    #print(assign_value)

    # 单物理影响
    s = ''
    if category == 'one':
        value_in_s = CHANNEL_INTERACTION_CONFIG_DICT[enviroment_var]
        s = ''' init(%s):=-1;
     next(%s):=
       case
         %s=%s & %s!=%s: 0;''' % (
            enviroment_var + '_CONFIG', enviroment_var + '_CONFIG', enviroment_var, value_in_s, enviroment_var,
            enviroment_var + '_last')

        # assign_value ['fan.switchCap.switch = on', 'window.switch = open']影响环境值 的排列组合，从n开始到1
        for i in range(len(assign_value), 0, -1):
            num = 0
            # c 对应一个Cnm的类<itertools.combinations object at 0x0000016AF7A6EDB0>
            c = combinations(assign_value, i)
            # j为Cnm类中的元素('fan.switchCap.switch = on', 'window.switch = open')
            for j in c:
                string1 = ''
                string2 = '%s+' % (enviroment_var + '_CONFIG')
                for k in range(len(j)):
                    # j[k]为'fan.switchCap.switch = on'
                    if k != len(j) - 1:
                        string1 = string1 + j[k] + ' & '
                        # smoke_window.switch_config
                        string2 = string2 + enviroment_var + '_' + j[k].split('=')[0].replace(' ', '') + '_config' + '+'
                    else:
                        string1 = string1 + j[k]
                        string2 = string2 + enviroment_var + '_' + j[k].split('=')[0].replace(' ', '') + '_config'
                #string2 += ')'
                # print('string1')
                # print(string1)
                # print('string2')
                # print(string2)
                s = s + '''
         %s>=0 & %s<%s & %s & %s<=%s: %s;
         %s>=0 & %s<%s & %s & %s>%s: %s;''' \
                    % (enviroment_var + '_CONFIG', enviroment_var + '_CONFIG', enviroment_var + '_threshold', string1,
                       string2, enviroment_var + '_threshold', string2,
                       enviroment_var + '_CONFIG', enviroment_var + '_CONFIG', enviroment_var + '_threshold', string1,
                       string2, enviroment_var + '_threshold', enviroment_var + '_threshold')

        # 没处理的情况
        s = s + '''
         %s>=0 & %s<%s & (%s+%s)>=0: %s + %s;
         %s>=0 & %s<%s & (%s+%s)<0: 0;
         %s>=%s: -1;
         TRUE: %s;
       esac;\n\n''' % (enviroment_var + '_CONFIG', enviroment_var + '_CONFIG', enviroment_var + '_threshold',
                       enviroment_var + '_CONFIG', enviroment_var + '_not_handle_config', enviroment_var + '_CONFIG',
                       enviroment_var + '_not_handle_config',
                       enviroment_var + '_CONFIG', enviroment_var + '_CONFIG', enviroment_var + '_threshold',
                       enviroment_var + '_CONFIG', enviroment_var + '_not_handle_config',
                       enviroment_var + '_CONFIG', enviroment_var + '_threshold', enviroment_var + '_CONFIG')

    elif category == 'two':
        s = ''' init(%s):=0;
        next(%s):=
          case''' % (
            enviroment_var + '_CONFIG', enviroment_var + '_CONFIG')

        # assign_value ['fan.switchCap.switch = on', 'window.switch = open']影响环境值 的排列组合，从n开始到1
        for i in range(len(assign_value), 0, -1):
            num = 0
            # c 对应一个Cnm的类<itertools.combinations object at 0x0000016AF7A6EDB0>
            c = combinations(assign_value, i)
            # j为Cnm类中的元素('fan.switchCap.switch = on', 'window.switch = open')
            for j in c:
                string1 = ''
                string2 = '%s+' % (enviroment_var + '_CONFIG')
                for k in range(len(j)):
                    # j[k]为'fan.switchCap.switch = on'
                    if k != len(j) - 1:
                        string1 = string1 + j[k] + ' & '
                        # smoke_window.switch_config
                        string2 = string2 + enviroment_var + '_' + j[k].split('=')[0].replace(' ', '') + '_config' + '+'
                    else:
                        string1 = string1 + j[k]
                        string2 = string2 + enviroment_var + '_' + j[k].split('=')[0].replace(' ', '') + '_config'
                # temperature_CONFIG<temperature_rise_threshold & temperature_CONFIG>temperature_drop_threshold : temperature;
                # temperature_CONFIG>=temperature_rise_threshold: temperature+1;
                # temperature_CONFIG<=temperature_drop_threshold: temperature-1;
                #print('string1')
                #print(string1)
                #print('string2')
                #print(string2)
                s = s + '''
            %s<%s & %s>%s & %s & %s<=%s & %s>=%s: %s;
            -- 一种设备状态组合
            %s<%s & %s>%s & %s & %s>%s: %s;
            %s<%s & %s>%s & %s & %s<%s: %s;''' \
                    % (enviroment_var + '_CONFIG', enviroment_var + '_rise_threshold', enviroment_var + '_CONFIG', enviroment_var + '_drop_threshold',
                       string1, string2, enviroment_var + '_rise_threshold', string2, enviroment_var + '_drop_threshold', string2,
                       enviroment_var + '_CONFIG', enviroment_var + '_rise_threshold', enviroment_var + '_CONFIG', enviroment_var + '_drop_threshold',
                       string1, string2, enviroment_var + '_rise_threshold', enviroment_var + '_rise_threshold',
                       enviroment_var + '_CONFIG', enviroment_var + '_rise_threshold', enviroment_var + '_CONFIG', enviroment_var + '_drop_threshold',
                       string1, string2, enviroment_var + '_drop_threshold', enviroment_var + '_drop_threshold')
                #print(s)
        # 超过threshold后重新计数
        s = s + '''
            -- 超过threshold后重新计数
            %s>=%s : 0;
            %s<=%s : 0;
            TRUE: %s;
          esac;\n\n''' % (enviroment_var + '_CONFIG', enviroment_var + '_rise_threshold',
                          enviroment_var + '_CONFIG', enviroment_var + '_drop_threshold',
                          enviroment_var + '_CONFIG')

    return s


def find_info_in_spec(violating_type, spec):
    if violating_type == 'liveness':
        # r'--LTLSPEC G((smoke=detected)->(X(fan.switchCap.switch = on) & F(runin_fan.switchCap.switch_on_0.timer=1 & fan.switchCap.switch = on)))'
        # r'smoke=detected  ->F  runin_fan.switchCap.switch_on_0.timer=1&fan.switchCap.switch=on'
        property_info = spec.replace('--LTLSPEC G(', '').replace('(', '').replace(')', '').replace(' ', '').split('->F')
        # smoke = detected & smoke != smoke_last , fan.switchCap.switch = on U runin_fan.switchCap.switch_on_0.timer = 1
        front_ = property_info[0]
        sign = ''

        front_attribute = property_info[0].split(sign)[0]
        front_attribute_value = property_info[0].split('&')[0].split(sign)[1]
        time_attribute = property_info[1].split('&')[0]
        end_ = property_info[1]
        sign = ''

        end_attribute = property_info[1].split('U')[0].split(sign)[0]
        end_attribute_value = property_info[1].split('U')[0].split(sign)[1]
        # print('[front_attribute, front_attribute_value, end_attribute, end_attribute_value]')
        # print([front_attribute, front_attribute_value, end_attribute, end_attribute_value])
        return [front_attribute, front_attribute_value, end_attribute, end_attribute_value]
    elif violating_type == 'state-event':
        # G((weather.rain = raining)->X(window.switch = close))  只能处理单event
        # 'weather.rain = raining & rain!=last', 'window.switch = close'
        property_info = spec.replace('--LTLSPEC G(', '').replace('(', '').replace(')', '').replace(' ', '').split('->X')
        front_ = property_info[0]
        sign = ''
        if '>=' in front_:
            sign = '>='
        elif '<=' in front_:
            sign = '<='
        elif '<' in front_:
            sign = '<'
        elif '>' in front_:
            sign = '>'
        elif '=' in front_:
            sign = '='
        front = property_info[0].split('&')
        #print(front)
        #print(sign)
        front_attribute = front[0].split(sign)[0]
        front_attribute_value = front[0].split(sign)[1]
        # front_last_attribute = front[1]
        end_ = property_info[1]
        sign = ''
        if '>=' in end_:
            sign = '>='
        elif '<=' in end_:
            sign = '<='
        elif '<' in end_:
            sign = '<'
        elif '>' in end_:
            sign = '>'
        elif '=' in end_:
            sign = '='
        end_attribute = property_info[1].split(sign)[0]
        end_attribute_value = property_info[1].split(sign)[1]
        return [front_attribute, front_attribute_value, end_attribute, end_attribute_value]
    elif violating_type == 'state-state':
        # [r'--LTLSPEC G((smoke = detected & smoke == smoke_last)->(fan.switchCap.switch = on))', 'state-state']
        # [smoke=detected&smoke==smoke_last, fan.switchCap.switch = on']
        property_info = spec.replace('--LTLSPEC G(', '').replace('(', '').replace(')', '').replace(' ', '').split('->')
        front_ = property_info[0]
        sign = ''
        if '>=' in front_:
            sign = '>='
        elif '<=' in front_:
            sign = '<='
        elif '<' in front_:
            sign = '<'
        elif '>' in front_:
            sign = '>'
        elif '=' in front_:
            sign = '='
        front = property_info[0].split('&')
        front_attribute = front[0].split(sign)[0]
        front_attribute_value = front[0].split(sign)[1]
        # front_last_attribute = front[1]
        end_ = property_info[1]
        sign = ''
        if '>=' in end_:
            sign = '>='
        elif '<=' in end_:
            sign = '<='
        elif '<' in end_:
            sign = '<'
        elif '>' in end_:
            sign = '>'
        elif '=' in end_:
            sign = '='
        end_attribute = property_info[1].split(sign)[0]
        end_attribute_value = property_info[1].split(sign)[1]
        return [front_attribute, front_attribute_value, end_attribute, end_attribute_value]


def module_RUNIN(delay):
    runin_text = '''MODULE RUNIN(delay)
VAR
  timer:0..%d;
ASSIGN
  init(timer):=0;
  next(timer):=
      case
        delay=0:0;
        timer=0 & delay>0: delay;
        timer>0 & delay>0: timer - 1;
        TRUE: timer;
      esac;\n\n''' % delay
    return runin_text

#获得action为给定属性的规则的谓词
def analyze_predicate(entity_attribute, tap_set):
    rule_predicate = []
    # 首先处理front_attribute，保证有序性方便后续original_flag处理
    tap_amount = len(tap_set)
    # 一个循环处理同设备能力多条规则的一条
    # 之后是规则中的谓词
    for i in range(tap_amount):
        # 第一个谓词是next()谓词
        li = []
        li.append(entity_attribute)
        # tap_set[i]对应一条规则
        single_rule = tap_set[i]
        # trigger
        for j in single_rule[0]:
            sign = ''
            if '>=' in j:
                sign = '>='
            elif '<=' in j:
                sign = '<='
            elif '<' in j:
                sign = '<'
            elif '>' in j:
                sign = '>'
            elif '=' in j:
                sign = '='
            li.append(j.split(sign)[0].replace(' ', ''))
        # condition
        for j in single_rule[1]:
            # 无条件
            if j == 'none':
                break
            # 有条件
            else:
                sign = ''
                if '>=' in j:
                    sign = '>='
                elif '<=' in j:
                    sign = '<='
                elif '<' in j:
                    sign = '<'
                elif '>' in j:
                    sign = '>'
                elif '=' in j:
                    sign = '='
                li.append(j.split(sign)[0].replace(' ', ''))
        rule_predicate.append(li)
    res = []
    for single_rule in rule_predicate:
        for single_predicate in single_rule:
            res.append(single_predicate)
    res = list(set(res))
    #print('rule_predicate')
    #print(res)
    return res


def estimate_related(entity_attribute_list, entity_rule_list, property_related_attribute):
    erl = {}
    logically_erl = {}
    # 初始赋值
    related_attribute = []
    related_attribute.append(property_related_attribute)
    # 首先找相关规则
    # 如果是属性本身，则将全部规则加入
    round = 0
    # 加入影响的规则
    while (True):
        new_attribute_in_one_iteration = []
        round = round + 1
        for entity_attribute, tap_set in entity_rule_list.items():
            # 新加的相关属性，['temperature', 'temperature']
            for i in related_attribute[round - 1]:
                # 加入动作为相关属性的TAP规则
                if entity_attribute == i:
                    erl.update({entity_attribute: tap_set})
                    logically_erl.update({entity_attribute: tap_set})
                    # 通过trigger找影响的entity
                    for j in tap_set:
                        trigger = j[0]
                        for single_trigger in trigger:
                            # 如果是 = 类 smoke = detected
                            re_pattern = r'[a-zA-Z0-9._]+(.*?)[a-zA-Z0-9._]+'
                            # 返回string中所有与pattern匹配的全部字符串,返回形式为数组。返回>=
                            compare_sign = re.findall(re_pattern, single_trigger)[0]
                            if compare_sign == '=':
                                new_attribute_in_one_iteration.append(single_trigger.split('=')[0].replace(' ', ''))
                            # 如果是 > >= < <=类 temperature>22
                            else:
                                # 找到字符串中第一个非英文字母，以及两段英文字母之间的字符串
                                new_attribute_in_one_iteration.append(
                                    single_trigger.split(compare_sign)[0].replace(' ', ''))
                    break
        # 为空说明影响的已经找完了
        if new_attribute_in_one_iteration == []:
            break
        related_attribute.append(new_attribute_in_one_iteration)
    # 然后找相关属性，entity_attribute_list里找相关变量的VAR
    eal = {}
    # 逻辑上相关的用于谓词，不用物理相关的
    logically_eal = {}
    for round_list in related_attribute:
        for j in round_list:
            for key, value in entity_attribute_list.items():
                if key == j:
                    eal.update({key: value})
                    logically_eal.update({key: value})
                    break

    if 'home.mode' in entity_rule_list:
        logically_eal.update({'home.mode': ['away', 'home']})

    # 如果安全属性里不包含数值抽象，则排除此类数值谓词
    print('property_related_attribute')
    print(property_related_attribute)
    #print(logically_eal)
    if not set(property_related_attribute).intersection(NUMBER_ABSTRACT):
        for na in NUMBER_ABSTRACT:
            if na in logically_eal:
                logically_eal.pop(na)
    #print(logically_eal)

    # implicit phsical effect
    total_attribute = []
    for key, value in entity_attribute_list.items():
        total_attribute.append(key)
    current_attribute = []
    for key, value in eal.items():
        current_attribute.append(key)
    implicit = []
    for name, value in eal.items():
        for cb in CHANNEL_INTERACTION_CONFIG_LIST:
            if name == cb.name:
                # 只考虑温度
                if name == 'temperatureMeasurement.temperature':
                    for i in cb.config_list:
                        # 并且存在于当前系统
                        ele = i[0].replace(' ', '')
                        ele_name = ele.split('=')[0]
                        #print('ele_name')
                        #print(ele_name)
                        # 在全集但是不在当前规则
                        if ele != 'not_handle' and ele_name in total_attribute and ele_name not in current_attribute:
                            implicit.append(ele_name)
                    break
    #print('更新前')
    #print(eal)

    # 根据implicit更新eal
    for i in implicit:
            for key, value in entity_attribute_list.items():
                if key == i:
                    eal.update({key: value})
                    break
    #print('更新后')
    #print(implicit)
    #print(eal)

    #print('规则更新前')
    #print(erl)
    # 根据implicit更新erl，并补充新属性
    new_attribute = []
    for i in implicit:
        for entity_attribute, tap_set in entity_rule_list.items():
                if entity_attribute == i:
                    erl.update({entity_attribute: tap_set})
                    new_attribute = analyze_predicate(entity_attribute, tap_set)
    current_attribute = []
    for key, value in eal.items():
        current_attribute.append(key)
    update_attribute = []
    for i in new_attribute:
        if i in total_attribute and i not in current_attribute:
            for key, value in entity_attribute_list.items():
                if key == i:
                    update_attribute.append(key)
                    eal.update({key: value})
                    break
            break
    #print('规则更新后')
    #print(erl)
    #print('再次更新属性后')
    #print(update_attribute)
    #print(eal)

    # 递归终点
    #if implicit == [] and update_attribute == []:
    #print('筛选后的建模设备和规则如下：')
    #print(eal)
    #print(erl)
    #print(entity_attribute_list)
    # 加入condition和trigger中的设备
    for entity_attribute, tap_set in erl.items():
        for single_rule in tap_set:
            if len(single_rule) == 4:
                #print('6666666666666')
                # 更新trigger
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
                entity_name = trigger.split(sign)[0].replace('\n', '').replace('\r', '').replace(' ', '')
                #print(entity_name)
                if entity_name not in eal:
                    for key, value in entity_attribute_list.items():
                        if key == entity_name:
                            eal.update({entity_name: value})
                            break
                if single_rule[1][0] != 'none':
                    for single_condition in single_rule[1]:
                        # 返回string中所有与pattern匹配的全部字符串,返回形式为数组。返回>=
                            sign = ''
                            if '>=' in single_condition:
                                sign = '>='
                            elif '<=' in single_condition:
                                sign = '<='
                            elif '<' in single_condition:
                                sign = '<'
                            elif '>' in single_condition:
                                sign = '>'
                            elif '=' in single_condition:
                                sign = '='
                            print(single_rule)
                            print(single_condition)
                            entity_name = single_condition.split(sign)[0].replace('\n', '').replace('\r', '').replace(' ', '')
                            print(entity_name)
                            if entity_name not in eal:
                                for key, value in entity_attribute_list.items():
                                    if key == entity_name:
                                        eal.update({entity_name: value})
                                        break

    #print('筛选后的建模设备和规则如下：')
    #print(eal)
    #print(erl)

    return eal, erl, logically_eal, logically_erl

    #return estimate_related(eal, erl, property_related_attribute)


# {window.switch : [0] 规则1有延迟，[]空规则2无延迟}
def estimate_runin(entity_rule_list):
    # 存在延时action，记录数组下标，下标为延时属性
    res = {}
    for entity_attribute, tap_set in entity_rule_list.items():
        tap_amount = len(tap_set)
        # 一个循环处理同设备能力多条规则的一条
        total_res = []
        for i in range(tap_amount):
            # value[i]对应一条规则
            single_rule = tap_set[i]
            single_res = []
            # [['smoke=detected'], ['none'], ['open', 'close'], [5, 0, 'none']]的[5,0]
            single_rule_delay = single_rule[-1]
            for j in range(len(single_rule_delay)):
                # 数字类型且大于0
                if type(single_rule_delay[j]) == type(1) and single_rule[-1][j] > 0:
                    single_res.append(j)
            total_res.append(single_res)
        if total_res:
            res.update({entity_attribute: total_res})
    '''entity_attribute:[[],[1,5]]'''
    # print('estimate_runin')
    # print(res)
    return res

def estimate_wait_trigger(entity_rule_list):
    # 存在延时action，记录数组下标，下标为延时属性
    res = {}
    for entity_attribute, tap_set in entity_rule_list.items():
        tap_amount = len(tap_set)
        # 一个循环处理同设备能力多条规则的一条
        total_res = []
        for i in range(tap_amount):
            # value[i]对应一条规则
            single_rule = tap_set[i]
            single_res = []
            # [['smoke=detected'], ['none'], ['open', 'close'], [5, 0]]的[5,0]
            single_rule_delay = single_rule[-1]
            for j in range(len(single_rule_delay)):
                if type(single_rule_delay[j]) == type('1') and 'wait_trigger' in single_rule_delay[j]:
                    single_res.append(single_rule_delay[j].replace('wait_trigger', '').replace(' ', ''))
            total_res.append(single_res)
        if total_res:
            res.update({entity_attribute: total_res})
    '''entity_attribute:[[],[1,5]]'''
    # print('estimate_runin')
    # print(res)
    return res


def estimate_trigger_delay(entity_rule_list):
    # 存在延时action，记录数组下标，下标为延时属性
    res = {}
    for entity_attribute, tap_set in entity_rule_list.items():
        tap_amount = len(tap_set)
        # 一个循环处理同设备能力多条规则的一条
        total_res = []
        for i in range(tap_amount):
            # value[i]对应一条规则
            single_rule = tap_set[i]
            single_res = []
            # [['smoke=detected'], ['none'], ['open', 'close'], [5, 0]]的[5,0]
            single_rule_delay = single_rule[-1]
            for j in range(len(single_rule_delay)):
                if type(single_rule_delay[j]) == type('1') and 'trigger_delay' in single_rule_delay[j]:
                    single_res.append(single_rule[0][0] + ' ' + single_rule_delay[j].replace('trigger_delay', '').replace(' ', ''))
            total_res.append(single_res)
        if total_res:
            res.update({entity_attribute: total_res})
    '''entity_attribute:[[],[1,5]]'''
    # print('estimate_runin')
    # print(res)
    return res



class ModelBuilder(object):
    ID = 0

    def __init__(self, entity_attribute_list, entity_rule_list, spec):
        # 筛选相关的，以property建模
        self.entity_attribute_list, self.entity_rule_list = entity_attribute_list, entity_rule_list
        self.extended_attribute_list = []
        self.wait_trigger_record = []
        self.trigger_delay_record = []
        self.smv_text = ''
        self.all_attribute_dic = {}
        self.__class__.ID += 1
        self.spec = spec[0]
        self.violating_type = spec[1]
        # index
        self.extended_action_index = estimate_runin(self.entity_rule_list)
        self.wait_trigger_list = estimate_wait_trigger(self.entity_rule_list)
        self.trigger_delay_list = estimate_trigger_delay(self.entity_rule_list)
        #print('wait_trigger')
        #print(self.wait_trigger_list)

    def get_var_value(self, var):
        for key, value in self.entity_attribute_list.items():
            VAR_text = ''
            if key == var:
                if type(value) == list:
                    # 头，中间，尾
                    VAR_text = '{'
                    for i in value:
                        if i != value[-1]:
                            VAR_text = VAR_text + str(i) + ','
                        else:
                            VAR_text = VAR_text + str(i)
                    VAR_text = VAR_text + '}'
                # 数值类型 0..5  布尔类型 boolean
                elif '..' in value or value == 'boolean':
                    VAR_text = VAR_text + value
                break
        return VAR_text

    def __EXTENDED_ENVIROMENT_ASSIGN(self, enviroment_var, enviroment_count, value):
        category = ''
        # 应该只找CHANNEL_INTERACTION_CONFIG_LIST和目前属性的交集 交集 交集
        for cb in CHANNEL_INTERACTION_CONFIG_LIST:
            if enviroment_var == cb.name:
                if len(cb.threshold) == 2:
                    category += 'one'
                elif len(cb.threshold) == 4:
                    category += 'two'
                break

        # if 不在CHANNEL_INTERACTION_CONFIG_LIST里，如rain
        # channel-based interaction 的threshold不变
        exist_flag = 0
        for cb in CHANNEL_INTERACTION_CONFIG_LIST:
            if enviroment_var == cb.name:
                exist_flag = 1
                break
        # rain由count自然变化
        if not exist_flag:
            s = '''     init(%s):=1;
     next(%s):=
       case
         next(%s)!=%s & %s =0: 1;
         %s = 1: 0;
         TRUE: %s;
       esac;

     next(%s):=
       case
         %s = 1: %s;
         %s = 0: %s;
         TRUE: %s;
       esac;\n\n''' % (
                enviroment_count, enviroment_count, enviroment_var, enviroment_var, enviroment_count, enviroment_count,
                enviroment_count, enviroment_var, enviroment_count, enviroment_var, enviroment_count, value,
                enviroment_var)
            return s
        else:
            v1 = ''
            v2 = self.get_var_value(enviroment_var)
            # 等于不安全状态
            for key, v in CHANNEL_INTERACTION_CONFIG_DICT.items():
                if key == enviroment_var:
                    v1 = v
                    break
            # 排除不安全后的安全状态，list枚举类型达到阈值后切换为安全状态
            if '{' in v2:
                for i in v2.replace(' ', '').replace('{', '').replace('}', '').split(','):
                    if v1 != i:
                        v2 = i
                        break
            # 如果是温度类型，则达到阈值加一
            # 但是存在超过阈值问题
            elif '..' in v2:
                v2 = enviroment_var + '+1'
            s = ''
            if category == 'one':
                s = '''     init(%s):=1;
         next(%s):=
              case
                next(%s)!=%s & %s =0: 1;
                %s = 1: 0;
                TRUE: %s;
              esac;
    
         next(%s):=
              case
                %s>=0 & %s<%s: %s;
                %s>=%s: %s;
                --因为顺序执行，所以下面肯定是smoke_clear=-1
                %s = 1: %s;
                %s = 0: %s;
                TRUE: %s;
              esac;\n\n''' % (
                    enviroment_count, enviroment_count, enviroment_var, enviroment_var, enviroment_count, enviroment_count,
                    enviroment_count, enviroment_var,
                    enviroment_var + '_CONFIG', enviroment_var + '_CONFIG', enviroment_var + '_threshold', v1,
                    enviroment_var + '_CONFIG', enviroment_var + '_threshold', v2,
                    enviroment_count, enviroment_var, enviroment_count, value, enviroment_var)
            elif category == 'two':
                l = self.get_var_value(enviroment_var).split('..')
                upper = l[1]
                down = l[0]
                s = '''     next(%s):=
         case
           -- 如果在threshold范围内，则温度不变
           %s<%s & %s>%s: %s;
           %s>=%s & %s<=%s: %s;
           %s<=%s & %s>=%s: %s;
           TRUE: %s;
         esac;\n\n''' % (enviroment_var, enviroment_var + '_CONFIG', enviroment_var + '_rise_threshold',
                    enviroment_var + '_CONFIG', enviroment_var + '_drop_threshold', enviroment_var,
                    enviroment_var + '_CONFIG', enviroment_var + '_rise_threshold', enviroment_var + ' + ' + str(CHANNEL_INTERACTION_CONFIG_PER_TIME[enviroment_var]), upper, enviroment_var + ' + ' + str(CHANNEL_INTERACTION_CONFIG_PER_TIME[enviroment_var]),
                    enviroment_var + '_CONFIG', enviroment_var + '_drop_threshold', enviroment_var + ' - ' + str(CHANNEL_INTERACTION_CONFIG_PER_TIME[enviroment_var]), down, enviroment_var + ' - ' + str(CHANNEL_INTERACTION_CONFIG_PER_TIME[enviroment_var]),
                    enviroment_var)
            # 加入smoke_CONFIG
            s = s + generate_channel_based_config(enviroment_var, self.entity_attribute_list)
            return s

    def __Delay(self, name1, upper_limit, name2, trigger_condition):
        s = '''     init(%s) := 0;
     next(%s) :=
            case
                %s: %s;
                %s.timer = 1: 0;
                TRUE: %s;
            esac;\n\n''' % (name1, name1, trigger_condition, upper_limit, name2, name1)
        return s

    def __Extended_rule_flag_ASSIGN(self, name1, name2, trigger_condition):
        s = '''     init(%s) := 0;
     next(%s) :=
            case
                %s: 1;
                %s.timer = 1: 0;
                TRUE: %s;
            esac;\n\n''' % (name1, name1, trigger_condition, name2, name1)
        return s

    def build_INVAR(self):
        VAR_text = ''
        # '   INVAR\n'
        for key, value in self.entity_attribute_list.items():
            # channel-based interaction config
            for cb in CHANNEL_INTERACTION_CONFIG_LIST:
                if key == cb.name:
                    for i in cb.config_list:
                        attribute = i[0].split('=')[0].replace(' ', '')
                        # assign_value = i[0].split('=')[1].replace(' ', '')
                        config = i[1]
                        # 如果为最后的Not_handle
                        if attribute == 'not_handle':
                            if config > 0:
                                VAR_text = VAR_text + '   INVAR\n     ' + key + '_not_handle_config = ' + str(
                                    config) + '\n'
                            else:
                                VAR_text = VAR_text + '   INVAR\n     ' + key + '_not_handle_config = ' + str(
                                    config) + '\n'
                            continue
                        # 只加入和当前属性相关的
                        if attribute in self.entity_attribute_list:
                            if config > 0:
                                VAR_text = VAR_text + '   INVAR\n     ' + key + '_' + attribute + '_config = ' + str(
                                    config) + '\n'
                            else:
                                VAR_text = VAR_text + '   INVAR\n     ' + key + '_' + attribute + '_config = ' + str(
                                    config) + '\n'
                    break

        return VAR_text

    def build_VAR(self):
        VAR_text = '   VAR\n'
        for key, value in self.entity_attribute_list.items():
            # 枚举类型 [0,1,2] [on,off]
            if type(value) == list:
                # 头，中间，尾
                VAR_text = VAR_text + '     ' + key + ':{'
                for i in value:
                    if i != value[-1]:
                        VAR_text = VAR_text + str(i) + ','
                    else:
                        VAR_text = VAR_text + str(i)
                VAR_text = VAR_text + '};\n'
                # 上一状态
                VAR_text = VAR_text + '     ' + key + LAST_STATE + ':{'
                for i in value:
                    # 最后一个不加,
                    if i != value[-1]:
                        VAR_text = VAR_text + str(i) + ','
                    else:
                        VAR_text = VAR_text + str(i)
                VAR_text = VAR_text + '};\n'
            # 数值类型 0..5  布尔类型 boolean
            elif '..' in value or value == 'boolean':
                VAR_text = VAR_text + '     ' + key + ':' + value + ';\n'
                # 上一状态
                VAR_text = VAR_text + '     ' + key + LAST_STATE + ':' + value + ';\n'
            # 自然延时属性
            if key in EXTENDED_ENVIRONMENT:
                VAR_text = VAR_text + '     ' + key + ENVIRONMENT_COUNT + ':0..1;\n'
            # channel-based interaction config
            for cb in CHANNEL_INTERACTION_CONFIG_LIST:
                if key == cb.name:
                    category = ''
                    if len(cb.threshold) == 2:
                        category += 'one'
                    elif len(cb.threshold) == 4:
                        category += 'two'
                    if category == 'one':
                        VAR_text = VAR_text + '     ' + key + '_CONFIG:-1..' + str(cb.threshold[1]) + ';\n'
                        VAR_text = VAR_text + '     ' + key + '_threshold:' + str(cb.threshold[0]) + '..' + str(cb.threshold[1]) + ';\n'
                    elif category == 'two':
                        VAR_text = VAR_text + '     ' + key + '_CONFIG:' + str(cb.threshold[2]) + '..' + str(cb.threshold[1]) + ';\n'
                        VAR_text = VAR_text + '     ' + key + '_rise_threshold:' + str(cb.threshold[0]) + '..' + str(cb.threshold[1]) + ';\n'
                        VAR_text = VAR_text + '     ' + key + '_drop_threshold:' + str(cb.threshold[2]) + '..' + str(cb.threshold[3]) + ';\n'
                    for i in cb.config_list:
                        attribute = i[0].split('=')[0].replace(' ', '')
                        # assign_value = i[0].split('=')[1].replace(' ', '')
                        config = i[1]
                        # 如果为最后的Not_handle
                        if attribute == 'not_handle':
                            if config > 0:
                                VAR_text = VAR_text + '     ' + key + '_not_handle_config:0..' + str(config) + ';\n'
                            else:
                                VAR_text = VAR_text + '     ' + key + '_not_handle_config:' + str(config) + '..0;\n'
                            continue
                        # 只加入和当前属性相关的
                        if attribute in self.entity_attribute_list:
                            if config > 0:
                                VAR_text = VAR_text + '     ' + key + '_' + attribute + '_config:' + str(config) + '..' \
                                           + str(config) + ';\n'
                            else:
                                VAR_text = VAR_text + '     ' + key + '_' + attribute + '_config:' + str(config) + '..' \
                                + str(config) + ';\n'
                    break

        # 延时多加变量
        for entity_attribute, total_index in self.extended_action_index.items():
            '''entity_attribute:[[],[1,5]]'''
            # entity_attribute: [[[trigger1,trigger2],condition,[action1,action2],[time1,time2,0,5,-1]] , rule2 ]
            tap_amount = len(total_index)
            for i in range(tap_amount):
                single_index = total_index[i]
                # 如果该规则无延时则跳过
                if single_index == []:
                    continue
                # 当前属性需要处理的单条规则
                tap_set = self.entity_rule_list[entity_attribute]
                single_rule = tap_set[i]
                single_rule_actionSet = single_rule[2]
                single_rule_delaySet = single_rule[3]
                for j in single_index:
                    # 添加delaywindow: 0..5;
                    name1 = ''
                    # 纯延时类的
                    if 'none' in single_rule_actionSet:
                        name1 += 'delay_' + entity_attribute + '_' + 'none' + '_' + str(i)
                    else:
                        name1 += 'delay_' + entity_attribute + '_' + single_rule_actionSet[j] + '_' + str(i)
                    VAR_text = VAR_text + '     ' + name1 + ':' + '0..' + str(single_rule_delaySet[j]) + ';\n'
                    # 添加runinwindow: RUNIN(delaywindow);
                    name2 = ''
                    # delay在trigger和condition的情况
                    if 'none' in single_rule_actionSet:
                        name2 += 'runin_' + entity_attribute + '_' + 'none' + '_' + str(i)
                    # delay在action的情况
                    else:
                        name2 += 'runin_' + entity_attribute + '_' + single_rule_actionSet[j] + '_' + str(i)
                    VAR_text = VAR_text + '     ' + name2 + ':' + 'RUNIN(' + name1 + ');\n'
                    # 添加延时属性变量
                    #rule_flag_string = 'extended_rule_FLAG_' + entity_attribute + '_' + single_rule_actionSet[j] + '_' + str(i)
                    #VAR_text = VAR_text + '     ' + rule_flag_string + ':' + '{0,1};\n'
                    self.extended_attribute_list.append((name1, str(single_rule_delaySet[j]), name2, entity_attribute))

        # wait_trigger类型
        #print('self.wait_trigger_list')
        #print(self.wait_trigger_list)
        #print('self.extended_action_index')
        #print(self.extended_action_index)
        for entity_attribute, total_index in self.wait_trigger_list.items():
            '''entity_attribute:[[],[2]]'''
            # entity_attribute: [[[trigger1,trigger2],condition,[action1,action2],[time1,time2,0,5,-1]] , rule2 ]
            tap_amount = len(total_index)
            for i in range(tap_amount):
                single_index = total_index[i]
                # 如果该规则无wait_trigger则跳过
                if single_index == []:
                    continue
                # i是第几条规则
                # 当前属性需要处理的单条规则
                tap_set = self.entity_rule_list[entity_attribute]
                single_rule = tap_set[i]
                VAR_text = VAR_text + '     %s_wait_trigger_flag%d:{-1,0,1};\n' % (entity_attribute, i)
                self.wait_trigger_record.append(['%s_wait_trigger_flag%d' % (entity_attribute, i), single_index])

        for entity_attribute, total_index in self.trigger_delay_list.items():
            '''entity_attribute:[[],[2]]'''
            # entity_attribute: [[[trigger1,trigger2],condition,[action1,action2],[time1,time2,0,5,-1]] , rule2 ]
            print('self.trigger_delay_list')
            print(self.trigger_delay_list)
            tap_amount = len(total_index)
            for i in range(tap_amount):
                single_index = total_index[i]
                # 如果该规则无wait_trigger则跳过
                if single_index == []:
                    continue
                # i是第几条规则
                # 当前属性需要处理的单条规则
                tap_set = self.entity_rule_list[entity_attribute]
                single_rule = tap_set[i]

                VAR_text = VAR_text + '     %s_trigger_delay%d:-1..%s;\n' % (entity_attribute, i, single_index[0].split(' ')[1])
                self.trigger_delay_record.append(['%s_trigger_delay%d' % (entity_attribute, i), single_index])
            print('self.trigger_delay_record')
            print(self.trigger_delay_record)

        # 函数类型不用，因为ASSISGN在定义的函数MODULE里
        return VAR_text

    def __build_ASSIGN(self):
        ASSIGN_text = '   ASSIGN\n'

        # 非延时自然属性
        #for i in AFFECTED_IMMEDIATE_ENVIRONMENT:



        # 处理延时自然属性
        for i in EXTENDED_ENVIRONMENT:
            # 只处理相关的自然属性
            for key, value in self.entity_attribute_list.items():
                if i == key:
                    ASSIGN_text = ASSIGN_text + self.__EXTENDED_ENVIROMENT_ASSIGN(i, i + ENVIRONMENT_COUNT,
                                                                                  self.get_var_value(i))
                    break

        # channel-based interaction 的threshold不变
        for key, value in self.entity_attribute_list.items():
            for cb in CHANNEL_INTERACTION_CONFIG_LIST:
                if key == cb.name:
                    category = ''
                    if len(cb.threshold) == 2:
                        category += 'one'
                    elif len(cb.threshold) == 4:
                        category += 'two'
                    if category == 'one':
                        ASSIGN_text = ASSIGN_text + '      next(' + key + '_threshold):=' + key + '_threshold' + ';\n\n'
                    elif category == 'two':
                        ASSIGN_text = ASSIGN_text + '      next(' + key + '_rise_threshold):=' + key + '_rise_threshold' + ';\n\n'
                        ASSIGN_text = ASSIGN_text + '      next(' + key + '_drop_threshold):=' + key + '_drop_threshold' + ';\n\n'
                    break

        # 处理last变量的init，和属性里的取值反着来，确保第一个状态能触发
        spec_info_list = find_info_in_spec(self.violating_type, self.spec)
        front_attribute = spec_info_list[0]
        front_attribute_value = spec_info_list[1]
        end_attribute = spec_info_list[2]
        end_attribute_value = spec_info_list[3]
        #print('self.entity_attribute_list')
        #print(self.entity_attribute_list)
        for key, value in self.entity_attribute_list.items():
            if front_attribute == key:
                if type(value) == type('1'):
                    # value = value.split('..')
                    break
                for i in value:
                    if front_attribute_value != i:
                        ASSIGN_text = ASSIGN_text + '      init(' + front_attribute + LAST_STATE + '):=' + i + ';\n'
                        #print('front_attribute + LAST_STATE')
                        #print(front_attribute + LAST_STATE+ '):=' + i)
                        #print(front_attribute_value)
                        break
            elif end_attribute == key:
                if type(value) == type('1'):
                    # value = value.split('..')
                    break
                for i in value:
                    if end_attribute_value != i:
                        ASSIGN_text = ASSIGN_text + '      init(' + end_attribute + LAST_STATE + '):=' + i + ';\n'
                        #print('end_attribute + LAST_STATE')
                        #print(end_attribute + LAST_STATE+ '):=' + i)
                        #print(end_attribute_value)
                        break

        # 处理属性里没有的值 例如weather的属性没有处理smoke的情况，因为属性里没smoke，所以没他的值
        # 如果属性里有smoke clear，那么这步会直接排除smoke，所以不影响
        l1 = [front_attribute, end_attribute]
        l2 = []
        l3 = []
        for key, value in CHANNEL_INTERACTION_CONFIG_DICT.items():
            l2.append(key)
        for key, value in self.entity_attribute_list.items():
            l3.append(key)
        # 求l2和channel交集得到目前的
        l4 = set(l3).intersection(l2)
        # 求差集，多的要在前
        diff = list(set(l4).difference(l1))
        for ev in diff:
            # print(ev)
            v2 = self.get_var_value(ev)
            # print(v2)
            # 等于不安全状态
            v1 = CHANNEL_INTERACTION_CONFIG_DICT[ev]
            # print(v1)
            # 排除不安全后的安全状态，list枚举类型达到阈值后切换为安全状态
            if '{' in v2:
                for i in v2.replace(' ', '').replace('{', '').replace('}', '').split(','):
                    if v1 != i:
                        v2 = i
                        # print('      init(' + ev + LAST_STATE + '):=' + v2 + ';\n')
                        ASSIGN_text = ASSIGN_text + '      init(' + ev + LAST_STATE + '):=' + v2 + ';\n'
                        #print('ev + LAST_STATE')
                        #print(ev + LAST_STATE + '):=' + v2)
                        break
            # 如果是温度类型，则达到阈值加一
            # 但是存在超过阈值问题
            elif '..' in v2:
                pass
                # v2 = enviroment_var + '+1'
        ASSIGN_text = ASSIGN_text + '\n'

        sensor = ['presenceSensor.presence', 'temperatureMeasurement.temperature', 'smokeDetector.smoke',
                  'carbonMonoxideDetector.carbonMonoxide', 'carbonDioxideMeasurement.carbonDioxide', 'rainSensor.rain',
                  'relativeHumidityMeasurement.humidity']

        # 处理last变量的next
        for key, value in self.entity_attribute_list.items():
            ASSIGN_text = ASSIGN_text + '      next(' + key + LAST_STATE + '):=' + key + ';\n'
        # 常规变量
        for entity_attribute, tap_set in self.entity_rule_list.items():
            if entity_attribute in sensor:
                continue
            tap_amount = len(tap_set)
            # 一个循环处理同设备能力多条规则的一条
            tmp = []  # 处理.timer，延时
            s1, s2, s3 = '', '', ''
            s1 = s1 + '    next(' + entity_attribute + '):=\n          case\n'
            count = -1
            for i in range(tap_amount):
                count += 1
                # tap_set[i]对应一条规则
                single_rule = tap_set[i]
                ''''fan.switchCap.switch': [[['smoke=detected'],['none'],['on','off'],[5,0]] , [['presenceSensor=present'],['none'],['on','off'],[3,0]] , [['waterSensor=wet'],['none'],['on','off'],[3,0]]]}'''
                # trigger
                trigger = '             '
                # 处理多trigger的循环
                for j in single_rule[0]:
                    sign = ''
                    if '>=' in j:
                        sign = '>='
                    elif '<=' in j:
                        sign = '<='
                    elif '<' in j:
                        sign = '<'
                    elif '>' in j:
                        sign = '>'
                    elif '=' in j:
                        sign = '='
                    # 处理trigger_delay 如温度高于20度持续了20min
                    j_name = j.split(sign)[0]
                    j_attribute = j.split(sign)[1]
                    trigger_delay_flag = 0
                    trigger_delay_flag_str = ''
                    trigger_delay_flag_cnt = ''
                    # [['heater.switch_trigger_delay1', ['temperatureMeasurement.temperature>25 5']]]
                    for ele in self.trigger_delay_record:
                        # 是对应的规则
                        if entity_attribute == ele[0].split('_')[0] and str(count) == ele[0].split('_')[-1][-1]:
                            #print('exist')
                            #print(entity_attribute)
                            #print(count)
                            #print(j_name)
                            #print(ele[1][0].split(' ')[0])
                            # 且是对应的trigger
                            #if j_name == ele[1][0].split(' ')[0]:
                                trigger_delay_flag_str += ele[0]
                                trigger_delay_flag = 1
                                trigger_delay_flag_cnt += ele[1][0].split(' ')[1]
                                break
                    if trigger_delay_flag:
                        trigger = '             next(' + trigger_delay_flag_str + ')=%s' % trigger_delay_flag_cnt
                        continue
                    # 第一个trigger特殊处理一下
                    elif sign == '=':
                        trigger = trigger + j
                        # 体现trigger的跳变last
                        trigger = trigger + '&' + j_name + '!=' + j_name + LAST_STATE
                        continue
                    else:
                        if '<' in sign:
                            # 使用last变量体现trigger
                            trigger = trigger + j_name + '=' + str(int(j_attribute) - CHANNEL_INTERACTION_CONFIG_PER_TIME[j_name])
                            # 体现trigger的跳变last
                            trigger = trigger + '&' + j_name + '!=' + j_name + LAST_STATE + '&' + j_name + LAST_STATE + '=' + j_attribute
                            continue
                        elif '>' in sign:
                            # 使用last变量体现trigger
                            trigger = trigger + j_name + '=' + str(int(j_attribute) + CHANNEL_INTERACTION_CONFIG_PER_TIME[j_name])
                            # 体现trigger的跳变last
                            trigger = trigger + '&' + j_name + '!=' + j_name + LAST_STATE + '&' + j_name + LAST_STATE + '=' + j_attribute
                            continue

                # 处理多condition的循环
                condition = ''
                first_flag = 1
                for j in list(set(single_rule[1])):
                    if first_flag:
                        first_flag = 0
                        condition = condition + j
                        continue
                    condition = condition + '&' + j

                # 处理action
                action = single_rule[2][0]
                # 如果为AFTER类延时，不加t,c
                if action == 'none':
                    s1 = s1 + ''
                else:
                    # condition为空的情况
                    if single_rule[1][0] != 'none':
                        s1 = s1 + trigger + '&' + condition + ':' + action + ';\n'
                        print('wrong')
                        print(trigger + '&' + condition + ':' + action + ';\n')
                        print(single_rule)
                    else:
                        s1 = s1 + trigger + ':' + action + ';\n'

                # 处理TRUE
                # 处理延迟
                if single_rule[1][0] != 'none':
                    trigger_condition = trigger + '&' + condition  # trigger_condition + trigger + '&' + condition
                else:
                    trigger_condition = trigger
                # 要对应着延迟才处理
                for k in self.extended_attribute_list:
                    name1 = k[0]
                    upper_limit = k[1]
                    name2 = k[2]
                    single_rule_actionSet = single_rule[2]
                    # delay
                    string = ''
                    # 如果不为呆延时
                    if single_rule_actionSet[0] != 'none':
                        string += 'delay_' + entity_attribute + '_' + single_rule_actionSet[0] + '_' + str(i)
                    else:
                        string += 'delay_' + entity_attribute + '_' + 'none' + '_' + str(i)

                    # 延时规则的flag
                    rule_flag_string = 'extended_rule_FLAG_' + entity_attribute + '_' + single_rule_actionSet[0] + '_' + str(i)
                    if name1 == string:
                        s2 = s2 + self.__Delay(name1, upper_limit, name2,
                                               trigger_condition.replace(' ', '').replace('    ', ''))
                        # s2 = s2 + self.__Extended_rule_flag_ASSIGN(rule_flag_string, name2, trigger_condition.replace(' ', '').replace('    ', ''))
                # 处理到点关机
                extended_attribute_cnt = -1
                #print('self.extended_attribute_list')
                #print(self.extended_attribute_list)
                for k in self.extended_attribute_list:
                    extended_attribute_cnt += 1
                    name2 = k[2]
                    # entity_attribute = k[3]
                    single_rule_actionSet = single_rule[2]
                    string = ''
                    if single_rule_actionSet[0] != 'none':
                        string += 'runin_' + entity_attribute + '_' + single_rule_actionSet[0] + '_' + str(i)
                    else:
                        string += 'runin_' + entity_attribute + '_' + 'none' + '_' + str(i)
                    if name2 == string:
                        # 如果为wait_trigger
                        wtr_ele_list = []
                        for wtr_ele in self.wait_trigger_record:
                            wtr_ele_list.append(wtr_ele[0])
                        if ('%s_wait_trigger_flag%d' % (entity_attribute, i)) in wtr_ele_list:
                            # 抽象对应的一条规则
                            s3 = s3 + '             next(%s_wait_trigger_flag%d)=0:' % (entity_attribute, i) + single_rule_actionSet[1] + ';\n'
                        else:
                            # runinfan_smoke.timer=1&fan.switchCap.switch=on: off;
                            if single_rule_actionSet[0] != 'none':
                                s3 = s3 + '             ' + name2 + '.timer=1 & ' + entity_attribute + '=' + \
                                     single_rule_actionSet[0] + ':' + single_rule_actionSet[1] + ';\n'
                            else:
                                # 借鉴处理last变量的init
                                none_action = '('
                                for key, value in self.entity_attribute_list.items():
                                    if entity_attribute == key:
                                        for ii in value:
                                            if ii != single_rule_actionSet[1]:
                                                none_action += entity_attribute + '=' + ii + '|'
                                        break
                                none_action = none_action[:-1] + ')'
                                s3 = s3 + '             ' + name2 + '.timer=1 & ' + \
                                     none_action + ':' + single_rule_actionSet[1] + ';\n'


            s3 = s3 + '             TRUE:' + entity_attribute + ';\n          esac;\n'
            ASSIGN_text = ASSIGN_text + s2
            ASSIGN_text = ASSIGN_text + s1
            ASSIGN_text = ASSIGN_text + s3

            # wait_trigger_FLAG赋值
            #'self.wait_trigger_record')
            #print(self.wait_trigger_record)
            # self.wait_trigger_record记录了wait_trigger在第几条规则
            for j in self.wait_trigger_record:
                # wait_trigger_FLAG赋值 fan on 不一定要有
                #             runin_fan.switch_on_1.timer=1 & fan.switch=on & smokeDetector.smoke=detected:1;
                #             runin_fan.switch_on_1.timer=1 & fan.switch=on & smokeDetector.smoke=clear:0;
                #             wait_trigger_FLAG=1 & smokeDetector.smoke=clear:0;
                # (name1, str(single_rule_delaySet[j]), name2, entity_attribute)

                # bug出在extended只记录延时规则，而j是action为entity attribute的第几条规则，不看延时
                # 只针对有延时的做wait_trigger，所以直接匹配对应的延迟
                j_attribute = j[0].split('_')[0]
                j_cnt = j[0].split('_')[-1][-1]
                j_trigger = j[1][0]
                sign = ''
                if '>=' in j_trigger:
                    sign = '>='
                elif '<=' in j_trigger:
                    sign = '<='
                elif '<' in j_trigger:
                    sign = '<'
                elif '>' in j_trigger:
                    sign = '>'
                elif '=' in j_trigger:
                    sign = '='
                j_trigger_attribute = j_trigger.split(sign)[0]
                j_trigger_attribute_value = j_trigger.split(sign)[1]
                # 找到j_trigger的差集
                different_list = []
                different_str = '('
                for key, value in self.entity_attribute_list.items():
                    if j_trigger_attribute == key:
                        #print('j_trigger_attribute')
                        #print(j_trigger_attribute)
                        #print(value)
                        for v in value:
                            if j_trigger_attribute_value != v:
                                different_list.append(v)
                        different_list_len = len(different_list)
                        for v in range(different_list_len):
                            if (different_list_len > 1 and v == different_list_len - 1) or (different_list_len == 1):
                                different_str += j_trigger_attribute + '=' + different_list[v]
                            else:
                                different_str += j_trigger_attribute + '=' + different_list[v] + '|'
                        different_str += ')'
                        break

                for eal_ele in self.extended_attribute_list:
                    eal_list = eal_ele[0].split('_')
                    eal_attribute = eal_list[1]
                    eal_cnt = eal_list[-1]
                    # attribute匹配，并且
                    if eal_attribute == j_attribute and int(eal_cnt) == int(j_cnt):
                        corresponding_info = eal_ele
                        runin_name = corresponding_info[2]
                        print('different_str')
                        print(different_str)
                        wait_trigger_str = '''\n    init(%s_wait_trigger_flag%s):=-1;
            next(%s_wait_trigger_flag%s):=
                  case
                    %s.timer=1 & %s:1;
                    %s.timer=1 & %s:0;
                    %s_wait_trigger_flag%s=1 & %s:0;
                    %s_wait_trigger_flag%s=0:-1;
                    TRUE:%s_wait_trigger_flag%s;
                  esac;\n''' % (j_attribute, j_cnt, j_attribute, j_cnt,
                            runin_name, j_trigger,
                            runin_name, different_str,
                            j_attribute, j_cnt, different_str,
                            j_attribute, j_cnt,
                            j_attribute, j_cnt)
                        if 'init(%s_wait_trigger_flag%s)' % (j_attribute, j_cnt) not in ASSIGN_text:
                            ASSIGN_text = ASSIGN_text + wait_trigger_str
                            print(wait_trigger_str)
                            break

        ASSIGN_text = ASSIGN_text + assign_trigger_delay(self.trigger_delay_record, self.entity_attribute_list)

        return ASSIGN_text


    def build_model(self, property_cnt):
        curr_dir = os.getcwd()
        MODULE_RUNIN = module_RUNIN(20)
        INVAR_text = self.build_INVAR()
        VAR_text = self.build_VAR()
        ASSIGN_text = self.__build_ASSIGN()
        MOUDLUE_MAIN = 'MODULE main\n' + VAR_text + INVAR_text + ASSIGN_text
        self.smv_text = MODULE_RUNIN + MOUDLUE_MAIN
        file = open(curr_dir + '\smv\property%d\model%d.txt' % (property_cnt, self.__class__.ID), 'w+',
                    encoding='utf-8')
        file.write(self.smv_text)
        file.close()
        # self.build_ASSIGN()
