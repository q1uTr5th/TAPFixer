from CONST import EXTENDED_ENVIRONMENT, LAST_STATE, ENVIRONMENT_COUNT, UNAFFECTED_EXTENDED_ENVIRONMENT, TAB, CHANNEL_INTERACTION_CONFIG_LIST, CHANNEL_INTERACTION_CONFIG_DICT, UNAFFECTED_IMMEDIATE_ENVIRONMENT, CHANNEL_INTERACTION_CONFIG_PER_TIME, NUMBER_ABSTRACT, AFFECTED_IMMEDIATE_ENVIRONMENT
from ModelBuilder import module_RUNIN, estimate_runin, find_info_in_spec, generate_channel_based_config, estimate_wait_trigger, estimate_trigger_delay, assign_trigger_delay
import os
import time
import random
from itertools import combinations
import re

def find_action_in_spec(violating_type, spec):
    if violating_type == 'liveness':
        # r'--LTLSPEC G((smoke=detected)->(X(fan.switchCap.switch = on) & F(runin_fan.switchCap.switch_on_0.timer=1 & fan.switchCap.switch = on)))'
        property_info = spec.replace('--LTLSPEC G(', '').replace('(', '').replace(')', '').replace(' ', '').split('->F')
        end_state_in_property = property_info[1].split('U')[0].split('=')[0]
        end_state_value = property_info[1].split('U')[0].split('=')[1]
        return [end_state_in_property, end_state_value]
    elif violating_type == 'state-event':
        # G((weather.rain = raining)->!X(window.switch = close))  只能处理单event
        # 'weather.rain = raining', 'window.switch = close'
        property_info = spec.replace('--LTLSPEC G(', '').replace('(', '').replace(')', '').replace(' ', '').split('->X')
        sign = ''
        if '>=' in property_info[1]:
            sign = '>='
        elif '<=' in property_info[1]:
            sign = '<='
        elif '<' in property_info[1]:
            sign = '<'
        elif '>' in property_info[1]:
            sign = '>'
        elif '=' in property_info[1]:
            sign = '='
        event_in_property = property_info[1].split(sign)[0]
        event_value = [property_info[1].split(sign)[1]]
        return [event_in_property, event_value]
    elif violating_type == 'state-state':
        property_info = spec.replace('--LTLSPEC G(', '').replace('(', '').replace(')', '').replace(' ', '').split('->')
        sign = ''
        if '>=' in property_info[1]:
            sign = '>='
        elif '<=' in property_info[1]:
            sign = '<='
        elif '<' in property_info[1]:
            sign = '<'
        elif '>' in property_info[1]:
            sign = '>'
        elif '=' in property_info[1]:
            sign = '='
        event_in_property = property_info[1].split(sign)[0]
        event_value = [property_info[1].split(sign)[1]]
        return [event_in_property, event_value]

class ModelAbstractor(object):
    ID = 0
    INVAR_test_list = []
    WAIT_TRIGGER_cnt = -1
    INVAR_new_rule_list = []
    INVAR_delay = []
    original_flag_dic = {}
    new_flag_dic = {}
    NEW_RULE_AMOUNT = 1
    WAIT_TRIGGER_AMOUNT = 0

    def __init__(self, cex_trace, entity_attribute_list, entity_rule_list,
                 violating_state_position, mode, flag_INVAR, round_count, spec, abstract_mode, logically_eal):
        self.__class__.ID += 1
        self.states = cex_trace
        # 取第一个冲突状态，几个里面最大的
        self.upperlimit = violating_state_position[0] + 1
        self.entity_attribute_list, self.entity_rule_list = entity_attribute_list, entity_rule_list
        self.smv_text = ''
        self.extended_attribute_list = []
        self.wait_trigger_record = []
        self.trigger_delay_record = []
        self.flag_original_amount = []
        # 这个是logicall
        self.predicate = []
        self.logicall_and_physical_predicate = self.analyze_logicall_and_physical_predicate()
        self.mode = mode
        self.flag_INVAR = flag_INVAR
        self.round_count = round_count
        # new_rule_amount设置为1，代表每次新增一条
        self.new_rule_amount = self.__class__.NEW_RULE_AMOUNT
        self.spec = spec[0]
        self.violating_type = spec[1]
        self.extended_action_index = estimate_runin(self.entity_rule_list)
        # 安全属性中的
        self.entity_attribute = find_action_in_spec(self.violating_type, self.spec)[0]
        #print('安全属性中的')
        #print(self.entity_attribute)
        self.new_rule_amount_cnt = 0
        self.delay_used_in_abstract = [] # 用于延时抽象
        self.abstract_mode = abstract_mode
        self.wait_trigger_list = estimate_wait_trigger(self.entity_rule_list)
        self.property_entity_delay_rule = []
        self.rule_predicate, self.subtract_predicate = [], []
        self.logicall_eal = logically_eal
        self.number_abstract_candidate = self.number_abstract()
        self.trigger_delay_list = estimate_trigger_delay(self.entity_rule_list)
        # print('self.number_abstract_candidate')
        # print(self.number_abstract_candidate)

    def analyze_logicall_and_physical_predicate(self):
        # 谓词全体就是entity_attribute_list本身
        predicate = []
        # 这里改成逻辑上
        for key, value in self.entity_attribute_list.items():
            predicate.append(key)
        return predicate

    def number_abstract(self):
        # 初始化
        res = {}
        for i in NUMBER_ABSTRACT:
            res.update({i: []})

        # 先取属性里的
        spec_info_list = find_info_in_spec(self.violating_type, self.spec)
        front_attribute = spec_info_list[0]
        front_attribute_value = spec_info_list[1]
        end_attribute = spec_info_list[2]
        end_attribute_value = spec_info_list[3]
        process_flag = 1
        if front_attribute in NUMBER_ABSTRACT:
            center_value = int(front_attribute_value)
            res[front_attribute].append(center_value)
            if process_flag:
                for i in range(1, 2):
                    res[front_attribute].append(center_value + i * CHANNEL_INTERACTION_CONFIG_PER_TIME[front_attribute])
                for i in range(1, 2):
                    res[front_attribute].append(center_value - i * CHANNEL_INTERACTION_CONFIG_PER_TIME[front_attribute])
        if end_attribute in NUMBER_ABSTRACT:
            center_value = int(end_attribute_value)
            res[end_attribute].append(center_value)
            if process_flag:
                for i in range(1, 2):
                    res[end_attribute].append(center_value + i * CHANNEL_INTERACTION_CONFIG_PER_TIME[end_attribute])
                for i in range(1, 2):
                    res[end_attribute].append(center_value - i * CHANNEL_INTERACTION_CONFIG_PER_TIME[end_attribute])

        # 找到属性里的值
        for entity, tap_set in self.entity_rule_list.items():
            for single_rule in tap_set:
                trigger = single_rule[0][0]
                re_pattern = r'[a-zA-Z0-9._]+(.*?)[a-zA-Z0-9._]+'
                # 返回string中所有与pattern匹配的全部字符串,返回形式为数组。返回>=
                compare_sign = re.findall(re_pattern, trigger)[0]
                trigger_name = trigger.split(compare_sign)[0]
                #print('trigger_name')
                #print(trigger_name)

                if trigger_name in NUMBER_ABSTRACT:
                    trigger_value = int(trigger.split(compare_sign)[1])
                    #print(trigger_value)
                    res[trigger_name].append(trigger_value)
                    if process_flag:
                        for i in range(1, 2):
                            res[trigger_name].append(trigger_value + i * CHANNEL_INTERACTION_CONFIG_PER_TIME[trigger_name])
                        for i in range(1, 2):
                            res[trigger_name].append(trigger_value - i * CHANNEL_INTERACTION_CONFIG_PER_TIME[trigger_name])
                condition_set = single_rule[1]
                if condition_set[0] != 'none':
                    for single_condition in condition_set:
                        re_pattern = r'[a-zA-Z0-9._]+(.*?)[a-zA-Z0-9._]+'
                        # 返回string中所有与pattern匹配的全部字符串,返回形式为数组。返回>=
                        compare_sign = re.findall(re_pattern, single_condition)[0]
                        condition_name = single_condition.split(compare_sign)[0]
                        if condition_name in NUMBER_ABSTRACT:
                            condition_value = int(single_condition.split(compare_sign)[1])
                            res[condition_name].append(condition_value)
                            if process_flag:
                                for i in range(1, 2):
                                    res[condition_name].append(condition_value + i * CHANNEL_INTERACTION_CONFIG_PER_TIME[condition_name])
                                for i in range(1, 2):
                                    res[condition_name].append(condition_value - i * CHANNEL_INTERACTION_CONFIG_PER_TIME[condition_name])

        # 字典的value去重
        for key, value in res.items():
            v = list(set(value))
            res.update({key: v})
        #print('res')
        #print(res)
        return res


    def collect_threshold_var(self, mode):
        res = ''
        if mode == 'iteration':
            res = '    INVAR\n    '
            for single_attribute in self.states[0]:
                # 排除wait_trigger_flag，因为不通过flag找
                if 'threshold' in single_attribute:
                    res += single_attribute.replace('\n', '').replace('\r', '') + ' & '
            res = res[:-2] + '\n\n'
        # 第一次
        else:
            res = ''

        if not res.replace(' ', '').replace('INVAR', '').replace('\n', ''):
            return ''
        return res


    # 分析每条规则包含的谓词
    def analyze_predicate(self):
        # 谓词全体就是entity_attribute_list本身
        predicate = []
        # 这里改成逻辑上
        for key, value in self.logicall_eal.items():
            predicate.append(key)

        # 分析和安全属性出现的属性相关的谓词，第一个谓词是next()谓词
        spec_info_list = find_info_in_spec(self.violating_type, self.spec)
        front_attribute = spec_info_list[0]
        front_attribute_value = spec_info_list[1]
        end_attribute = spec_info_list[2]
        end_attribute_value = spec_info_list[3]
        rule_predicate = []
        '''# 首先处理front_attribute，保证有序性方便后续original_flag处理
        for entity_attribute, tap_set in self.entity_rule_list.items():
            if entity_attribute == front_attribute:
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
                        print('j.split(sign)[0].replace()')
                        print(j.split(sign)[0].replace(' ', ''))
                        if j.split(sign)[0].replace(' ', '') in predicate:
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
                            print('j.split(sign)[0].replace()')
                            print(j.split(sign)[0].replace(' ', ''))
                            if j.split(sign)[0].replace(' ', '') in predicate:
                                li.append(j.split(sign)[0].replace(' ', ''))
                    rule_predicate.append(li)'''
        # 之后处理end_attribute
        for entity_attribute, tap_set in self.entity_rule_list.items():
            if entity_attribute == end_attribute:
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
                        print('j.split(sign)[0].replace()')
                        print(j.split(sign)[0].replace(' ', ''))
                        if j.split(sign)[0].replace(' ', '') in predicate:
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
                            print('j.split(sign)[0].replace()')
                            print(j.split(sign)[0].replace(' ', ''))
                            if j.split(sign)[0].replace(' ', '') in predicate:
                                li.append(j.split(sign)[0].replace(' ', ''))
                    rule_predicate.append(li)

        subtract_predicate = []
        for single_rule in rule_predicate:
            subtract = list(set(predicate) ^ set(single_rule))
            subtract_predicate.append(subtract)

        return predicate, rule_predicate, subtract_predicate

    def get_var_value_and_amount(self, var):
        var_amount = 0
        VAR_text = ''
        for key, value in self.entity_attribute_list.items():
            if key == var:
                if type(value) == list:
                    var_amount = len(value)
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
                    # if '..' in value and key in self.number_abstract_candidate:
                    if key in self.number_abstract_candidate:
                        #print('key')
                        #print(key)
                        var_amount = len(self.number_abstract_candidate[key])
                        #print(var_amount)
                    #elif '..' in value:
                    #    var_amount = int(value.split('..')[1]) + abs(int(value.split('..')[0])) + 1
                    else:
                        var_amount = 2
                break
        return VAR_text, var_amount

    def find_assign_before_violating_state(self, attribute_not_rule_related):
        # 之后去反例路径里找冲突状态之前的取值
        # [:self.upperlimit]代表冲突状态之前
        attribute_not_rule_related_dic = {}
        # 一次性找完一个属性的全部取值，所以for在外围
        # not_rule_realated是不受影响的属性如下雨
        for attribute in attribute_not_rule_related:
            value = []
            for state in self.states[:self.upperlimit]:
                for attribute_assign in state:
                    # 避免选到_last等变量
                    if (attribute + ' =') in attribute_assign:
                        # '='不能变
                        value.append(attribute_assign.split('=')[1].replace(' ', ''))
                        break
            attribute_not_rule_related_dic.update({attribute: value})
        return attribute_not_rule_related_dic

    # 多了flag和step、step_upperlimit变量
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
                                VAR_text = VAR_text + '     ' + key + '_not_handle_config:' + str(config) + '..' + str(config) + ';\n'
                            else:
                                VAR_text = VAR_text + '     ' + key + '_not_handle_config:' + str(config) + '..' + str(config) + ';\n'
                            continue
                        # 只加入和当前属性相关的
                        if attribute in self.entity_attribute_list:
                            if config > 0:
                                VAR_text = VAR_text + '     ' + key + '_' + attribute + '_config:' + str(config) + '..' + str(config) + ';\n'
                            else:
                                VAR_text = VAR_text + '     ' + key + '_' + attribute + '_config:' + str(config) + '..' + str(config) + ';\n'
                    break


        # 延时多加变量
        for entity_attribute, total_index in self.extended_action_index.items():
            '''entity_attribute:[[],[1,5]]'''
            # entity_attribute: [[[trigger1,trigger2],condition,[action1,action2],[time1,time2,0,5,-1]] , rule2 ]
            tap_amount = len(total_index)
            for i in range(tap_amount):
                # 如果该规则无延时则跳过
                single_index = total_index[i]
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
                    if 'none' in single_rule_actionSet:
                        name1 += 'delay_' + entity_attribute + '_' + 'none' + '_' + str(i)
                    else:
                        name1 += 'delay_' + entity_attribute + '_' + single_rule_actionSet[j] + '_' + str(i)
                    VAR_text = VAR_text + '     ' + name1 + ':' + '0..' + str(single_rule_delaySet[j]) + ';\n'
                    # 添加runinwindow: RUNIN(delaywindow);
                    name2 = 'runin_' + entity_attribute + '_' + single_rule_actionSet[j] + '_' + str(i)
                    VAR_text = VAR_text + '     ' + name2 + ':' + 'RUNIN(' + name1 + ');\n'
                    # 添加延时属性变量
                    #rule_flag_string = 'extended_rule_FLAG_' + entity_attribute + '_' + single_rule_actionSet[j] + '_' + str(i)
                    #VAR_text = VAR_text + '     ' + rule_flag_string + ':' + '{0,1};\n'
                    # 用于延时抽象
                    self.delay_used_in_abstract.append([name1, str(single_rule_delaySet[j])])
                    self.extended_attribute_list.append((name1, str(single_rule_delaySet[j]), name2, entity_attribute))

        # wait_trigger类型
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

        # 函数类型不用


        # step、step_upperlimit变量
        VAR_text = VAR_text + '     step:0..' + str(self.upperlimit) + ';\n'
        # VAR_text = VAR_text + '     step_upperlimit:0..' + str(self.upperlimit) + ';\n'
        # 抽象原规则的flag
        if [] not in self.flag_original_amount or (len(self.flag_original_amount) != 1):#self.round_count == 1:
            if self.abstract_mode == 'present':
                cnt = -1
                for single_rule in self.flag_original_amount:
                    cnt += 1
                    for single_predicate in single_rule:
                        #print('single_predicate')
                        #print(single_predicate)
                        single_predicate_name = single_predicate[0]
                        # 不抽象数值类
                        if single_predicate_name not in self.number_abstract_candidate:
                            for i in range(single_predicate[1]):
                                # 第一个，属于flag_original的第几个；第二个:entity；第三个：该entity取值范围里的第几个
                                VAR_text = VAR_text + '     original_flag_rule%s_%s_%s:boolean;\n' % (str(cnt), single_predicate[0], str(i))

        # 第二轮迭代加入新规则
        if self.abstract_mode == 'new':
            # 谓词全体就是entity_attribute_list本身
            predicate = []
            for key, value in self.logicall_eal.items():
                predicate.append(key)
            #print('predicate')
            #print(predicate)
            # 排除当前谓词，next(window.switch)
            predicate_without_now_predicate = list(set(predicate) ^ set([self.entity_attribute]))
            predicate_amount = len(predicate_without_now_predicate)
            # 加入single_amount条新规则
            for single_amount in range(self.new_rule_amount):
                # 一个谓词一个triggerflag，加其取值flag
                for i in range(predicate_amount):
                    current_predicate = predicate_without_now_predicate[i]
                    a, c = self.get_var_value_and_amount(current_predicate)
                    # triggerflag
                    VAR_text = VAR_text + '     new_rule%s_%s_triggerflag:boolean;\n' % (str(single_amount), current_predicate)
                    # 取值flag
                    for j in range(c):
                        VAR_text = VAR_text + '     new_rule%s_%s_valueflag%s:boolean;\n' % (str(single_amount), current_predicate, str(j))
                    # 如果为数值类抽象
                    if current_predicate in NUMBER_ABSTRACT and current_predicate in self.logicall_eal:
                        # 一上 一下
                        for j in range(c):
                            for cnt in ['rise', 'drop']:
                                VAR_text = VAR_text + '     new_rule%s_%s_valueflag%s_%s:boolean;\n' % (str(single_amount), current_predicate, str(j), cnt)


        if self.abstract_mode == 'wait_trigger':
            VAR_text = VAR_text + '     wait_trigger_FLAG:{-1,0,1};\n'

        # 第三轮迭抽象延时
        if self.abstract_mode == 'delay':
            for duia in self.delay_used_in_abstract:
                VAR_text = VAR_text + '     ' + duia[0] + '_abstract_flag:{0,' + str(duia[1]) + '};\n'

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

        return VAR_text

    def build_config_INVAR(self):
        VAR_text = ''
        #'   INVAR\n'
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
                                VAR_text = VAR_text + '   INVAR\n     ' + key + '_not_handle_config = ' + str(config) + '\n'
                            else:
                                VAR_text = VAR_text + '   INVAR\n     ' + key + '_not_handle_config = ' + str(config) + '\n'
                            continue
                        # 只加入和当前属性相关的
                        if attribute in self.entity_attribute_list:
                            if config > 0:
                                VAR_text = VAR_text + '   INVAR\n     ' + key + '_' + attribute + '_config = ' + str(config) + '\n'
                            else:
                                VAR_text = VAR_text + '   INVAR\n     ' + key + '_' + attribute + '_config = ' + str(config) + '\n'
                    break

        return VAR_text


    def new_rule_predicate(self):
        trigger_res = []
        value_res = []
        res = '!( '
        # 要排除当前action的谓词
        tmp = list(set(self.predicate) ^ set([self.entity_attribute]))
        for i in tmp:
            trigger_res.append('new_rule0_' + i + '_triggerflag')
            res += 'new_rule0_' + i + '_triggerflag' + '=FALSE & '
            a, c = self.get_var_value_and_amount(i)
            for j in range(c):
                value_res.append('new_rule0_' + i + '_valueflag%d' % j)
                res += 'new_rule0_' + i + '_valueflag%d' % j + '=FALSE & '
        # 去除&
        res = res[:-2]
        res += ')'
        return res


    def exclude_existing_rule(self, abstract_mode):
        existing_rule = []
        for entity_attribute, tap_set in self.entity_rule_list.items():
            # 因为只new当前的
            if entity_attribute == self.entity_attribute:
                tap_amount = len(tap_set)
                # 一个循环处理同设备能力多条规则的一条
                tmp = []  # 处理.timer，延时
                count = -1
                for i in range(tap_amount):
                    count += 1
                    # tap_set[i]对应一条规则 [['smoke=detected'],['none'],['on','off'],[5,0,'none']]
                    # (new_rule0_smokeDetector.smoke_triggerflag)->(smokeDetector.smoke != smokeDetector.smoke_last)) & ((new_rule0_smokeDetector.smoke_valueflag0)
                    single_rule = tap_set[i]
                    # trigger
                    sign = ''
                    t = single_rule[0][0]
                    if '>=' in t:
                        sign = '>='
                    elif '<=' in t:
                        sign = '<='
                    elif '<' in t:
                        sign = '<'
                    elif '>' in t:
                        sign = '>'
                    elif '=' in t:
                        sign = '='
                    trigger_name = single_rule[0][0].split(sign)[0].replace(' ', '')
                    trigger_flag = 'new_rule0_' + trigger_name + '_triggerflag'
                    trigger_var = 0
                    if '<' in sign:
                        trigger_var = int(single_rule[0][0].split(sign)[1].replace(' ', '')) - CHANNEL_INTERACTION_CONFIG_PER_TIME[trigger_name]
                    elif '>' in sign:
                        trigger_var = int(single_rule[0][0].split(sign)[1].replace(' ', '')) + CHANNEL_INTERACTION_CONFIG_PER_TIME[trigger_name]
                    else:
                        trigger_var = single_rule[0][0].split(sign)[1].replace(' ', '')
                    # 获取value flag编号
                    a, c = self.get_var_value_and_amount(trigger_name)
                    trigger_valueflag = ''

                    possible_value = []
                    if 'boolean' in a:
                        possible_value = ['FALSE', 'TRUE']
                    # 数值类的处理有问题
                    elif '..' in a:
                        #lower = int(a.split('..')[0])
                        #upper = int(a.split('..')[1])
                        possible_value = self.number_abstract_candidate[trigger_name]#list(range(lower, upper + 1))
                        #print('possible value')
                        #print(possible_value)
                    elif '{' in a:
                        possible_value = a.replace('{', '').replace('}', '').split(',')

                    #print('trigger_var')
                    #print(type(trigger_var))
                    for j in range(c):
                        if possible_value[j] == trigger_var:
                            #print('trigger_var')
                            #print(trigger_var)
                            trigger_valueflag += 'new_rule0_' + trigger_name + '_valueflag%d' % j
                            break

                    condition_set = single_rule[1]
                    for j in range(len(condition_set)):
                        condition = condition_set[j].replace(' ', '')
                        #print(condition)
                        condition_valueflag = ''
                        possible_value = []
                        if condition != 'none':
                            sign = ''
                            if '>=' in condition:
                                sign = '>='
                            elif '<=' in condition:
                                sign = '<='
                            elif '<' in condition:
                                sign = '<'
                            elif '>' in condition:
                                sign = '>'
                            elif '=' in condition:
                                sign = '='
                            condition_name = condition.split(sign)[0].replace(' ', '')
                            a, c = self.get_var_value_and_amount(condition_name)
                            # condition_var = condition.split(sign)[1].replace(' ', '')
                            condition_var = 0
                            if '<' in sign:
                                condition_var = int(condition.split(sign)[1].replace(' ', '')) - \
                                              CHANNEL_INTERACTION_CONFIG_PER_TIME[condition_name]
                            elif '>' in sign:
                                condition_var = int(condition.split(sign)[1].replace(' ', '')) + \
                                              CHANNEL_INTERACTION_CONFIG_PER_TIME[condition_name]
                            else:
                                condition_var = condition.split(sign)[1].replace(' ', '')
                            if 'boolean' in a:
                                possible_value = ['FALSE', 'TRUE']
                            # 数值类的处理有问题
                            elif '..' in a:
                                #lower = int(a.split('..')[0])
                                #upper = int(a.split('..')[1])
                                possible_value = self.number_abstract_candidate[condition_name]#list(range(lower, upper + 1))
                            elif '{' in a:
                                possible_value = a.replace('{', '').replace('}', '').split(',')
                            #print(possible_value)
                            #print(condition_var)
                            for j in range(c):
                                if possible_value[j] == condition_var:
                                    condition_valueflag += 'new_rule0_' + condition_name + '_valueflag%d' % j
                                    break
                            #action_set = single_rule[2]
                            #latency = single_rule[3]

                    existing_rule.append([trigger_flag, trigger_valueflag, condition_valueflag])#, action_set, latency])
                break
        #print('existing_rule')
        #print(existing_rule)
        # 上述循环已经记录了所有现有规则对应的谓词
        #print('existing_rule')
        #print(existing_rule)
        #print(self.new_rule_predicate().split('&'))
        invar_list = []
        if existing_rule:
            for single_rule in existing_rule:
                # 一个循环生成一条规则的INVAR
                single_invar = '   INVAR\n     '
                res = self.new_rule_predicate().split('&')
                for i in res:
                    # 每次遍历一个，如果flag出现在其中，就置为TRUE。如果没有，就正常加入
                    ifexist = 0
                    for flag in single_rule:
                        # 排除为空的情况
                        if flag in i and flag != '':
                            ifexist = 1
                            single_invar += i.replace('FALSE', 'TRUE') + ' & '
                            break
                    if not ifexist:
                        single_invar += i + ' & '
                single_invar = single_invar[:-2]
                invar_list.append(single_invar + '\n')

            return invar_list
        # 如果走这说明规则为空
        return invar_list


    def build_INVAR(self):
        # step_upperlimit
        INVAR_TEXT = ''
        #INVAR_TEXT = INVAR_TEXT + '     step_upperlimit = ' + str(self.upperlimit) + '\n'

        INVAR_TEXT = INVAR_TEXT + self.build_config_INVAR()

        #print('self.collect_threshold_var(self.abstract_mode)')
        INVAR_TEXT = INVAR_TEXT + self.collect_threshold_var(self.mode)


        # 对现有规则
        # 前者对应，后者对应有原规则不缺谓词的情况，此情况下差集为空
        if [] not in self.flag_original_amount or (len(self.flag_original_amount) != 1):# self.round_count == 1:
            if self.abstract_mode == 'present':
                cnt = -1
                for single_rule in self.flag_original_amount:
                    cnt += 1
                    for single_predicate in single_rule:
                        single_predicate_name = single_predicate[0]
                        # 不抽象数值类
                        res = ''
                        if single_predicate_name not in self.number_abstract_candidate:
                            res = '   INVAR\n     '
                            for i in range(single_predicate[1]):
                                if i == single_predicate[1]-1:
                                    res += 'toint(original_flag_rule%s_%s_%s)' % (str(cnt), single_predicate[0], str(i))
                                else:
                                    res += 'toint(original_flag_rule%s_%s_%s) + ' % (str(cnt), single_predicate[0], str(i))
                            res += ' < 2\n'
                    # '     toint(flag1) + toint(flag2) != 2'
                        INVAR_TEXT = INVAR_TEXT + res
                # 不能全为FALSE
                cnt = -1
                none_false_str = '   INVAR\n     !('
                print('self.flag_original_amount')
                print(self.flag_original_amount)
                for single_rule in self.flag_original_amount:
                    cnt += 1
                    for single_predicate in single_rule:
                        #res = ''
                        for i in range(single_predicate[1]):
                            if i == single_predicate[1] - 1:
                                none_false_str += 'original_flag_rule%s_%s_%s = FALSE & ' % (str(cnt), single_predicate[0], str(i))
                            else:
                                none_false_str += 'original_flag_rule%s_%s_%s = FALSE & ' % (str(cnt), single_predicate[0], str(i))
                        #res += ' )\n'
                        # '     toint(flag1) + toint(flag2) != 2'
                print('self.logicall_eal')
                print(self.logicall_eal)
                # if none_false_str != '   INVAR\n     !(':
                #     INVAR_TEXT = INVAR_TEXT + none_false_str[:-2] + ' )\n'



        # 加入新增规则的flag
        if self.abstract_mode == 'new':
            INVAR_TEXT = INVAR_TEXT + self.INVAR_new_rule_flag(self.entity_attribute)


        # 在抽象新规则时排除现有规则
        if self.abstract_mode == 'new':
            #print('exclude_existing_rule')
            eer = self.exclude_existing_rule(self.abstract_mode)
            print('在抽象新规则时排除现有规则')
            print(eer)
            for i in eer:
                INVAR_TEXT = INVAR_TEXT + i
            #print(eer)
            # 如果action in spec
            #if eer[-2][0] == find_action_in_spec(self.violating_type, self.spec)[1][0]:
            #    print(eer)


        # 在抽象现有规则时排除现有规则
        if self.abstract_mode == 'present':
            # 统计front规则数量
            spec_info_list = find_info_in_spec(self.violating_type, self.spec)
            front_attribute = spec_info_list[0]
            front_attribute_value = spec_info_list[1]
            end_attribute = spec_info_list[2]
            end_attribute_value = spec_info_list[3]
            front_rule_amount = 0
            try:
                front_rule_amount += len(self.entity_rule_list[front_attribute])
            except:
                front_rule_amount += 0
            # 统计end规则数量
            end_rule_amount = 0
            try:
                end_rule_amount += len(self.entity_rule_list[end_attribute])
            except:
                end_rule_amount += 0
            # 首先针对end
            if end_rule_amount:
                # 通过字符串比较将同trigger的规则归类，并按照谓词数量从多到少排序
                # 先求出trigger有几类
                trigger_catogory = []
                # [['fan.switch', 'smokeDetector.smoke'], ['fan.switch', 'presenceSensor.presence']]
                end_rule = self.entity_rule_list[end_attribute]
                corespond_rule_predicate = self.rule_predicate#[front_rule_amount:]
                for i in range(end_rule_amount):
                    corespond_rule_predicate[i].append(i)
                # substract可能为空
                corespond_substract = self.subtract_predicate#[front_rule_amount:]
                for i in end_rule:
                    # ['fan.switch', 'smokeDetector.smoke'] 默认第二个为trigger且有且仅有一个trigger
                    trigger_catogory.append(i[0][0])
                # set去除重复项
                without = set(trigger_catogory)
                trigger_catogory_amount = len(without)
                # 初始化trigger: 为该trigger的规则 的字典
                trigger_dict = {}
                for i in without:
                    trigger_dict.update({i: []})
                # 将同trigger的规则归类
                cnt = -1
                for i in end_rule:
                    cnt += 1
                    rule_trigger = i[0][0]
                    # 将规则对应的谓词加入
                    trigger_dict[rule_trigger].append(corespond_rule_predicate[cnt])
                # 按照谓词数量从多到少排序
                for trigger_name, rule_set in trigger_dict.items():
                    rule_set.sort(key=len, reverse=True)
                #print('trigger_dict')
                #print(trigger_dict)
                # 如果存在差集，就去找同trigger的最多的规则
                cnt = -1
                for i in corespond_substract:
                    cnt += 1
                    if i != []:
                        current_rule = end_rule[cnt]
                        current_trigger = current_rule[0][0]
                        current_predicate = corespond_rule_predicate[cnt][:-1]
                        current_index = corespond_rule_predicate[cnt][-1]
                        # 求出每一个trigger类中谓词数量最多的规则中的谓词，符号化为s1，并求该谓词与谓词全集的差集s2；
                        # 谓词数量最多的规则s1
                        most_predicate_rule_predicate1 = trigger_dict[current_trigger][0][:-1]
                        rule_index = trigger_dict[current_trigger][0][-1]
                        # 求s1与谓词全集的差集s2
                        sub_predicate2 = list(set(self.predicate) ^ set(most_predicate_rule_predicate1))
                        # 求该规则与s1谓词差集s3，s3全取TRUE加s2全取FALSE
                        sub_predicate3 = list(set(most_predicate_rule_predicate1) ^ set(current_predicate))

                        if len(most_predicate_rule_predicate1) == len(current_predicate) and most_predicate_rule_predicate1 != current_predicate:
                            print('谓词相同的情况')
                            print(most_predicate_rule_predicate1)
                            print(current_predicate)
                            #print('most_predicate_rule_predicate1')
                            #print(most_predicate_rule_predicate1)
                            #print(current_predicate)
                            continue

                        # 如果为单条规则，sub_predicate3为空
                        if not(sub_predicate3):
                            continue
                        #print('排除')
                        #print(sub_predicate2)
                        #print(sub_predicate3)
                        # 还要获得谓词数量最多的规则中的谓词取值
                        #print(current_rule)
                        #print(end_rule[rule_index])
                        # 找到和self.flag_original_amount关系，得到original_flag_rule%s_%s_%s
                        # 应该是front_amount + index
                        original_flag_rule_str = '!('
                        for j in sub_predicate2:
                            a, c = self.get_var_value_and_amount(j)
                            for k in range(c):
                                original_flag_rule_str += 'original_flag_rule%d_%s_%d = FALSE & ' % (current_index, j, k)

                        # 还要获得谓词数量最多的规则中的谓词取值
                        # [['smokeDetector.smoke=detected'], ['none'], ['on', 'off'], [5, 0, 'none']]
                        # ['presenceSensor.presence']
                        # t,a相同，那么从C里找信息，从C里找对应谓词的取值
                        rule_condition = end_rule[rule_index][1]
                        if rule_condition[0] != 'none':
                            for rc in rule_condition:
                                for k in sub_predicate3:
                                    sign = ''
                                    if '>=' in rc:
                                        sign = '>='
                                    elif '<=' in rc:
                                        sign = '<='
                                    elif '<' in rc:
                                        sign = '<'
                                    elif '>' in rc:
                                        sign = '>'
                                    elif '=' in rc:
                                        sign = '='
                                    rc_predicate_name = rc.split(sign)[0].replace(' ', '')
                                    if rc_predicate_name == k.replace(' ', ''):
                                        # print(rc_predicate_name)
                                        rc_predicate_attribute = rc.split(sign)[1].replace(' ', '')
                                        a, c = self.get_var_value_and_amount(rc_predicate_name)
                                        attribute_range = []
                                        if '{' in a:
                                            attribute_range = a.replace('{', '').replace('}', '').replace(' ', '').split(',')
                                        # 数值类情况怎么办
                                        else:
                                            #upper = int(a.replace(' ', '').split('..')[1])
                                            #down = int(a.replace(' ', '').split('..')[0])
                                            attribute_range = []
                                            if 'boolean' not in a:
                                                #attribute_range = self.number_abstract_candidate[rc_predicate_name]
                                                for m in self.number_abstract_candidate[rc_predicate_name]:#list(range(down, upper + 1)):
                                                    attribute_range.append(str(m))
                                            else:
                                                attribute_range.append('TRUE')
                                                attribute_range.append('FALSE')
                                        #print('排除2')
                                        #print(a)
                                        #print(c)
                                        #print(attribute_range)
                                        #print(rc_predicate_attribute)
                                        for m in range(c):
                                            if rc_predicate_attribute == attribute_range[m].replace(' ', ''):
                                                original_flag_rule_str += 'original_flag_rule%d_%s_%d = TRUE & ' % (current_index, rc_predicate_name, m)
                                            else:
                                                original_flag_rule_str += 'original_flag_rule%d_%s_%d = FALSE & ' % (
                                                current_index, rc_predicate_name, m)
                                        break
                        original_flag_rule_str = original_flag_rule_str[:-2] + ')\n'
                        if original_flag_rule_str != ')\n':
                            INVAR_TEXT = INVAR_TEXT + '\n   INVAR\n     ' + original_flag_rule_str
                            #print('original_flag_rule_str')
                            #print(original_flag_rule_str)


            # 之后针对front
            elif front_rule_amount:
                pass





        # 第三轮迭抽象延时
        '''if self.abstract_mode == 'delay':
            # 第一次可以随机取
            if ModelAbstractor.ID == 1:
                duia_str = '   INVAR\n     '
                for duia in self.delay_used_in_abstract:
                    # 每次随机选一个值
                    duia_str = duia_str + duia[0] + '_abstract = ' + str(0 if random.randint(0, 10) > 5 else duia[1]) + ';\n'
                INVAR_TEXT = INVAR_TEXT + duia_str'''

        if self.mode == 'iteration':
            # 排除第一次的情况，因为flag还没有取过值
            if self.flag_INVAR.replace(' ', '') != ')\n\n':
                for duia in self.delay_used_in_abstract:
                    for s_a in self.states[0]:
                        if (duia[0]+'_abstract_flag') in s_a:
                            print('!('+duia[0]+'_abstract_flag'+'='+s_a.split('=')[1]+')')
                            #INVAR_TEXT = INVAR_TEXT + '   INVAR\n' + self.flag_INVAR
                            # 之后不能取之前的值
                            '''if self.__class__.INVAR_test_list:
                                for i in self.__class__.INVAR_delay:
                                    INVAR_TEXT = INVAR_TEXT + i
                            self.__class__.INVAR_delay.append('   INVAR\n' + self.flag_INVAR)'''
            else:
                pass


        # 如果是第一次之后的迭代，则要加INVAR排除flag取值
        if self.mode == 'iteration':
            # 排除第一次的情况
            if self.flag_INVAR.replace(' ', '') != ')\n\n':
                INVAR_TEXT = INVAR_TEXT + '   INVAR\n' + self.flag_INVAR
                # 以前的INVAR也要加上
                if self.__class__.INVAR_test_list:
                    for i in self.__class__.INVAR_test_list:
                        INVAR_TEXT = INVAR_TEXT + i
                self.__class__.INVAR_test_list.append('   INVAR\n' + self.flag_INVAR)

                # new rule
                # self.__class__.INVAR_new_rule_list.append()

            # 排除第一次
            else:
                # 是等于''还是 + ''
                INVAR_TEXT = INVAR_TEXT + ''
                #   INVAR
                #     !(flag1 = TRUE & flag2 = FALSE)
                pass


        return INVAR_TEXT

    def INVAR_new_rule_flag(self, entity_attribute):
        triggerflag = []
        VAR_text = ''
        none_false_str = '   INVAR\n      !('

        tmp = self.predicate
        # 排除当前谓词，next(window.switch)
        predicate_without_now_predicate = list(set(tmp) ^ set([self.entity_attribute]))
        predicate_amount = len(predicate_without_now_predicate)
        # 加入single_amount条新规则
        for single_amount in range(self.new_rule_amount):
            # 一个谓词一个triggerflag，加其取值flag
            for i in range(predicate_amount):
                current_predicate = predicate_without_now_predicate[i]
                a, c = self.get_var_value_and_amount(current_predicate)
                # triggerflag
                none_false_str += 'new_rule%s_%s_triggerflag = FALSE & ' % (str(single_amount), current_predicate)
                triggerflag.append('new_rule%s_%s_triggerflag' % (str(single_amount), current_predicate))
                # 取值flag
                # toint(flag1) + toint(flag2) != 2
                VAR_text = VAR_text + '   INVAR\n      '
                for j in range(c):
                    none_false_str += 'new_rule%s_%s_valueflag%s = FALSE & ' % (str(single_amount), current_predicate, str(j))
                    VAR_text = VAR_text + 'toint(new_rule%s_%s_valueflag%s)' % (str(single_amount), current_predicate, str(j))
                    if j != c-1:
                        VAR_text = VAR_text + ' + '
                VAR_text = VAR_text + ' < 2 \n'

                # 数值类抽象多加flag
                if current_predicate in NUMBER_ABSTRACT and current_predicate in self.logicall_eal:
                    for j in range(c):
                        VAR_text = VAR_text + '   INVAR\n      toint(new_rule%s_%s_valueflag%s_%s)+toint(new_rule%s_%s_valueflag%s_%s)=1\n' % (
                                                                                    str(single_amount), current_predicate, str(j), 'rise',
                                                                                    str(single_amount), current_predicate, str(j), 'drop')

        # -- 一次只能一个trigger
        # toint(flag3) + toint(flag6) = 1
        VAR_text = VAR_text + '   INVAR\n      '
        triggerflag_len = len(triggerflag)
        for i in range(triggerflag_len):
            VAR_text = VAR_text + 'toint(' + triggerflag[i] + ')'
            if i != triggerflag_len - 1:
                VAR_text = VAR_text + ' + '
        VAR_text = VAR_text + ' = 1\n'

        # VAR_text = VAR_text + none_false_str[:-2] + ')\n'
        return VAR_text

    def ASSISGN_flag(self):
        cnt = -1
        res = ''
        for single_rule in self.flag_original_amount:
            cnt += 1
            for single_predicate in single_rule:
                single_predicate_name = single_predicate[0]
                # 不抽象数值类
                if single_predicate_name not in self.number_abstract_candidate:
                    for i in range(single_predicate[1]):
                        res += '      next(original_flag_rule%s_%s_%s) := original_flag_rule%s_%s_%s; \n\n' % (str(cnt), single_predicate[0], str(i), str(cnt), single_predicate[0], str(i))
        return res

    def ASSIGN_new_rule_flag(self):
        VAR_text = '\n'
        tmp = self.predicate
        # 排除当前谓词，next(window.switch)
        predicate_without_now_predicate = list(set(tmp) ^ set([self.entity_attribute]))
        predicate_amount = len(predicate_without_now_predicate)
        # 加入single_amount条新规则
        for single_amount in range(self.new_rule_amount):
            # 一个谓词一个triggerflag，加其取值flag
            for i in range(predicate_amount):
                current_predicate = predicate_without_now_predicate[i]
                a, c = self.get_var_value_and_amount(current_predicate)
                # triggerflag
                VAR_text = VAR_text + '      next(new_rule%s_%s_triggerflag) :=\n          case\n' % (str(single_amount), current_predicate)
                # 取值flag
                VAR_text = VAR_text + '            (' # 外侧加括号维持运算优先级
                for j in range(c):
                    VAR_text = VAR_text + 'next(new_rule%s_%s_valueflag%s)' % (str(single_amount), current_predicate, str(j))
                    if j != c-1:
                        VAR_text = VAR_text + ' | '
                VAR_text = VAR_text + ')=FALSE: FALSE;\n'
                VAR_text = VAR_text + '            TRUE: new_rule%s_%s_triggerflag;\n         esac;\n' % (str(single_amount), current_predicate)
                # 取值flag
                for j in range(c):
                    VAR_text = VAR_text + '      next(new_rule%s_%s_valueflag%s) := new_rule%s_%s_valueflag%s;\n' % (str(single_amount), current_predicate, str(j), str(single_amount), current_predicate, str(j))

                # 数值类抽象
                if current_predicate in NUMBER_ABSTRACT and current_predicate in self.logicall_eal:
                    for j in range(c):
                        for cnt in ['rise', 'drop']:
                            VAR_text = VAR_text + '      next(new_rule%s_%s_valueflag%s_%s) := new_rule%s_%s_valueflag%s_%s;\n' % (
                            str(single_amount), current_predicate, str(j), cnt, str(single_amount), current_predicate, str(j), cnt)

        VAR_text = VAR_text + '\n'
        return VAR_text


    def generate_flag_original_amount(self):
        # self.predicate是针对全体属性的，self.rule_predicate, self.subtract_predicate只包含安全属性中的属性
        self.predicate, self.rule_predicate, self.subtract_predicate = self.analyze_predicate()
        print('self.predicate')
        print(self.predicate)
        print(self.rule_predicate)
        print(self.subtract_predicate)
        #print('全体谓词')
        #print(self.predicate)
        for single_rule in self.subtract_predicate:
            li = []
            for single_predicate in single_rule:
                a, c = self.get_var_value_and_amount(single_predicate)
                li.append([single_predicate, c])
            self.flag_original_amount.append(li)
        #print('self.flag_original_amount')
        #print(self.flag_original_amount)
        return


    def abstract_time_ASSIGN(self):
            VAR_TEXT = '\n'
            duia_str = ''
            for duia in self.delay_used_in_abstract:
                # 每次随机选一个值
                duia_str = duia_str + '      next(' + duia[0] + '_abstract_flag):=' + duia[0] + '_abstract_flag;\n'
            VAR_TEXT = VAR_TEXT + duia_str + '\n'

            return VAR_TEXT

    def __Extended_rule_flag_ASSIGN(self, name1, name2, trigger_condition):
        s = '''     init(%s) := 0;
     next(%s) :=
            case
                %s: 1;
                %s.timer = 1: 0;
                TRUE: %s;
            esac;\n\n''' % (name1, name1, trigger_condition, name2, name1)
        return s

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

    def collect_last_var(self):
        res = []
        if self.mode == 'iteration':
            for single_attribute in self.states[0]:
                # 排除wait_trigger_flag，因为不通过flag找
                if 'last' in single_attribute:
                    res.append(single_attribute.replace('\n', '').replace('\r', ''))
        # 第一次
        else:
            res = []
        return res

    def __build_ASSIGN(self):
        # 安全属性里的信息
        spec_info_list = find_info_in_spec(self.violating_type, self.spec)
        front_attribute = spec_info_list[0]
        front_attribute_value = spec_info_list[1]
        end_attribute = spec_info_list[2]
        end_attribute_value = spec_info_list[3]



        ''' step变量取值 '''
        ASSIGN_text = '   ASSIGN\n'
        ASSIGN_text = ASSIGN_text + self.step_text()

        # 数值类last变量值和上次保持一致
        # print('collect_last_var')
        # print(self.collect_last_var())
        for i in self.collect_last_var():
            tmp = i.replace(' ', '').replace('_last', '').split('=')
            if tmp[0] in NUMBER_ABSTRACT:
                print('wrong')
                print('         init(%s) := %s;\n' % (tmp[0] + LAST_STATE, tmp[1]))
                ASSIGN_text = ASSIGN_text + '         init(%s) := %s;\n' % (tmp[0] + LAST_STATE, tmp[1])

        ''' 找到冲突前的取值 '''
        # 不被设备执行影响的延时自然属性，比如下雨
        # 在开始前，先做和相关属性集合的交集,weather_count不管
        li = []
        for key, value in self.entity_attribute_list.items():
            li.append(key)
        intersect_set = set(li).intersection(UNAFFECTED_EXTENDED_ENVIRONMENT)
        unaffected_environment_dic = self.find_assign_before_violating_state(intersect_set)
        for key, value in unaffected_environment_dic.items():
            s, amount = self.get_var_value_and_amount(key)
            ASSIGN_text = ASSIGN_text + self.__UNAFFECTED_EXTENDED_ENVIROMENT_ASSIGN(key, key + ENVIRONMENT_COUNT,
                                                                                     s, value)

        # channel-based interaction 的threshold不变
        for key, value in self.entity_attribute_list.items():
            for cb in CHANNEL_INTERACTION_CONFIG_LIST:
                if key == cb.name:
                    category = ''
                    if len(cb.threshold) == 2:
                        category += 'one'
                    elif len(cb.threshold) == 4:
                        category += 'two'
                    if self.mode != 'iteration':
                        if category == 'one':
                            ASSIGN_text = ASSIGN_text + '      next(' + key + '_threshold):=' + key + '_threshold' + ';\n\n'
                        elif category == 'two':
                            ASSIGN_text = ASSIGN_text + '      next(' + key + '_rise_threshold):=' + key + '_rise_threshold' + ';\n\n'
                            ASSIGN_text = ASSIGN_text + '      next(' + key + '_drop_threshold):=' + key + '_drop_threshold' + ';\n\n'
                        break

        # 不被设备执行影响的非延时自然属性，比如present
        intersect_set = set(li).intersection(UNAFFECTED_IMMEDIATE_ENVIRONMENT)
        unaffected_immediate_environment_dic = self.find_assign_before_violating_state(intersect_set)
        for key, value in unaffected_immediate_environment_dic.items():
            s, amount = self.get_var_value_and_amount(key)
            ASSIGN_text = ASSIGN_text + self.__UNAFFECTED_IMMEDIATE_ENVIROMENT_ASSIGN(key, key + ENVIRONMENT_COUNT,
                                                                                     s, value)

        # 被设备影响的非延时自然属性，比如光照，窗户开关
        # 目前是固定init
        print('被设备影响的非延时自然属性')
        affected_immediate_environment = set(self.logicall_and_physical_predicate).difference(EXTENDED_ENVIRONMENT).difference(UNAFFECTED_IMMEDIATE_ENVIRONMENT)
        # 减去当前安全属性
        affected_immediate_environment_without_safety_property = affected_immediate_environment.difference([front_attribute, end_attribute])
        affected_immediate_environment_dic = self.find_assign_before_violating_state(affected_immediate_environment_without_safety_property)
        for key, value in affected_immediate_environment_dic.items():
            s, amount = self.get_var_value_and_amount(key)
            if key not in self.entity_rule_list:
                ASSIGN_text = ASSIGN_text + '         init(%s) := %s;\n' % (key, value[0].replace('\n', '').replace('\r', ''))
            #ASSIGN_text = ASSIGN_text + self.__AFFECTED_IMMEDIATE_ENVIROMENT_ASSIGN(key, key + ENVIRONMENT_COUNT, s, value)


        # 不被设备影响的延时自然属性，比如下雨，已建模在函数开头

        # 被设备影响的延时自然属性，比如温度，烟雾
        # 先交集求出延时属性，后差集求出被设备影响的延时自然属性
        intersect_set = set(li).intersection(EXTENDED_ENVIRONMENT).difference(UNAFFECTED_EXTENDED_ENVIRONMENT)
        print('被设备影响的延时自然属性')
        print(intersect_set)
        affected_environment_dic = self.find_assign_before_violating_state(intersect_set)
        for key, value in affected_environment_dic.items():
            s, amount = self.get_var_value_and_amount(key)
            ASSIGN_text = ASSIGN_text + self.__AFFECTED_EXTENDED_ENVIROMENT_ASSIGN(key, key + ENVIRONMENT_COUNT,
                                                                                     s, value)


        # 处理last变量，处理方式同ModelBuilder,last不管
        for key, value in self.entity_attribute_list.items():
            if front_attribute == key:
                if type(value) == type('1'):
                    # value = value.split('..')
                    break
                for i in value:
                    if front_attribute_value != i:
                        ASSIGN_text = ASSIGN_text + '      init(' + front_attribute + LAST_STATE + '):=' + i + ';\n'
                        break
            elif end_attribute == key:
                if type(value) == type('1'):
                    # value = value.split('..')
                    break
                for i in value:
                    if end_attribute_value != i:
                        ASSIGN_text = ASSIGN_text + '      init(' + end_attribute + LAST_STATE + '):=' + i + ';\n'
                        break
        # 同ModelBuilder
        # 处理属性里没有的值 例如weather的属性没有处理smoke的情况，因为属性里没smoke，所以没他的值
        # 如果属性里有smoke clear，那么这步会直接排除smoke，所以不影响
        # 设定某些实体的不安全属性，让LAST变量初始为不安全
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
            #print(ev)
            v2 = self.get_var_value(ev)
            #print(v2)
            # 等于不安全状态
            v1 = CHANNEL_INTERACTION_CONFIG_DICT[ev]
            #print(v1)
            # 排除不安全后的安全状态，list枚举类型达到阈值后切换为安全状态
            if '{' in v2:
                for i in v2.replace(' ', '').replace('{', '').replace('}', '').split(','):
                    if v1 != i:
                        v2 = i
                        #print('      init(' + ev + LAST_STATE + '):=' + v2 + ';\n')
                        ASSIGN_text = ASSIGN_text + '      init(' + ev + LAST_STATE + '):=' + v2 + ';\n'
                        break
            # 如果是温度类型，则达到阈值加一
            # 但是存在超过阈值问题
            elif '..' in v2:
                pass
                # v2 = enviroment_var + '+1'
        ASSIGN_text = ASSIGN_text + '\n'

        # 处理last变量的next
        for key, value in self.entity_attribute_list.items():
            ASSIGN_text = ASSIGN_text + '      next(' + key + LAST_STATE + '):=' + key + ';\n'

        # 伪反例消除算法之进行下一条延时规则的抽象
        if self.abstract_mode == 'wait_trigger':
            # 首先筛选出和属性相关的延时规则作为抽象备选
            for eal_ele in self.extended_attribute_list:
                #front_attribute = spec_info_list[0]
                #front_attribute_value = spec_info_list[1]
                #end_attribute = spec_info_list[2]
                #end_attribute_value = spec_info_list[3]
                eal_attribute = eal_ele[0].split('_')[1]
                if eal_attribute == front_attribute:
                    self.property_entity_delay_rule.append(eal_ele)
                elif eal_attribute == end_attribute:
                    self.property_entity_delay_rule.append(eal_ele)

            self.__class__.WAIT_TRIGGER_AMOUNT = len(self.property_entity_delay_rule)
            print('self.__class__.WAIT_TRIGGER_AMOUNT')
            print(self.__class__.WAIT_TRIGGER_AMOUNT)
            print('self.property_entity_delay_rule')
            print(self.property_entity_delay_rule)

            if self.mode == 'iteration':
               # 不能这样排除第一次的情况，因为flag还没有取过值，因为wait_trigger不靠flag
                if self.__class__.WAIT_TRIGGER_cnt < self.__class__.WAIT_TRIGGER_AMOUNT - 1:
                    self.__class__.WAIT_TRIGGER_cnt += 1
                    print('self.__class__.WAIT_TRIGGER_cnt')
                    print(self.__class__.WAIT_TRIGGER_cnt)
                    #print('self.__class__.WAIT_TRIGGER_cnt')
                    #print(self.__class__.WAIT_TRIGGER_cnt)
                # 如果到最后一条则再回到第一条
                #else:
                    #print('self.__class__.WAIT_TRIGGER_cnt_else')
                    #print(self.__class__.WAIT_TRIGGER_cnt)
                    #self.__class__.WAIT_TRIGGER_cnt = 0



            # 第三轮迭抽象延时
        if self.abstract_mode == 'delay':
            ASSIGN_text = ASSIGN_text + self.abstract_time_ASSIGN()


        # 不涉及TAP规则的设备属性不变 并且不能是安全属性值
        attribute_not_rule_related = []
        for attribute1, value in self.entity_attribute_list.items():
            flag = 0
            for attribute2, rule in self.entity_rule_list.items():
                if attribute1 == attribute2:
                    flag = 1
                    break
            if not flag:
                attribute_not_rule_related.append(attribute1)
        print('不涉及TAP规则')
        attribute_not_rule_related = list(set(attribute_not_rule_related).difference(EXTENDED_ENVIRONMENT).difference(UNAFFECTED_EXTENDED_ENVIRONMENT).\
              difference(UNAFFECTED_IMMEDIATE_ENVIRONMENT).difference(AFFECTED_IMMEDIATE_ENVIRONMENT).difference([self.entity_attribute]))
        print(attribute_not_rule_related)
        attribute_not_rule_related_dic = self.find_assign_before_violating_state(attribute_not_rule_related)
        print(attribute_not_rule_related_dic)
        for anrr in attribute_not_rule_related:
            ASSIGN_text = ASSIGN_text + self.__NOT_RULE_RELATEED_ASSIGN(anrr, attribute_not_rule_related_dic[anrr])


        # ASSIGN_flag 针对现有规则
        #print('self.flag_original_amount')
        #print(self.flag_original_amount)
        if [] not in self.flag_original_amount or (len(self.flag_original_amount) != 1): #self.round_count == 1:
            if self.abstract_mode == 'present':
                ASSIGN_text = ASSIGN_text + self.ASSISGN_flag()

        # 针对新规则flag的ASSIGN
        # 第二轮迭代加入新规则
        if self.abstract_mode == 'new':
            ASSIGN_text = ASSIGN_text + self.ASSIGN_new_rule_flag()

        new_rule_str = ''
        if self.abstract_mode == 'new':
            # if i == tap_amount - 1:
            # 处理新增规则的情况
            # ((flag1|flag2) & (flag3)->(weather.rainState != weather.rain)) & ((flag1)->(weather.rain = raining)) & ((flag2)->(weather.rain = not_raining)) & ((flag4|flag5) & (flag6)->(smokeState != smoke)) & ((flag4)->(smoke = detected)) & ((flag5)->(smoke = clear)): open;
            # 一次只新增一条
            self.new_rule_amount_cnt = self.new_rule_amount_cnt + 1
            if self.new_rule_amount_cnt <= self.new_rule_amount:
                new_rule_str = new_rule_str + '             ' + self.ASSIGN_new_rule()

        # 对无TAP规则的情况
        if self.abstract_mode == 'new':
            if not self.entity_rule_list:
                ASSIGN_text = ASSIGN_text + '    next(' + self.entity_attribute + '):=\n          case\n'
                ASSIGN_text = ASSIGN_text + new_rule_str
                ASSIGN_text = ASSIGN_text + '             TRUE:' + self.entity_attribute + ';\n          esac;\n'

        sensor = ['presenceSensor.presence', 'temperatureMeasurement.temperature', 'smokeDetector.smoke',
                  'carbonMonoxideDetector.carbonMonoxide', 'carbonDioxideMeasurement.carbonDioxide', 'rainSensor.rain',
                  'relativeHumidityMeasurement.humidity']

        # 获得所有变量冲突前的取值，这步按理来说是在之前
        # predicate(attribute):[0,1,2,3,4]
        predicate_dic = self.find_assign_before_violating_state(self.predicate)
        # 常规变量
        for entity_attribute, tap_set in self.entity_rule_list.items():
            if entity_attribute in sensor:
                continue
            '''if entity_attribute in list(affected_immediate_environment_without_safety_property):
                print('跳过不建模')
                print(entity_attribute)
                continue'''
            # 它的位置可能是bug点
            rule_index = -1
            tap_amount = len(tap_set)
            # 一个循环处理同设备能力多条规则的一条
            tmp = []  # 处理.timer，延时
            s1, s2, s3 = '', '', ''
            # init步骤要有
            for key, value in predicate_dic.items():
                if key == entity_attribute:
                    s1 = ('    init(' + entity_attribute + '):=' + value[0] +';\n').replace('\r', '')
                    break
            s1 = s1 + '    next(' + entity_attribute + '):=\n          case\n'
            #print('tap_amount')
            #print(tap_amount)
            #print('rule_index')
            #print(rule_index)
            count = -1
            for i in range(tap_amount):
                count += 1
                #print('i')
                #print(i)
                rule_index += 1
                # tap_set[i]对应一条规则
                single_rule = tap_set[i]
                ''''fan.switchCap.switch': [[['smoke=detected'],['none'],['on','off'],[5,0]] , [['presenceSensor=present'],['none'],['on','off'],[3,0]] , [['waterSensor=wet'],['none'],['on','off'],[3,0]]]}'''
                # trigger
                trigger = '             '
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
                    elif sign == '=':
                        trigger = trigger + j
                        # 体现trigger的跳变last
                        trigger = trigger + '&' + j_name + '!=' + j_name + LAST_STATE
                        continue
                    else:
                        j_name = j.split(sign)[0]
                        j_attribute = j.split(sign)[1]
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

                # condition
                condition = ''
                first_flag = 1
                for j in list(set(single_rule[1])):
                    if first_flag:
                        first_flag = 0
                        condition = condition + j
                        continue
                    condition = condition + '&' + j
                # 谓词抽象现有规则
                # 利用顺序分析的rule_index来实现对应关系
                predicate_text = ''
                # 要为front和end才抽象
                if self.abstract_mode == 'present' and entity_attribute == end_attribute:#(entity_attribute == front_attribute or entity_attribute == end_attribute):
                    # 利用第一个谓词是next()谓词来知道对应哪个
                    # & ((flag1)->(weather.rain = raining)) & ((flag2)->(weather.rain = not_raining))
                    #print('list index out of range')
                    #print(self.flag_original_amount)
                    #print(rule_index)
                    single_rule_predicate = self.flag_original_amount[rule_index]
                    #print('wrong1')
                    #print(self.flag_original_amount)
                    #print(rule_index)
                    for sp in range(len(single_rule_predicate)):
                            single_predicate = single_rule_predicate[sp]
                            #print('single_predicate')
                            #single_predicate)
                            single_predicate_name = single_predicate[0]
                            # 不抽象数值类
                            if single_predicate_name not in self.number_abstract_candidate:
                                v, cn = self.get_var_value_and_amount(single_predicate[0])
                                possible_value = []
                                if 'boolean' in v:
                                    possible_value = ['FALSE', 'TRUE']
                                elif '..' in v:
                                    #lower = int(v.split('..')[0])
                                    #upper = int(v.split('..')[1])
                                    possible_value = self.number_abstract_candidate[single_predicate[0]]# list(range(lower, upper+1))
                                elif '{' in v:
                                    possible_value = v.replace('{', '').replace('}', '').split(',')
                                for am in range(single_predicate[1]):
                                    predicate_text += ' & ((original_flag_rule%s_%s_%s)->(%s = %s))' % (str(rule_index), single_predicate[0],
                                                                                                        str(am), single_predicate[0], possible_value[am])
                                    self.__class__.original_flag_dic.update({'original_flag_rule%s_%s_%s' % (str(rule_index), single_predicate[0], str(am)): '%s = %s' % (single_predicate[0], possible_value[am])})
                # action凑整条
                #print(predicate_text)
                action = single_rule[2][0]
                # 如果为AFTER类延时，不加t,c
                if action == 'none':
                    s1 = s1 + ''
                else:
                    # condition为空的情况
                    if single_rule[1][0] != 'none':
                        s1 = s1 + trigger + '&' + condition + predicate_text + ':' + action + ';\n'
                        #print('wrong')
                        #print(trigger + '&' + condition + predicate_text + ':' + action + ';\n')
                    else:
                        s1 = s1 + trigger + predicate_text + ':' + action + ';\n'
                        #print('wrong')
                        #print(trigger + predicate_text + ':' + action + ';\n')


                # 处理延迟
                if single_rule[1][0] != 'none':
                    trigger_condition = trigger + '&' + condition + predicate_text
                else:
                    trigger_condition = trigger + predicate_text
                # 要对应着延迟才处理
                for k in self.extended_attribute_list:
                    name1 = k[0]
                    upper_limit = k[1]
                    name2 = k[2]
                    single_rule_actionSet = single_rule[2]
                    # delay
                    string = ''
                    if single_rule_actionSet[0] != 'none':
                        string += 'delay_' + entity_attribute + '_' + single_rule_actionSet[0] + '_' + str(i)
                    else:
                        string += 'delay_' + entity_attribute + '_' + 'none' + '_' + str(i)

                    # 添加延时属性变量
                    # rule_flag_string = 'extended_rule_FLAG_' + entity_attribute + '_' + single_rule_actionSet[0] + '_' + str(i)
                    if name1 == string:
                        if self.abstract_mode != 'delay':
                            s2 = s2 + self.__Delay(name1, upper_limit, name2,
                                               trigger_condition.replace(' ', '').replace('    ', ''))
                            # s2 = s2 + self.__Extended_rule_flag_ASSIGN(rule_flag_string, name2, trigger_condition.replace(' ', '').replace('    ', ''))
                        # 如果是第三轮即3+3n，则抽象runin
                        else:#'{0,' + upper_limit + '}'

                            s2 = s2 + self.__Delay(name1, name1 + '_abstract_flag', name2,
                                               trigger_condition.replace(' ', '').replace('    ', ''))

                            # s2 = s2 + self.__Extended_rule_flag_ASSIGN(rule_flag_string, name2, trigger_condition.replace(' ', '').replace('    ', ''))
                # 处理到点关机
                extended_attribute_cnt = -1
                for k in self.extended_attribute_list:
                    extended_attribute_cnt += 1
                    # (delay_name1, 延时多少, runin_name2, entity_attribute)
                    name2 = k[2]
                    # entity_attribute = k[3]
                    # single_rule [[t],[c],[a],[latency]]
                    single_rule_actionSet = single_rule[2]
                    string = ''
                    if single_rule_actionSet[0] != 'none':
                        string += 'runin_' + entity_attribute + '_' + single_rule_actionSet[0] + '_' + str(i)
                    else:
                        string += 'runin_' + entity_attribute + '_' + 'none' + '_' + str(i)

                    if name2 == string:
                        # runinfan_smoke.timer=1&fan.switchCap.switch=on: off;
                        # wait_trigger抽象,抽象对应的一条规则
                        # 如果为wait_trigger
                        wtr_ele_list = []
                        for wtr_ele in self.wait_trigger_record:
                            wtr_ele_list.append(wtr_ele[0])
                        if ('%s_wait_trigger_flag%d' % (entity_attribute, i)) in wtr_ele_list:
                            # 如果有wait_trigger则不抽象
                            s3 = s3 + '             next(%s_wait_trigger_flag%d)=0:' % (entity_attribute, i) + single_rule_actionSet[1] + ';\n'
                            #print('越界？')
                            #print(self.property_entity_delay_rule)
                            #print(self.__class__.WAIT_TRIGGER_cnt)
                            # 如果要抽象的是已有的wait_trigger，则加一，跳过该规则
                            if self.abstract_mode == 'wait_trigger' and (entity_attribute == front_attribute or entity_attribute == end_attribute) \
                                and self.property_entity_delay_rule[self.__class__.WAIT_TRIGGER_cnt][2] == string \
                                    and self.__class__.WAIT_TRIGGER_cnt < self.__class__.WAIT_TRIGGER_AMOUNT - 1:
                                self.__class__.WAIT_TRIGGER_cnt += 1
                        else:
                            # # 抽象对应的一条规则，只抽象安全属性里的
                            if self.abstract_mode == 'wait_trigger' and (entity_attribute == front_attribute or entity_attribute == end_attribute) \
                                    and self.property_entity_delay_rule[self.__class__.WAIT_TRIGGER_cnt][2] == string:
                                    print('self.property_entity_delay_rule')
                                    print(self.property_entity_delay_rule)
                                    print(self.property_entity_delay_rule[self.__class__.WAIT_TRIGGER_cnt])
                                    # 抽象对应的一条规则
                                    s3 = s3 + '             next(wait_trigger_FLAG)=0:' + single_rule_actionSet[1] + ';\n'
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
                                                    none_action += ii + '|'
                                            break
                                    none_action = none_action[:-1] + ')'
                                    s3 = s3 + '             ' + name2 + '.timer=1 & ' + entity_attribute + '=' + \
                                         none_action + ':' + single_rule_actionSet[1] + ';\n'

            # TRUE
            s3 = s3 + '             TRUE:' + entity_attribute + ';\n          esac;\n'
            # Delay
            ASSIGN_text = ASSIGN_text + s2
            # TAP规则
            ASSIGN_text = ASSIGN_text + s1
            # 抽象新规则
            # 要为front和end才抽象
            if self.abstract_mode == 'new' and entity_attribute == end_attribute: #(entity_attribute == front_attribute or entity_attribute == end_attribute):
                ASSIGN_text = ASSIGN_text + new_rule_str
            # 到点关机和TRUE
            ASSIGN_text = ASSIGN_text + s3

            # wait_trigger_flag赋值
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
                        ASSIGN_text = ASSIGN_text + wait_trigger_str
                        break

        # wait_trigger_FLAG赋值 如果无延时则不抽象
        if self.abstract_mode == 'wait_trigger' and self.extended_attribute_list != []:
            # 从安全属性里找到前置条件 并找到差集
            front = front_attribute + '=' + front_attribute_value
            end = end_attribute + '=' + end_attribute_value
            different_list = []
            for key, value in self.entity_attribute_list.items():
                if front_attribute == key:
                    for i in value:
                        if front_attribute_value != i:
                            different_list.append(i)
            different_str = '('
            different_list_len = len(different_list)
            for i in range(different_list_len):
                if (different_list_len > 1 and i == different_list_len - 1) or (different_list_len == 1):
                    different_str += front_attribute + '=' + different_list[i]
                else:
                    different_str += front_attribute + '=' + different_list[i] + '|'
            different_str += ')'
            # wait_trigger_FLAG赋值
            #             runin_fan.switch_on_1.timer=1 & fan.switch=on & smokeDetector.smoke=detected:1;
            #             runin_fan.switch_on_1.timer=1 & fan.switch=on & smokeDetector.smoke=clear:0;
            #             wait_trigger_FLAG=1 & smokeDetector.smoke=clear:0;
            # (name1, str(single_rule_delaySet[j]), name2, entity_attribute)
            #print('数组可能越界')
            #print(self.property_entity_delay_rule)
            #print(self.__class__.WAIT_TRIGGER_cnt)
            corresponding_info = self.property_entity_delay_rule[self.__class__.WAIT_TRIGGER_cnt]
            runin_name = corresponding_info[2]
            wait_trigger_str = '''    init(wait_trigger_FLAG):=-1;
        next(wait_trigger_FLAG):=
              case
                %s.timer=1 & %s:1;
                %s.timer=1 & %s:0;
                wait_trigger_FLAG=1 & %s:0;
                wait_trigger_FLAG=0:-1;
                TRUE:wait_trigger_FLAG;
              esac;\n''' % (runin_name, front,
                            runin_name, different_str,
                            different_str)
            ASSIGN_text = ASSIGN_text + wait_trigger_str

        ASSIGN_text = ASSIGN_text + assign_trigger_delay(self.trigger_delay_record, self.entity_attribute_list)

        return ASSIGN_text

    def ASSIGN_new_rule(self):
        VAR_text = ''
        tmp = self.predicate
        # 排除当前谓词，next(window.switch)
        predicate_without_now_predicate = list(set(tmp) ^ {self.entity_attribute})
        predicate_amount = len(predicate_without_now_predicate)
        # 加入single_amount条新规则
        for single_amount in range(self.new_rule_amount):
            # 一个谓词一个triggerflag，加其取值flag
            # action默认取安全属性里的
            action = find_action_in_spec(self.violating_type, self.spec)[1][0]
            for i in range(predicate_amount):
                current_predicate = predicate_without_now_predicate[i]
                a, c = self.get_var_value_and_amount(current_predicate)
                # ((flag1|flag2) & (flag3)->(weather.rainState != weather.rain)) & ((flag1)->(weather.rain = raining)) & ((flag2)->(weather.rain = not_raining)) & ((flag4|flag5) & (flag6)->(smokeState != smoke)) & ((flag4)->(smoke = detected)) & ((flag5)->(smoke = clear)): open;
                VAR_text = VAR_text + '((('
                # trigger
                for j in range(c):
                    VAR_text = VAR_text + 'new_rule%s_%s_valueflag%s' % (str(single_amount), current_predicate, str(j))
                    if j != c-1:
                        VAR_text = VAR_text + '|'
                VAR_text = VAR_text + ') & ('
                triggerflag = 'new_rule%s_%s_triggerflag' % (str(single_amount), current_predicate)
                self.__class__.new_flag_dic.update({triggerflag: current_predicate})
                VAR_text = VAR_text + triggerflag
                VAR_text = VAR_text + '))->('
                VAR_text = VAR_text + current_predicate + ' != ' + current_predicate + LAST_STATE
                VAR_text = VAR_text + '))'
                # 取值flag做condition
                VAR_text = VAR_text + ' & '
                possible_value = []
                if 'boolean' in a:
                    possible_value = ['FALSE', 'TRUE']
                # 数值类的处理有问题
                elif '..' in a:
                    #lower = int(a.split('..')[0])
                    #upper = int(a.split('..')[1])
                    possible_value = self.number_abstract_candidate[current_predicate]#list(range(lower, upper + 1))
                elif '{' in a:
                    possible_value = a.replace('{', '').replace('}', '').split(',')
                # 数值类的处理有问题，导致每个值都是一个谓词
                for am in range(c):
                    VAR_text = VAR_text + '((new_rule%s_%s_valueflag%s)->(%s = %s))' % (str(single_amount), current_predicate, str(am),
                                                                                        current_predicate, possible_value[am])


                    # 数值类
                    if current_predicate in NUMBER_ABSTRACT and current_predicate in self.logicall_eal:
                        # rise前缀
                        VAR_text = VAR_text + '& (((' + triggerflag + '&' + 'new_rule%s_%s_valueflag%s' % (str(single_amount), current_predicate,  str(am)) + ') & '
                        VAR_text = VAR_text + '(' + 'new_rule%s_%s_valueflag%s_%s' % (str(single_amount), current_predicate, str(am), 'rise') + '))'
                        # rise后缀
                        VAR_text = VAR_text + '->(%s = %s))' % (current_predicate + LAST_STATE, str(int(possible_value[am]) + CHANNEL_INTERACTION_CONFIG_PER_TIME[current_predicate]))
                        # drop前缀
                        VAR_text = VAR_text + '& (((' + triggerflag + '&' + 'new_rule%s_%s_valueflag%s' % (str(single_amount), current_predicate,  str(am)) + ') & '
                        VAR_text = VAR_text + '(' + 'new_rule%s_%s_valueflag%s_%s' % (str(single_amount), current_predicate, str(am), 'drop') + '))'
                        # drop后缀
                        VAR_text = VAR_text + '->(%s = %s))' % (current_predicate + LAST_STATE, str(int(possible_value[am]) - CHANNEL_INTERACTION_CONFIG_PER_TIME[current_predicate]))


                    if am != c-1:
                        VAR_text = VAR_text + '&'

                    self.__class__.new_flag_dic.update({'new_rule%s_%s_valueflag%s' % (str(single_amount), current_predicate, str(am)): possible_value[am]})
                # action
                if i != predicate_amount - 1:
                    VAR_text = VAR_text + ' & '
                else:
                    VAR_text = VAR_text + ':'
                    VAR_text = VAR_text + action
                    VAR_text = VAR_text + ';\n'
        return VAR_text


    def __Delay(self, name1, upper_limit, name2, trigger_condition):
        s = '''     init(%s) := 0;
     next(%s) :=
            case
                %s: %s;
                %s.timer = 1: 0;
                TRUE: %s;
            esac;\n\n''' % (name1, name1, trigger_condition, upper_limit, name2, name1)
        return s

    def abstract_model(self, directory):
        begin_time = time.time()
        # 如果是某谓词的next，则使用剩下谓词
        curr_dir = os.getcwd()
        MODULE_RUNIN = module_RUNIN(20)
        self.generate_flag_original_amount()
        VAR_text = self.build_VAR()
        INVAR_text = self.build_INVAR()
        ASSIGN_text = self.__build_ASSIGN()
        MOUDLUE_MAIN = 'MODULE main\n' + VAR_text + INVAR_text + ASSIGN_text
        self.smv_text = MODULE_RUNIN + MOUDLUE_MAIN
        file = open(directory + r'\abstract%d.txt' % ModelAbstractor.ID, 'w+', encoding='utf-8')
        file.write(self.smv_text)
        # file.write(ASSIGN_text)
        file.close()
        end_time = time.time()
        abstract_time = float(end_time - begin_time) * 100
        return abstract_time

    def __NOT_RULE_RELATEED_ASSIGN(self, attribute_not_rule_related, attribute_not_rule_related_dic):
        step = ''
        # init之后的第二状态开始
        cnt = 2
        for i in range(1, self.upperlimit):
            if i != self.upperlimit - 1:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + attribute_not_rule_related_dic[
                    i].replace('\r', '') + ';\n'
                cnt += 1
            # 区别末尾
            else:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + attribute_not_rule_related_dic[
                    i].replace('\r', '') + ';'
                cnt += 1
        s = '''
     next(%s):=
       case\n''' % (attribute_not_rule_related) + step + '''
         TRUE: %s;
       esac;\n\n''' % attribute_not_rule_related
        return s


    def __UNAFFECTED_IMMEDIATE_ENVIROMENT_ASSIGN(self, unaffected_environment_dic_key,
                                                unaffected_environment_dic_key_count, value,
                                                unaffected_environment_dic_var):
        step = ''
        # init之后的第二状态开始
        cnt = 2
        for i in range(1, self.upperlimit):
            if i != self.upperlimit - 1:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + unaffected_environment_dic_var[i].replace('\r', '') + ';\n'
                cnt += 1
            # 区别末尾
            else:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + unaffected_environment_dic_var[i].replace('\r', '') + ';'
                cnt += 1
        s = '''
     init(%s):=%s;
     next(%s):=
       case\n''' % (unaffected_environment_dic_key,
            unaffected_environment_dic_var[0].replace('\r', '').replace('\n', ''),
            unaffected_environment_dic_key) + step + '''
         TRUE: %s;
       esac;\n\n''' % value
        return s


    # 它包含TAP规则
    def __AFFECTED_IMMEDIATE_ENVIROMENT_ASSIGN(self, affected_environment_dic_key,
                                                affected_environment_dic_key_count, value,
                                                affected_environment_dic_var):
        step = ''
        # init之后的第二状态开始
        cnt = 2
        for i in range(1, self.upperlimit):
            if i != self.upperlimit - 1:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + affected_environment_dic_var[i].replace('\r', '') + ';\n'
                cnt += 1
            # 区别末尾
            else:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + affected_environment_dic_var[i].replace('\r', '') + ';'
                cnt += 1
        s = '''
     init(%s):=%s;
     next(%s):=
       case\n''' % (affected_environment_dic_key,
            affected_environment_dic_var[0].replace('\r', '').replace('\n', ''),
            affected_environment_dic_key) + step + '''
         TRUE: %s;
       esac;\n\n''' % value
        return s



    def __UNAFFECTED_EXTENDED_ENVIROMENT_ASSIGN(self, unaffected_environment_dic_key,
                                                unaffected_environment_dic_key_count, value,
                                                unaffected_environment_dic_var):
        step = ''
        # init之后的第二状态开始
        cnt = 2
        for i in range(1, self.upperlimit):
            if i != self.upperlimit - 1:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + unaffected_environment_dic_var[
                    i].replace('\r', '') + ';\n'
                cnt += 1
            # 区别末尾
            else:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + unaffected_environment_dic_var[
                    i].replace('\r', '') + ';'
                cnt += 1
        s = '''     init(%s):=1;
     next(%s):=
       case
         next(%s)!=%s & %s =0: 1;
         %s = 1: 0;
         TRUE: %s;
       esac;

     init(%s):=%s;
     next(%s):=
       case\n''' % (
            unaffected_environment_dic_key_count, unaffected_environment_dic_key_count, unaffected_environment_dic_key,
            unaffected_environment_dic_key, unaffected_environment_dic_key_count, unaffected_environment_dic_key_count,
            unaffected_environment_dic_key_count, unaffected_environment_dic_key,
            unaffected_environment_dic_var[0].replace('\r', '').replace('\n', ''),
            unaffected_environment_dic_key) + step + '''
         %s = 1: %s;
         %s = 0: %s;
         TRUE: %s;
       esac;\n\n''' % (
                unaffected_environment_dic_key_count, unaffected_environment_dic_key,
                unaffected_environment_dic_key_count,
                value, unaffected_environment_dic_key)
        return s

    def __AFFECTED_EXTENDED_ENVIROMENT_ASSIGN(self, affected_environment_dic_key,
                                                affected_environment_dic_key_count, value,
                                                affected_environment_dic_var):
        #print('AFFECTED_EXTENDED_ENVIROMENT_ASSIGN')
        #print(affected_environment_dic_key)
        enviroment_var = affected_environment_dic_key
        enviroment_count = enviroment_var + ENVIRONMENT_COUNT
        category = ''
        # 应该只找CHANNEL_INTERACTION_CONFIG_LIST和目前属性的交集 交集 交集
        for cb in CHANNEL_INTERACTION_CONFIG_LIST:
            if affected_environment_dic_key == cb.name:
                if len(cb.threshold) == 2:
                    category += 'one'
                elif len(cb.threshold) == 4:
                    category += 'two'
                break

        step = ''
        # init之后的第二状态开始
        cnt = 2
        for i in range(1, self.upperlimit):
            if i != self.upperlimit - 1:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + affected_environment_dic_var[
                    i].replace('\r', '') + ';\n'
                cnt += 1
            # 区别末尾
            else:
                step = step + '         ' + 'next(step) = ' + str(cnt) + ': ' + affected_environment_dic_var[
                    i].replace('\r', '') + ';'
                cnt += 1

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

        init(%s):=%s;
        next(%s):=
            case\n''' % (
                enviroment_count, enviroment_count, enviroment_var, enviroment_var, enviroment_count, enviroment_count,
                enviroment_count, enviroment_var, affected_environment_dic_var[0], enviroment_var) + '''
               %s>=0 & %s<%s: %s;
               %s>=%s: %s;
               --因为顺序执行，所以下面肯定是smoke_clear=-1
               %s = 1: %s;
               %s = 0: %s;
               TRUE: %s;
             esac;\n\n''' % (
                enviroment_var + '_CONFIG', enviroment_var + '_CONFIG', enviroment_var + '_threshold', v1,
                enviroment_var + '_CONFIG', enviroment_var + '_threshold', v2,
                enviroment_count, enviroment_var, enviroment_count, value, enviroment_var)
        elif category == 'two':
            l = self.get_var_value(enviroment_var).split('..')
            upper = l[1]
            down = l[0]
            #print('affected_environment_dic_key')
            #print(affected_environment_dic_key)
            s = '''     
    init(%s):=%s;     
    next(%s):=
        case\n''' % (enviroment_var, affected_environment_dic_var[0].replace('\n', '').replace('\r', ''), enviroment_var) + '''
          -- 如果在threshold范围内，则温度不变
          %s<%s & %s>%s: %s;
          %s>=%s & %s<=%s: %s;
          %s<=%s & %s>=%s: %s;
          TRUE: %s;
        esac;\n\n''' % (enviroment_var + '_CONFIG', enviroment_var + '_rise_threshold',
                        enviroment_var + '_CONFIG', enviroment_var + '_drop_threshold', enviroment_var,
                        enviroment_var + '_CONFIG', enviroment_var + '_rise_threshold',
                        enviroment_var + ' + ' + str(CHANNEL_INTERACTION_CONFIG_PER_TIME[enviroment_var]), upper,
                        enviroment_var + ' + ' + str(CHANNEL_INTERACTION_CONFIG_PER_TIME[enviroment_var]),
                        enviroment_var + '_CONFIG', enviroment_var + '_drop_threshold',
                        enviroment_var + ' - ' + str(CHANNEL_INTERACTION_CONFIG_PER_TIME[enviroment_var]), down,
                        enviroment_var + ' - ' + str(CHANNEL_INTERACTION_CONFIG_PER_TIME[enviroment_var]),
                        enviroment_var)
        # 加入smoke_CONFIG
        s = s + generate_channel_based_config(affected_environment_dic_key, self.entity_attribute_list)
        return s


    def step_text(self):
        step_text = '''    init(step) := 1;
    next(step) :=
        case
            step < %d & step > 0: step + 1;
            step = %d: 0;
            TRUE: step;
    esac;\n\n''' % (self.upperlimit, self.upperlimit)
        return step_text
