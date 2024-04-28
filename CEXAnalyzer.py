from CONST import EXTENDED_ENVIRONMENT, LAST_STATE, ENVIRONMENT_COUNT, UNAFFECTED_EXTENDED_ENVIRONMENT, TAB, NUMBER_ABSTRACT, CHANNEL_INTERACTION_CONFIG_PER_TIME
from ModelAbstractor import ModelAbstractor, find_action_in_spec, find_info_in_spec
import re

class CEXAnalyzer(object):
    ID = 0
    entity_attribute_list = {}

    def __init__(self, cex_trace, spec, entity_attribute_list,  entity_rule_list,  spurious_standard):
        self.__class__.ID += 1
        self.states = cex_trace
        self.spec = spec[0]
        self.violating_type = spec[1]
        self.__class__.entity_attribute_list = entity_attribute_list
        self.spurious_standard = spurious_standard
        self.entity_attribute_list = entity_attribute_list
        self.entity_rule_list = entity_rule_list
        # 安全属性中的
        self.entity_attribute = find_action_in_spec(self.violating_type, self.spec)[0]
        self.new_rule_amount = ModelAbstractor.NEW_RULE_AMOUNT
        self.violating_state_position = self.find_violating_state()

    #def find_violating_state(self):
        '''if self.violating_type == 'liveness':
            # r'--LTLSPEC G((smoke=detected & smoke != smoke_last)->F(runin_fan.switchCap.switch_on_0.timer>1 & fan.switchCap.switch = on))'
            # G((smoke = detected & smoke != smoke_last)->F((fan.switchCap.switch = on) U (smoke = clear)))
            property_info = self.spec.replace('--LTLSPEC G(', '').replace('(', '').replace(')', '').replace(' ', '').split('->F')
            # smoke=detected
            front_state_in_property = property_info[0].split('&')[0]
            # smoke_last
            last_state = property_info[0].split('&')[1].split('!=')[1]
            # smoke=clear
            until_info = property_info[1].split('U')[1]
            # fan.switchCap.switch
            end_state_in_property = property_info[1].split('U')[0].split('=')[0]
            # on
            end_state_value = [property_info[1].split('U')[0].split('=')[1]]
            # 除了on的其他值，意思是这些值的出现就是我们要找的
            value, value_amount = self.get_var_value_and_amount(end_state_in_property)
            value = list(set(value.replace('{', '').replace('}', '').split(',')).difference(set(end_state_value)))
            value_list = []
            for i in range(len(value)):
                # fan.switchCap.switch=off等取值就是我们要找的
                value_list.append(end_state_in_property + ' = ' + value[i])
            front_position = []
            F_violating_state_position = []
            U_state_position = []
            state_count = -1
            for state in self.states:
                #print(state)
                state_count += 1
                # # 找到前置状态 'smoke = detected'
                flag3 = 0
                flag4 = 0

                # 处理一个状态里的属性值
                # 遍历的顺序是从前往后，所以保证了F和X的有序性
                for state_attribute in state:
                    # 找到前置状态 'smoke = detected'
                    if front_state_in_property in state_attribute.replace(' ', ''):
                        #print('state_attribute')
                        #print(state_attribute)
                        flag3 = 1
                        # break体现了未来，并不，因为是索引之间的关系判断
                        continue
                    # smoke!=smoke_last
                    if last_state in state_attribute:
                        last_state_value = state_attribute.replace(' ', '').replace('\r', '').split('=')[1]
                        # smoke=detected,smoke_last=clear
                        if last_state_value != front_state_in_property.split('=')[1]:
                            #print('last_state_value')
                            #print(last_state_value)
                            flag4 = 1
                            continue
                    # 先判断fan.switch，判断为除了安全属性之外的其它动作出现，之后才是runin,因为build_VAR的方法
                    for value_ele in value_list:
                        # 'fan.switchCap.switch = off'
                        if value_ele in state_attribute:
                            #print('value_ele')
                            #print(value_ele)
                            F_violating_state_position.append(state_count)
                            continue
                    # 'runin_fan.switchCap.switch_on_0.timer = 1'
                    if until_info in state_attribute.replace(' ', ''):
                        #print('until_info')
                        #print(until_info)
                        U_state_position.append(state_count)
                        continue
                # smoke=detected smoke!=smoke_last 同时存在才算
                if flag3 and flag4:
                    front_position.append(state_count)
            # 有效性判断，F_violating_state_position的元素在front中某个元素和U中某个元素的区间中，则为一对冲突状态
            #'front_position')
            #print(front_position)
            #print('F_violating_state_position')
            #print(F_violating_state_position)
            #print('U_state_position')
            #print(U_state_position)
            # 去掉U中比front中最小元素小或等于的，因为F
            cnt_list = []
            min_front_position = min(front_position)
            for i in range(len(U_state_position)):
                if U_state_position[i] <= min_front_position:
                    cnt_list.append(i)
            # 用正序counter，前提是cnt_list有序
            #print(cnt_list)
            counter = 0
            for index in cnt_list:
                index = index - counter
                U_state_position.pop(index)
                counter += 1
            #print('U_state_position')
            #print(U_state_position)
            # 如果U为空，说明没有出现过clear，即F基本都不满足
            # 没U就为false
            if not U_state_position:
                length = len(F_violating_state_position)
                flag_arr = [0] * length
                for i in range(length):
                    for j in front_position:
                        # > 体现了 F
                        if F_violating_state_position[i] > j:
                            flag_arr[i] = 1
                            break
                cnt = -1
                cnt_list = []
                for i in flag_arr:
                    cnt += 1
                    if i != 1:
                        cnt_list.append(cnt)
                # 排除为0的，剩下的是有效性
                # 用正序counter，前提是cnt_list有序
                counter = 0
                for index in cnt_list:
                    index = index - counter
                    F_violating_state_position.pop(index)
                    counter += 1'''


        '''
            length = len(F_violating_state_position)
            flag_arr = [0] * length
            for i in range(length):
                for j in front_position:
                    # > 体现了 F
                    if F_violating_state_position[i] > j:
                        flag_arr[i] = 1
                        break
            cnt = -1
            cnt_list = []
            for i in flag_arr:
                cnt += 1
                if i != 1:
                    cnt_list.append(cnt)
            # 排除为0的，剩下的是有效性
            # 用正序counter，前提是cnt_list有序
            counter = 0
            for index in cnt_list:
                index = index - counter
                F_violating_state_position.pop(index)
                counter += 1'''
        '''return F_violating_state_position'''

    def find_violating_state(self):
        if self.violating_type == 'state-event':
            # G((weather.rain = raining)->!X(window.switch = close))  只能处理单event
            # 'weather.rain = raining', 'window.switch = close'
            property_info = self.spec.replace('--LTLSPEC G(', '').replace('(', '').replace(')', '').split('->X')
            # print(property_info)
            # G((temperatureMeasurement.temperature = 15 & temperatureMeasurement.temperature_last = 16)->X(heater.switch = on))
            front = property_info[0].split('&')
            # temperatureMeasurement.temperature = 15
            state_in_property = front[0].replace(' ', '')
            # 非数值类
            last_state = ''
            re_pattern = r'[a-zA-Z0-9._]+(.*?)[a-zA-Z0-9._]+'
            # 返回string中所有与pattern匹配的全部字符串,返回形式为数组。返回>=
            compare_sign = re.findall(re_pattern, state_in_property)[0]
            #print('compare_sign')
            #print(compare_sign)
            # 数值类
            not_number_flag = 0
            if state_in_property.split(compare_sign)[0] not in NUMBER_ABSTRACT:
                not_number_flag = 1
            #print('not_number_flag')
            #print(not_number_flag)
            if not_number_flag:
                last_state += front[1].split('!=')[1].replace(' ', '')
                #print('last_state')
                #print(last_state)
            # 数值类
            else:
                last_state += front[1].split('=')[0].replace(' ', '')
                #print('last_state')
                #print(last_state)
            # last_state_in_property = []
            event_in_property = property_info[1].split('=')[0].replace(' ', '')
            event_value = [property_info[1].split('=')[1].replace(' ', '')]
            value, value_amount = self.get_var_value_and_amount(event_in_property)
            # 默认event为枚举类型
            value = list(set(value.replace('{', '').replace('}', '').split(',')).difference(set(event_value)))
            value_list = []
            for i in range(len(value)):
                # print(end_state_in_property + ' = ' + value[i])
                value_list.append(event_in_property + ' = ' + value[i])

            state_count = -1
            front_position = []

            violating_state_position = []
            #for kkk in self.states:
            #   print(kkk)
            for state in self.states:
                state_count += 1
                flagA = 0
                flagB = 0
                # 处理一个状态里的属性值
                for state_attribute in state:
                    # 找到前置状态
                    # 正属性,反属性也是要找同一个冲突状态？
                    #if not ('->!' in self.spec):
                    # state_attribute为
                    if state_in_property in state_attribute.replace(' ', ''):
                        flagA = 1
                        continue

                    # smoke!=smoke_last
                    if last_state in state_attribute:
                        last_state_value = state_attribute.replace(' ', '').replace('\r', '').split('=')[1]
                        # smoke=detected,smoke_last=clear
                        if not_number_flag:
                            if last_state_value != state_in_property.split('=')[1]:
                                #print('last_state_value')
                                #print(last_state_value)
                                flagB = 1
                                continue
                        # 数值类
                        else:
                            if last_state_value == front[1].split('=')[1].replace(' ', ''):
                                #print('数值类')
                                #print(last_state_value)
                                #print(front[1].split('=')[1].replace(' ', ''))
                                flagB = 1
                                continue

                    # 体现X的，不用体现，依然是索引关系
                    # 'window.switch = open'
                    for value_ele in value_list:
                        if value_ele in state_attribute:
                            violating_state_position.append(state_count)
                            break
                    # 反属性也是要找同一个冲突状态？
                    '''else:
                        if state_in_property in state_attribute:
                            front_position.append(state_count)
                            continue
                        # 体现X的，不用体现，依然是索引关系
                        for value_ele in value_list:
                            if value_ele in state_attribute:
                                violating_state_position.append(state_count)
                                break'''
                    # smoke=detected smoke!=smoke_last 同时存在才算
                if flagA and flagB:
                    front_position.append(state_count)

            #print(front_position)
            #print(violating_state_position)
            #print(front_position)
            #print(violating_state_position)
            # 有效性判断，violating_state_position的元素都在front下一个,则是冲突
            length = len(violating_state_position)
            #print(violating_state_position)
            #print(front_position)
            flag_arr = [0] * length
            for i in range(length):
                for j in front_position:
                    # -1体现了X
                    if violating_state_position[i] - 1 == j:
                        flag_arr[i] = 1
                        break
            cnt = -1
            cnt_list = []
            for i in flag_arr:
                cnt += 1
                if i != 1:
                    cnt_list.append(cnt)
            # 排除为0的，剩下的是有效性
            # 用正序counter，前提是cnt_list有序
            counter = 0
            for index in cnt_list:
                index = index - counter
                violating_state_position.pop(index)
                counter += 1
            return violating_state_position

        elif self.violating_type == 'state-state':
            # G((weather.rain = raining)->!X(window.switch = close))  只能处理单event
            # 'weather.rain = raining', 'window.switch = close'
            # temperatureMeasurement.temperature > 22
            property_info = self.spec.replace('--LTLSPEC G(', '').replace('(', '').replace(')', '').split('->')
            # print(property_info)
            front = property_info[0].split('&')
            state_in_property = front[0].replace(' ', '')
            if '>' in state_in_property or '<' in state_in_property:
                sign = ''
                if '>=' in state_in_property:
                    sign = '>='
                elif '<=' in state_in_property:
                    sign = '<='
                elif '<' in state_in_property:
                    sign = '<'
                elif '>' in state_in_property:
                    sign = '>'
                elif '=' in state_in_property:
                    sign = '='
                # temperatureMeasurement.temperature
                a_name = state_in_property.split(sign)[0]
                a_value = state_in_property.split(sign)[1]
            last_state = front[1].split('=')[1].replace(' ', '')
            # last_state_in_property = []
            event_in_property = property_info[1].split('=')[0].replace(' ', '')
            event_value = [property_info[1].split('=')[1].replace(' ', '')]
            value, value_amount = self.get_var_value_and_amount(event_in_property)
            # 默认event为枚举类型
            value = list(set(value.replace('{', '').replace('}', '').split(',')).difference(set(event_value)))
            value_list = []
            for i in range(len(value)):
                # print(end_state_in_property + ' = ' + value[i])
                value_list.append(event_in_property + ' = ' + value[i])

            state_count = -1
            front_position = []
            violating_state_position = []
            #for kkk in self.states:
            #   print(kkk)
            for state in self.states:
                state_count += 1
                flagA = 0
                flagB = 0
                # 处理一个状态里的属性值
                for state_attribute in state:
                    # 找到前置状态
                    # 正属性,反属性也是要找同一个冲突状态？
                    #if not ('->!' in self.spec):
                    # state_attribute为
                    if state_in_property in state_attribute.replace(' ', ''):
                        flagA = 1
                        continue

                    # smoke!=smoke_last
                    if last_state in state_attribute:
                        last_state_value = state_attribute.replace(' ', '').replace('\r', '').split('=')[1]
                        # smoke=detected,smoke_last=clear
                        if last_state_value == state_in_property.split('=')[1]:
                            #print('last_state_value')
                            #print(last_state_value)
                            flagB = 1
                            continue

                    # 体现X的，不用体现，依然是索引关系
                    # 'window.switch = open'
                    for value_ele in value_list:
                        if value_ele in state_attribute:
                            violating_state_position.append(state_count)
                            break
                    # 反属性也是要找同一个冲突状态？
                    '''else:
                        if state_in_property in state_attribute:
                            front_position.append(state_count)
                            continue
                        # 体现X的，不用体现，依然是索引关系
                        for value_ele in value_list:
                            if value_ele in state_attribute:
                                violating_state_position.append(state_count)
                                break'''
                    # smoke=detected smoke!=smoke_last 同时存在才算
                if flagA and flagB:
                    front_position.append(state_count)

            #print(front_position)
            #print(violating_state_position)

            # 有效性判断，violating_state_position的元素都在front下一个,则是冲突
            length = len(violating_state_position)
            #print(violating_state_position)
            #print(front_position)
            flag_arr = [0] * length
            for i in range(length):
                for j in front_position:
                    # ==体现了同状态
                    if violating_state_position[i] == j:
                        flag_arr[i] = 1
                        break
            cnt = -1
            cnt_list = []
            for i in flag_arr:
                cnt += 1
                if i != 1:
                    cnt_list.append(cnt)
            # 排除为0的，剩下的是有效性
            # 用正序counter，前提是cnt_list有序
            counter = 0
            for index in cnt_list:
                index = index - counter
                violating_state_position.pop(index)
                counter += 1
            return violating_state_position

    def get_var_value_and_amount(self, var):
        var_amount = 0
        VAR_text = ''
        for key, value in self.__class__.entity_attribute_list.items():
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
                    if '..' in value:
                        var_amount = int(value.split('..')[1]) + abs(int(value.split('..')[0])) + 1
                    else:
                        var_amount = 2
                break
        return VAR_text, var_amount

    def spurious(self, iteration_limit):
        # 第一轮
        if iteration_limit == 1:
            mode = 'iteration'
            return mode
        # 如果有冲突状态，其中的某些状态可行
        if self.violating_state_position:
            # 以第一个冲突状态为基准，它之前和本身不出现冲突状态，说明被消除了，则认为不spurious之后的不管可能是其它导致。如果冲突状态仍存在则Spurious
            for i in self.violating_state_position:
                if i <= self.spurious_standard[0]:
                    mode = 'iteration'
                    # mode = 'find_possible'
                    return mode
            # 之前和本身不出现冲突状态
            # mode = 'iteration'
            mode = 'find_possible'
        # 如果没有冲突状态直接可行
        else:
            mode = 'find_possible'
        return mode

    def collect_flag_var(self, mode):
        if mode == 'iteration':
            res = '    !('
            for single_attribute in self.states[0]:
                # 排除wait_trigger_flag，因为不通过flag找
                if 'flag' in single_attribute and 'wait' not in single_attribute:
                    res += single_attribute.replace('\n', '').replace('\r', '') + ' & '
            res = res[:-2] + ')\n\n'
        # 第一次
        else:
            res = ''
        return res


    def map_delay2TAP(self, li):
        res = {}
        cnt = 0
        flag_res = ''
        for i in li:
            if '_abstract_flag' in i:
                flag_res += i + ' && '
                flag = i.split('=')[0]
                attribute_name = flag.split('_')[1]
                res.update({attribute_name: []})

        for i in li:
            if '_abstract_flag' in i:
                # 遍历规则dic找出
                flag = i.split('=')[0]
                attribute_name = flag.split('_')[1]
                action_in_flag = flag.split('_')[2]
                rule_index = int(flag.split('_')[3])
                flag_var = int(i.split('=')[1])
                tap_set = self.entity_rule_list[attribute_name]

                # 存起来后续用索引来处理
                tmp = []
                for j in tap_set:
                    # 默认从有延时到无延时所以j[-1] != 1
                    if action_in_flag in j[-2] and (len(j[-1]) != 1):
                        tmp.append(j)
                # 为对应索引
                rule = tmp[rule_index]
                trigger = rule[0]
                condtion = rule[1]
                # action & delay
                if int(flag_var) == 0:
                    # 无delay只有一个元素
                    action = [rule[2][0]]
                    delay = [0, 'none']
                else:
                    action = [rule[2]]
                    delay = [int(flag_var), 0, 'none']

                res[attribute_name].append([trigger, condtion, action, delay])
        return res, flag_res


    def map2TAP(self, tap_amount, para_entity_rule_list, abstract_mode):
        rule_list_copy = []
        new_rule_dic = {}
        if para_entity_rule_list:
            for entity_attribtue, tap_set in para_entity_rule_list.items():
                for single_rule in tap_set:
                    new_rule_dic.update({entity_attribtue: []})
                    rule_list_copy.append([entity_attribtue, single_rule])
        else:
            new_rule_dic.update({self.entity_attribute: []})
        new_rule_dic.update({self.entity_attribute: []})
        li = self.collect_flag_var('iteration').replace(' ', '').replace('\n', '').replace('(', '').replace(')', '').replace('!', '').split('&')

        # 得到各原规则的谓词取值
        rule_clasify = []
        for rule_index in range(tap_amount):
            single_rule_list = []
            for i in li:
                # 原规则
                if 'original_flag_rule%d' % rule_index in i:
                    single_rule_list.append(i)
                    continue
            rule_clasify.append(single_rule_list)
        # 得到各新规则的谓词取值
        rule_clasify_new_rule = []
        for rule_index in range(self.new_rule_amount):
            single_rule_list = []
            for i in li:
                # 新规则
                if 'new_rule%d' % rule_index in i:
                    single_rule_list.append(i)
                    continue
            rule_clasify_new_rule.append(single_rule_list)


        #print(rule_clasify)
        #print(rule_clasify_new_rule)
        # 产生自动机层面规则，映射到上层TAP规则, 按照main里给的规则格式
        #if not ModelAbstractor.original_flag_dic:
        # 首先是现有规则，original_flag属于trigger确定的
        count = -1  # 统计目前是到第几条规则了
        for single_rule in rule_clasify:
                count += 1
                # 对应的原规则
                rule = rule_list_copy[count][1]
                # trigger = rule[0]
                # condition = rule[1]
                # action = rule[2]
                # delay = rule[3]
                for single_flag in single_rule:
                    # 如果有效就添加对应的属性值
                    if 'TRUE' in single_flag:
                        # 添加对应的属性值
                        for key, value in ModelAbstractor.original_flag_dic.items():
                            # 因为是original_flag，所以直接当condition
                            if single_flag.split('=')[0] == key:
                                if 'none' in rule[1]:
                                    # 去掉none
                                    rule[1].remove('none')
                                # 然后加条件
                                rule[1].append(value)
                                break
                new_rule_dic[rule_list_copy[count][0]].append(rule)
        #print(ModelAbstractor.original_flag_dic)
        #print(ModelAbstractor.new_flag_dic)
        # 之后是新规则，如果有新规则的话
        #if not ModelAbstractor.new_flag_dic:
        count = -1  # 统计目前是到第几条规则了
        total_condition = []
        #print('rule_clasify_new_rule')
        #print(rule_clasify_new_rule)


        for single_rule in rule_clasify_new_rule:
                # 用于记录数值类的last变量
                record_num = []
                for single_flag in single_rule:
                    # 如果有效就添加对应的属性值
                    if 'TRUE' in single_flag:
                        if 'rise' in single_flag or 'drop' in single_flag:
                            record_num.append(single_flag)
                count += 1
                condition = []
                for single_flag in single_rule:
                    # 如果有效就添加对应的属性值
                    if 'TRUE' in single_flag:
                        # 添加对应的属性值
                        for key, value in ModelAbstractor.new_flag_dic.items():
                            # 因为是new_flag，所以直接当新规则
                            if single_flag.split('=')[0] == key:
                                # print("single_flag.split('=')[0]")
                                # print(single_flag.split('=')[0])
                                # 非数值类
                                if key.split('_')[2] not in NUMBER_ABSTRACT:
                                    # condition
                                    condition.append(key + '=' + str(value))
                                # 数值类
                                else:
                                    if 'trigger' in key:
                                        condition.append(key + '=' + str(value))
                                        # print(condition)
                                        continue
                                    # condition
                                    rise_flag = 0
                                    drop_flag = 0
                                    #print('record_num')
                                    #print(record_num)
                                    #print(key + '_rise=TRUE')
                                    if key + '_rise=TRUE' in record_num:
                                        rise_flag = 1
                                    else:
                                        drop_flag = 1
                                    # print(rise_flag)
                                    # print(drop_flag)

                                    if rise_flag:
                                        condition.append(key + '<' + str(value+1))
                                    else:
                                        condition.append(key + '>' + str(value-1))
                                # print(condition)
                                break
                total_condition.append(condition)
        # 从condition中挑出trigger
        total_trigger = []
        #print(total_trigger)
        #print(total_condition)
        for single_rule_condition in total_condition:
            # 先找到trigger
            tmp = ''
            for i in single_rule_condition:
                if 'trigger' in i:
                    # 从condition删除这个元素同时加入trigger中
                    tmp = tmp + i
                    single_rule_condition.remove(i)
                    break
            # 排除纯原规则没有新规则的情况
            if tmp == '':
                break
            # 如果有抽象新规则，则进行如下
            attribute_name = tmp.split('_')[2]
            # 根据刚找到的trigger定取值
            for i in single_rule_condition:
                if attribute_name in i:
                    # 从condition删除这个元素同时加入trigger中
                    # 非数值类情况
                    re_pattern = r'[a-zA-Z0-9._]+(.*?)[a-zA-Z0-9._]+'
                    compare_sign = re.findall(re_pattern, i)[0]
                    if i.split('_')[2] not in NUMBER_ABSTRACT:
                        total_trigger.append([i.split('_')[2] + compare_sign + i.split(compare_sign)[1]])
                    # 数值类情况根据last flag判断大于小于符号
                    else:
                        # val = int(i.split('=')[1])
                        total_trigger.append([i.split('_')[2] + compare_sign + i.split(compare_sign)[1]])
                    #print(r"i.split('_')[2]")
                    #print(i.split('_')[2])
                    single_rule_condition.remove(i)
                    break

        # 将flag组合成新规则
        for i in range(self.new_rule_amount):
            if total_trigger:
                #print('total_trigger')
                #print(total_trigger)
                #print('total_condition')
                #print(total_condition)
                # trigger
                trigger = total_trigger[i]
                # condition
                condition = []
                if not total_condition[i]:
                    condition = ['none']
                else:
                    # 将total_condition的flag映射为对应的取值
                    for tc in total_condition[i]:
                        condition.append(tc.split('_')[2] + '=' + tc.split('=')[1])
                # action默认取安全属性里的
                action = [find_action_in_spec(self.violating_type, self.spec)[1][0]]
                # delay，默认无延迟，无wait_trigger
                delay = [0, 'none']
                new_rule = [trigger, condition, action, delay]
                #print([trigger, condition, action, delay])
                entity_attribute = self.entity_attribute# find_action_in_spec(self.violating_type, self.spec)[0]
                new_rule_dic[entity_attribute].append(new_rule)


        # 得到延时标志位取值
        delay2TAP_res, flag_res = self.map_delay2TAP(li)
        print(flag_res)
        if delay2TAP_res:
            #print('delay2TAP_res')
            #print(delay2TAP_res)
            #print(new_rule_dic)
            for key, value in delay2TAP_res.items():
                #print(new_rule_dic[key])
                # 替换原规则
                for single_rule in value:
                    cnt = -1
                    for single_rule2 in new_rule_dic[key]:
                        #print(single_rule)
                        #print(single_rule2)
                        cnt += 1
                        # 如果trigger condition action的第一个相同，则为同一条规则，可以替换
                        if (single_rule[0] == single_rule2[0]) and (single_rule[1] == single_rule2[1]) \
                            and (single_rule[2][0] in single_rule2[-2]) and (len(single_rule2[-1]) == 3):
                                new_rule_dic[key][cnt] = single_rule
                                #print(single_rule)


                # new_rule_dic[key].append(single_rule)

        # [['smokeDetector.smoke=detected'], ['presenceSensor.presence = not_present'], ['on'], [-1]]
        #if abstract_mode == 'wait_trigger':

        wait_trigger_res = []
        if abstract_mode == 'wait_trigger':
            # 代表着entity.attribute的延时规则的第WAIT_TRIGGER_cnt条，将其none改为非none
            spec_info_list = find_info_in_spec(self.violating_type, self.spec)
            front_attribute = spec_info_list[0]
            front_attribute_value = spec_info_list[1]
            end_attribute = spec_info_list[2]
            end_attribute_value = spec_info_list[3]
            front = front_attribute + '=' + front_attribute_value

            rule_set = new_rule_dic[self.entity_attribute]
            extended_rule_cnt = -1
            cnt = -1
            for singlerule in rule_set:
                cnt += 1
                if len(singlerule[-1]) == 3:
                    extended_rule_cnt += 1
                    if extended_rule_cnt == ModelAbstractor.WAIT_TRIGGER_cnt:
                        tmp = singlerule
                        tmp[-1][-1] = 'wait_trigger ' + front
                        rule_set[cnt] = tmp
                        wait_trigger_res = tmp
                        break

        # 返回fix_flag and fix_TAP
        # new的情况
        if abstract_mode == 'new':
            return rule_clasify + rule_clasify_new_rule, new_rule_dic
        elif abstract_mode == 'present':
            return rule_clasify, new_rule_dic
        elif abstract_mode == 'wait_trigger':
            return wait_trigger_res, new_rule_dic
        else:
            return flag_res, new_rule_dic
'''        if rule_clasify and rule_clasify_new_rule:
            return rule_clasify + rule_clasify_new_rule, new_rule_dic
        # present情况
        elif rule_clasify:
            return rule_clasify, new_rule_dic
        elif rule_clasify_new_rule:
            return rule_clasify_new_rule, new_rule_dic
        else:
            return rule_clasify, new_rule_dic
'''