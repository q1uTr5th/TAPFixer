# 检验的同时，记录下反例信息
import time
import subprocess
from CONST import EXTENDED_ENVIRONMENT, LAST_STATE, ENVIRONMENT_COUNT, UNAFFECTED_EXTENDED_ENVIRONMENT, CHANNEL_INTERACTION_CONFIG_LIST


def get_all_VAR(entity_attribute_list, extended_action_index, entity_rule_list):
    tmp_dic = {}
    for key, value in entity_attribute_list.items():
        # 枚举类型 [0,1,2] [on,off]
        if type(value) == list:
            # 上一状态
            tmp_dic.update({key + LAST_STATE: value})
        # 数值类型 0..5  布尔类型 boolean
        elif '..' in value or value == 'boolean':
            # 上一状态
            tmp_dic.update({key + LAST_STATE: value})
        # 自然延时属性
        if key in EXTENDED_ENVIRONMENT:
            tmp_dic.update({key + ENVIRONMENT_COUNT: '0..1'})
        # channel-based interaction config
        for cb in CHANNEL_INTERACTION_CONFIG_LIST:
            if key == cb.name:
                tmp_dic.update({key + '_CONFIG': '-1..' + str(cb.threshold[1])})
                tmp_dic.update({key + '_threshold': str(cb.threshold[0]) + '..' + str(cb.threshold[1])})
                for i in cb.config_list:
                    attribute = i[0].split('=')[0].replace(' ', '')
                    # assign_value = i[0].split('=')[1].replace(' ', '')
                    config = i[1]
                    # 如果为最后的Not_handle
                    if attribute == 'not_handle':
                        if config > 0:
                            tmp_dic.update({key + '_not_handle_config': '0..' + str(config)})
                        else:
                            tmp_dic.update({key + '_not_handle_config': str(config) + '..0'})
                        continue
                    # 只加入和当前属性相关的
                    if attribute in entity_attribute_list:
                        if config > 0:
                            tmp_dic.update({key + '_' + attribute + '_config': '0..' + str(config)})
                        else:
                            tmp_dic.update({key + '_' + attribute + '_config': str(config) + '..0'})
                break

    # 延时多加变量
    for entity_attribute, total_index in extended_action_index.items():
        '''entity_attribute:[[],[1,5]]'''
        # entity_attribute: [[[trigger1,trigger2],condition,[action1,action2],[time1,time2,0,5,-1]] , rule2 ]
        tap_amount = len(total_index)
        for i in range(tap_amount):
            # 如果该规则无延时则跳过
            single_index = total_index[i]
            if single_index == []:
                continue
            # 当前属性需要处理的单条规则
            tap_set = entity_rule_list[entity_attribute]
            single_rule = tap_set[i]
            single_rule_actionSet = single_rule[2]
            single_rule_delaySet = single_rule[3]
            for j in single_index:
                # 添加delaywindow: 0..5;
                name1 = 'delay_' + entity_attribute + '_' + single_rule_actionSet[j] + '_' + str(i)
                tmp_dic.update({name1: '0..' + str(single_rule_delaySet[j])})
                # 添加runinwindow: RUNIN(delaywindow);
                name2 = 'runin_' + entity_attribute + '_' + single_rule_actionSet[j] + '_' + str(i)
                tmp_dic.update({name2+'.timer':  '0..' + str(single_rule_delaySet[j])})
    # 会改变字典的
    tmp_dic.update(entity_attribute_list)

    return tmp_dic


class ModelChecker(object):
    def __init__(self, smv_path, spec, entity_attribute_list, entity_rule_list):
        self.smv_path = smv_path
        self.spec = spec[0]
        self.entity_attribute_list, self.entity_rule_list = entity_attribute_list, entity_rule_list
        self.violating_type = spec[1]
        self.extended_action_index = self.__estimate_runin()
        # 改变了self.entity_attribute_list的值
        self.all_attribute_dic = get_all_VAR(self.entity_attribute_list, self.extended_action_index,
                                             self.entity_rule_list)
        #print('self.all_attribute_dic')
        #print(self.all_attribute_dic)
        self.all_attribute_list = []
        for attribute, value in self.all_attribute_dic.items():
            self.all_attribute_list.append(attribute)

    def __estimate_runin(self):
        # 存在延时action，记录数组下标，下标为延时属性
        res = {}
        for entity_attribute, tap_set in self.entity_rule_list.items():
            tap_amount = len(tap_set)
            # 一个循环处理同设备能力多条规则的一条
            total_res = []
            for i in range(tap_amount):
                # value[i]对应一条规则
                single_rule = tap_set[i]
                single_res = []
                for j in range(len(single_rule[-1])):
                    if type(single_rule[-1][j]) == type(1) and single_rule[-1][j] > 0:
                        single_res.append(j)
                total_res.append(single_res)
            if total_res:
                res.update({entity_attribute: total_res})
        '''entity_attribute:[[],[1,5]]'''
        return res

    def run_nusmv(self, run_mode, bound = '10'):
        # child = pexpect.spawn('ls -l')
        begin_time = time.time()
        # shell=True防止跳出窗口
        obj = subprocess.Popen('nuxmv -int ' + self.smv_path,
                               shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        cmd_out, cmd_error = '', ''
        if run_mode == 'normal':
            obj.stdin.write("read_model\n".encode())
            obj.stdin.write("flatten_hierarchy\n".encode())
            obj.stdin.write("encode_variables\n".encode())
            #obj.stdin.write("build_flat_model\n".encode())
            obj.stdin.write("build_model\n".encode())
            # LTL SPEC
            if 'LTLSPEC' in self.spec:
                cmd = 'check_ltlspec -p \"' + self.spec.split('SPEC ')[1] + '\"\n'
                print('检测指令：')
                print(cmd)
                # 从这里开始跑
                obj.stdin.write(cmd.encode())
                obj.stdin.close()
                # if '>!F(runin_fan.switchCap.switch_on_0.timer=1 & fan.switchCap.switch = on))' in self.spec:
                #    time.sleep(60)
            # CTL SPEC
            else:
                print(('check_ctlspec -p \"' + self.spec.split('SPEC ')[1] + '\"\n').encode())
                obj.stdin.write(('check_ctlspec -p \"' + self.spec.split('SPEC ')[1] + '\"\n').encode())
        else:
            obj.stdin.write("go_bmc\n".encode())
            specification = self.spec.split('SPEC ')[1].split('->')
            specification[0] = specification[0][:-1] + ' & step > %d)' % (int(bound) - 2)
            cmd = 'check_ltlspec_bmc -p \"' + specification[0] + '->' + specification[1]  + '\" -k ' + str(int(bound)) +'\n'
            #cmd = 'check_ltlspec_bmc -p \"' + self.spec.split('SPEC ')[1] + '\" -k ' + str(int(bound)+5) +'\n'
            print('检测指令：')
            print(cmd)
            cmd_out, cmd_error = obj.communicate(input=cmd.encode(), timeout=None)
            cmd_out = cmd_out.decode()
            cmd_error = cmd_error.decode()
            # 从这里开始跑
            #obj.stdin.write(cmd.encode())
            #obj.stdin.close()
            #cmd_error = obj.stderr.read().decode()
            #print(cmd_error)
            #while (True):
            #    cmd_out = obj.stdout.read().decode()
            #    print(cmd_out)
        if not(cmd_out):
            cmd_out = obj.stdout.read().decode()
            while (True):
                if cmd_out:
                    break
                cmd_out = obj.stdout.read().decode()
            obj.stdout.close()
            cmd_error = obj.stderr.read().decode()
        # NuSMV > -- specification  G x >= 0  is true\r\nNuSMV > -- specification  G x >= 0  is true\r\n
        out_res = []
        #spec_flag = 0

        if run_mode == 'normal':
            #print('-- no counterexample')
            #print(type(cmd_out))
            #print(cmd_out.split('nuXmv >'))
            for i in cmd_out.split('nuXmv >'):
                if '-- specification' in i:
                    out_res = i.split('\n')
        else:
            #print('-- no counterexample')
            #print(type(cmd_out))
            #print(cmd_out.split('-- no counterexample'))
            for i in cmd_out.split('-- no counterexample'):
                if '-- specification' in i:
                    #print('-- specification')
                    #print(i)
                    out_res = i.split('\n')
                    #spec_flag = 1

        #if not(spec_flag) and run_mode == 'anti':
        #    return [], [], '-1ms', 0
        if out_res == [] and run_mode == 'anti':
            end_time = time.time()
            verify_time = round(float(end_time - begin_time) * 1000, 3)
            return [], [], verify_time, 1
        '''for i in out_res:
            print(i)'''
        error_res = cmd_error
        obj.stderr.close()
        # 对子进程进行控制，处理完再进行之后步骤
        while True:
            # None 在运行, 0 正常结束
            if subprocess.Popen.poll(obj) is not None:
                break
        states = self.split_state(out_res, run_mode)
        loop_state_location = self.find_loop_state(states)
        states = self.complete_state(states, self.all_attribute_dic)
        property_satisfy = self.property_satisfaction(out_res, run_mode)
        end_time = time.time()
        verify_time = round(float(end_time - begin_time) * 1000, 3)

        return states, error_res, verify_time, property_satisfy

    # 找到loop，同时从状态变量里删除Loop
    def find_loop_state(self, states):
        # 'Loop starts here'
        res = 0
        state_count = -1
        for i in states:
            state_count += 1
            for j in i:
                if 'Loop starts here' in j:
                    res = state_count + 2
                    states[state_count].remove(j)
                    break
        return res

    # 分离出各状态
    def split_state(self, cex_trace, run_mode):
        states = []
        state = []
        state_flag = 0
        amount = 0
        ct = []
        if run_mode == 'normal':
            ct = cex_trace[4:]
            amount += len(ct)
        else:
            ct = cex_trace[5:]
            amount += len(ct)
        #print('ct')
        #print(ct)
        for i in ct:
            if '-> State:' in i or state_flag + 1 == amount:
                state_flag += 1
                # 排除第一个状态
                if state:
                    states.append(state)
                    state = []
            # 补充状态
            else:
                state_flag += 1
                state.append(i)
        # 排除LOOP的情况
        for j in range(states.count(['  -- Loop starts here\r'])):
            states.remove(['  -- Loop starts here\r'])
        return states
    # 补齐状态
    def complete_state(self, states, all_attribute_dic):
        # 如果当前状态数量不足，则copy上一状态，如此迭代
        # 从第二个状态开始
        state_count = 0
        for state in states[1:]:
            state_count += 1
            state_attribute = []
            # 获得当前状态的变量，用于之后求差集得到没有的变量
            for entity_attribute in state:
                for attribute, value in all_attribute_dic.items():
                    if attribute == entity_attribute.split('=')[0].replace(' ', ''):
                        state_attribute.append(attribute)
                        break
            # 求差集得到没有的变量
            ret = list(set(self.all_attribute_list) ^ set(state_attribute)) # 包含runin
            # 如果有差集，则补齐当前状态
            if ret:
                # 从上一状态补齐
                # k为缺的属性
                for k in ret:
                    # 因为从第二个状态开始，所以state_count-1
                    #print('k')
                    #print(k)
                    for last_state_attribute_assisgn in states[state_count - 1]:
                        # 如果仅仅是k in j排除不了count,last类型
                        if k == last_state_attribute_assisgn.split('=')[0].replace(' ', ''):
                            #print(last_state_attribute_assisgn.split('=')[0].replace(' ', ''))
                            state.append(last_state_attribute_assisgn)
                            break
        return states

    def property_satisfaction(self, cex_trace, run_mode):
        try:
            pbj = []
            if run_mode == 'normal':
                pbj = cex_trace[0]
            else:
                pbj = cex_trace[1]
            #print('property_satisfaction')
            #print(pbj)
            if 'false' in pbj:
                return 0
            else:
                return 1
        except:
            print('考虑更换活属性')
