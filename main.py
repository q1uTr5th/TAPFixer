from ModelBuilder import ModelBuilder, estimate_related, find_info_in_spec
from ModelChecker import ModelChecker
from ModelAbstractor import ModelAbstractor
from CEXAnalyzer import CEXAnalyzer
from CONST import ITERATION_UPPER, ROUND_UPPER, SPEC_LIST_PRIORITY, SPEC_LIST_SITUATION, SPEC_LIST_COMPARE
import os
import sys
import shutil
import time
from RuleExtractor import RuleExtractor
from GenerateRuleCase import generate_single_rule_case
import json
from UserInput import RULE_SET_USER, SPEC_LIST_USER

def generate_anti_attribute(spec):
    spec, property_type = spec[0], spec[1]
    # [r'--LTLSPEC G((rainSensor.rain = raining)->!X(window.switch = close))', 'state-event']
    if property_type == 'state-event' or property_type == 'liveness' or property_type == 'state-state':
        li = spec.split('->')
        li[1] = '!' + li[1]
        res = []
        res.append(li[0] + '->' + li[1])
        res.append(property_type)
        return res


def CEGAR(states, property_satisfy, spec, anti_spec, para_entity_attribute_list, para_entity_rule_list, round_count, iteration_limit, VIOLATING_POSITION, directory, abstract_mode, logically_eal):
    il = iteration_limit + 1
    # 如果达到迭代最大次数
    '''    print('ModelAbstractor.WAIT_TRIGGER_cnt')
        print(ModelAbstractor.WAIT_TRIGGER_cnt)
        print('ModelAbstractor.WAIT_TRIGGER_AMOUNT')
        print(ModelAbstractor.WAIT_TRIGGER_AMOUNT)'''
    if abstract_mode == '':
        return [], []

    if il > ITERATION_UPPER:
        return [], []
    begin_time = time.time()
    # 如果反属性验证为false，则有潜在修复建议
    if not property_satisfy:
        # last_violating_position = violating_state_position
        spurious_standard = VIOLATING_POSITION
        ca = CEXAnalyzer(states, spec, para_entity_attribute_list,  para_entity_rule_list, spurious_standard)
        violating_state_position = ca.violating_state_position
        # 实际过程是后面Abstract先执行才到这打印
        if il != 1:
            sys.stdout.write('冲突状态： ')
            print(violating_state_position)
        mode = ca.spurious(il)
        # 伪反例
        if mode == 'iteration':
            if abstract_mode == 'wait_trigger' and ModelAbstractor.WAIT_TRIGGER_cnt >= ModelAbstractor.WAIT_TRIGGER_AMOUNT - 1 and ModelAbstractor.WAIT_TRIGGER_AMOUNT != 0:
                return [], []
            # 如果不满足安全属性，则进行抽象
            print('——————正在第%d轮第%d次抽象——————' % (round_count, il))  # ModelAbstractor的调用算一次抽象
            # sys.stdout.write('冲突基准： ')
            # print(spurious_standard)
            flag_INVAR = ca.collect_flag_var(mode)
            ma = ModelAbstractor(states, para_entity_attribute_list, para_entity_rule_list,
                                 spurious_standard, mode, flag_INVAR, round_count, spec, abstract_mode, logically_eal)
            abstract_time = ma.abstract_model(directory)
            # print('ModelAbstractor time: ' + str(abstract_time) + 'ms')
            # para?无所谓，因为谓词也是在相关的里面选。para可以优化为没有
            abstract_smv_path = directory + r'\abstract%d.txt' % il
            # anti_spec = [r'--LTLSPEC G((rainSensor.rain = raining)->!X(window.switch = close))', 'state-event']# [r'--LTLSPEC G((smokeDetector.smoke=detected)->!F(runin_fan.switch_on_0.timer=1 & fan.switch = on))', 'liveness']
            print('检验反属性: ')
            print(anti_spec)
            abstract_checker = ModelChecker(abstract_smv_path, anti_spec, para_entity_attribute_list,
                                            para_entity_rule_list)
            # viloating的判断方法
            run_mode = 'anti'
            states, error_res, verify_time, property_satisfy = abstract_checker.run_nusmv(run_mode, VIOLATING_POSITION[0] + 1)
            #print('property_satisfy')
            #print(property_satisfy)
            end_time = time.time()
            verify_time = round(float(end_time - begin_time) * 1000, 3)
            print('检验用时: ' + str(verify_time) + 'ms')
            return CEGAR(states, property_satisfy, spec, anti_spec, para_entity_attribute_list, para_entity_rule_list, round_count, il, VIOLATING_POSITION, directory, abstract_mode, logically_eal)
        # 真反例
        elif mode == 'find_possible':
            # 统计TAP规则数量
            tap_amount = 0
            for key, value in para_entity_rule_list.items():
                tap_amount += len(value)
            fix_flag, fix_suggestion = ca.map2TAP(tap_amount, para_entity_rule_list, abstract_mode)

            return fix_flag, fix_suggestion

    # 如果反属性验证为true，即遍历了所有情况都没有潜在的修复建议，不存在反例，应该单独处理
    else:
        print('反属性验证为true')
        return CEGAR(states, property_satisfy, spec, anti_spec, para_entity_attribute_list, para_entity_rule_list, round_count, il, VIOLATING_POSITION, directory, abstract_mode, logically_eal)

        #return [], []

# 从这开始想函数
def anti_attribute_reasoning(property_satisfy, verify_time, states, para_entity_rule_list, round_count, property_cnt, spec, logically_eal):

    if round_count > ROUND_UPPER:
       return 0

    extended_rule_amount = 0
    for key, value in para_entity_rule_list.items():
        if key in logically_eal:
            # [['temperatureMeasurement.temperature>20'], ['none'], ['open'], [0, 'none']]
            for single_rule in value:
                if len(single_rule[2]) > 1:
                    extended_rule_amount += 1
    #print('extended_rule_amount')
    #print(extended_rule_amount)

    spec_info_list = find_info_in_spec(spec[1], spec[0])
    front_attribute = spec_info_list[0]
    end_attribute = spec_info_list[2]
    front_rule, end_rule = [], []

    abstract_mode = ''
    #if spec[1] == 'liveness':
    #    abstract_mode += 'liveness'

    # 1+3
    # if (round_count <= rule_amount and para_entity_rule_list) or ((round_count-2) % 3 == 0):
    #
    # 2+3n
    #try:
    #    exception = para_entity_rule_list[end_attribute]
    #except:
    #    abstract_mode += 'new'
    if (not(para_entity_rule_list) or ((round_count-2) % 3 == 0)) and not(abstract_mode):
        abstract_mode += 'new'
    # 3+3n
    elif ((round_count-3) % 3 == 0) and extended_rule_amount > 0 and not(abstract_mode):
        abstract_mode += 'wait_trigger'
    # ((round_count-1) % 3 == 0)
    # 4+4n
    #elif round_count % 4 == 0:
    #    abstract_mode += 'delay'
    # 1+3
    elif (round_count-1) % 3 == 0 and not(abstract_mode):
        abstract_mode += 'present'
    else:
        pass

    print('abstract_mode: ' + str(abstract_mode))
    print('round_count: ' + str(round_count))

    #property_satisfy, verify_time, states, para_entity_rule_list, round_count_cpy, property_cnt
    new_property_satisfy = property_satisfy
    new_verify_time = verify_time
    new_states = states
    new_para_entity_rule_list = para_entity_rule_list
    new_round_count = round_count # 已有对应变量
    new_property_cnt = property_cnt # 不会变
    if not new_property_satisfy:
        print('检验结果为： 违背属性')
        print('检验用时: ' + str(new_verify_time) + 'ms')
        ca = CEXAnalyzer(new_states, spec, para_entity_attribute_list, new_para_entity_rule_list, -1)
        violating_state_position = ca.violating_state_position
        VIOLATING_POSITION = violating_state_position
        sys.stdout.write('冲突状态 / 基准： ')
        print(VIOLATING_POSITION)
        print(new_states[VIOLATING_POSITION[0]-1])
        print(new_states[VIOLATING_POSITION[0]])
        print('——————————检验完毕——————————\n\n')
        # iteration对应一次抽象，每一轮interation_limit都要归零
        iteration_limit = 0
        directory = curr_dir + r'\smv\property%d\round%d' % (property_cnt, round_count)
        if not os.path.exists(directory):
            os.mkdir(directory)
        else:
            shutil.rmtree(directory)
            os.mkdir(directory)
        # violating_state_position = -1

        anti_spec = generate_anti_attribute(spec)
        fix_flag, fix_rule = CEGAR(new_states, new_property_satisfy, spec, anti_spec, para_entity_attribute_list,
                                   new_para_entity_rule_list, round_count, iteration_limit, VIOLATING_POSITION, directory, abstract_mode, logically_eal)
        global fixrule
        fixrule = fix_rule
        print('可行的规则修复谓词取值:')
        print(fix_flag)
        print('生成的修复规则 & 原规则: (fix_rule)')
        # para_entity_rule_list已经被更新了等于fix_rule
        print(fix_rule)
        print('生成的修复规则 & 原规则: (para_entity_rule_list)')
        print(new_para_entity_rule_list)
        print('———————————————————————————\n————————第%d轮抽象结束————————\n———————————————————————————\n\n' % round_count)  # ModelAbstractor的调用算一次抽象)

        round_count_cpy = round_count + 1
        # Abstractor全局变量的清零，INVAR对应一个轮次，不对应一次迭代
        ModelAbstractor.INVAR_test_list = []
        ModelAbstractor.WAIT_TRIGGER_cnt = -1
        ModelAbstractor.INVAR_new_rule_list = []
        ModelAbstractor.INVAR_delay = []
        ModelAbstractor.original_flag_dic = {}
        ModelAbstractor.new_flag_dic = {}
        ModelAbstractor.ID = 0
        # 如果不为空则应用修复规则建模
        # 我们想fix_flag为[]，所以处理fix_flag为 [[], []]的情况
        fix_rule_exist = 0
        if len(fix_flag) != 0:
            for i in fix_flag:
                if i:
                    fix_rule_exist = 1
        #print('fix_rule')
        #print(fix_rule)
        # 反属性推理结果为FALSE。并且要存在修复规则才建模验证全局性
        if fix_rule and fix_rule_exist:
            new_para_entity_rule_list = fix_rule
            print('——正在用修复后规则建立第%d轮模型——' % round_count_cpy)
            print('应用的规则:')
            print(fix_rule)
            # 原模型验证，para_entity_rule_list会变,用新规则ModelBuilder
            mb = ModelBuilder(para_entity_attribute_list, new_para_entity_rule_list, spec)
            model = mb.build_model(property_cnt)
            print('——————————建模成功——————————\n\n')

            # 针对该属性修复的漏洞数量
            global FIX_AMOUNT
            FIX_AMOUNT += 1
            if abstract_mode != 'wait_trigger':
                global FIX_SEMATICS_AMOUNT
                FIX_SEMATICS_AMOUNT += 1
            else:
                global FIX_CONFIG_AMOUNT
                FIX_CONFIG_AMOUNT += 1


            print('——————-正属性模型检验中——————')
            print('检验属性: ')
            print(spec)
            smv_path = curr_dir + '\smv\property%d\model%d.txt' % (property_cnt, ModelBuilder.ID)
            print('检验文件: ')
            print(smv_path)
            mc = ModelChecker(smv_path, spec, para_entity_attribute_list, new_para_entity_rule_list)
            run_mode = 'normal'
            new_states, error_res, new_verify_time, new_property_satisfy = mc.run_nusmv(run_mode)

        # 反属性推理结果为TRUE。说明当前抽象方式无效，要换一种抽象方式
        # 如果为空则复用上次的模型和满足性
        else:
            print('——复用上次模型和模型反例，不用建模和检验，直接抽象，property_satisfy默认不满足——\n\n')
            # new_model = model
            # new_property_satisfy = property_satisfy
            # abstract_mode = ['abstract_old_rule', 'abstract_ew_rule', 'abstract_delay']

        # 在这开始递归
        # 一定要加return，要不然没返回值
        return anti_attribute_reasoning(new_property_satisfy, new_verify_time, new_states, new_para_entity_rule_list, round_count_cpy, property_cnt, spec, logically_eal)

    else:
        return 1



compare_rule_list = RULE_SET_USER


group_num = 0
while(group_num < len(compare_rule_list)):
        group_num += 1
    #try:
        path = r'.\rule\all_in_dict.txt'
        rule_extractor = RuleExtractor(path)
        entity_attribute_list = rule_extractor.get_device_capbilities()


        entity_rule_list = compare_rule_list[group_num - 1]


        entity_rule_list_num = 0
        for i, j in entity_rule_list.items():
            entity_rule_list_num += len(j)

        test_file = open(r'.\rule\test_case_compare9.txt', 'a')
        data_str = json.dumps(entity_rule_list)
        test_file.write(data_str+'\n')
        test_file.close()

        curr_dir = os.getcwd()
        # ->F &不留空格，=取值留空格，time在前
        # liveness一般是枚举
        spec_list = SPEC_LIST_USER

        property_cnt = -1
        directory = ''

        sys.setrecursionlimit(3000)

        global fixrule
        fixrule = {}

        #global total_time
        #total_time = []

        global main_NEW_RULE_AMOUNT
        main_NEW_RULE_AMOUNT = 0

        # 在一轮中是固定的，用于判断伪反例
        VIOLATING_POSITION = []
        # para_entity_attribute_list, para_entity_rule_list = {}, {}


        # 删除smv中的所有文件防止bug
        if not os.path.exists(curr_dir + r'\smv'):
            os.mkdir(curr_dir + r'\smv')
        else:
            shutil.rmtree(curr_dir + r'\smv')
            os.mkdir(curr_dir + r'\smv')

        original_entity_rule_list = {}
        for i, j in entity_rule_list.items():
            original_entity_rule_list.update({i:j})



        spec_group_cnt = 0
        total_print_res = []
        global group_success_cnt
        group_success_cnt = 0
        global group_safe_cnt
        group_safe_cnt = 0
        global group_fail_cnt
        group_fail_cnt = 0
        begin_time1 = time.time()
        for spec_group in spec_list:
            spec_group_cnt += 1
            spec_success_cnt = 0
            spec_safe_cnt = 0
            spec_fail_cnt = 0
            spec_fix_amount = 0
            spec_fix_amount_semantics = 0
            spec_fix_amount_config = 0

            # 重置规则
            entity_rule_list = {}
            for i, j in original_entity_rule_list.items():
                entity_rule_list.update({i: j})
            # 开始计时
            begin_time = time.time()
            for spec in spec_group:


                # 归零
                global FIX_AMOUNT
                FIX_AMOUNT = 0
                global FIX_SEMATICS_AMOUNT
                FIX_SEMATICS_AMOUNT = 0
                global FIX_CONFIG_AMOUNT
                FIX_CONFIG_AMOUNT = 0

                round_count = 0
                # ModelBuilder对应一个属性
                ModelBuilder.ID = 0

                # 从总规则中筛选相关规则
                property_cnt += 1

                # 安全属性中的相关属性筛选，后面是进一步筛选，统一叫筛选
                spec_str = spec[0]
                property_related_attribute = []
                for key, value in entity_attribute_list.items():
                    if key in spec_str:
                        property_related_attribute.append(key)



                para_entity_attribute_list, para_entity_rule_list, logically_eal, logically_erl = estimate_related(entity_attribute_list, entity_rule_list,
                                                                                     property_related_attribute)
                property_directory = curr_dir + r'\smv\property%d' % property_cnt
                if not os.path.exists(property_directory):
                    os.mkdir(property_directory)
                else:
                    shutil.rmtree(property_directory)
                    os.mkdir(property_directory)

                # round对应一个修复的产生
                round_count += 1
                # Abstractor全局变量的清零，INVAR对应一个轮次，不对应一次迭代
                ModelAbstractor.INVAR_test_list = []
                ModelAbstractor.WAIT_TRIGGER_cnt = -1
                ModelAbstractor.INVAR_new_rule_list = []
                ModelAbstractor.INVAR_delay = []
                ModelAbstractor.original_flag_dic = {}
                ModelAbstractor.new_flag_dic = {}
                ModelAbstractor.ID = 0

                print('———————正在对属性%d建模———————' % (property_cnt+1))
                print('原规则:')
                print(para_entity_rule_list)
                mb = ModelBuilder(para_entity_attribute_list, para_entity_rule_list, spec)
                model = mb.build_model(property_cnt)
                print('——————————建模成功——————————\n\n')

                print('——————-正属性模型检验中——————')
                print('检验属性: ')
                print(spec)
                smv_path = curr_dir + '\smv\property%d\model%d.txt' % (property_cnt, ModelBuilder.ID)
                print('检验文件: ')
                print(smv_path)
                mc = ModelChecker(smv_path, spec, para_entity_attribute_list, para_entity_rule_list)
                run_mode = 'normal'
                states, error_res, verify_time, property_satisfy = mc.run_nusmv(run_mode)

                spec_info_list = find_info_in_spec(spec[1], spec[0])
                front_attribute = spec_info_list[0]
                end_attribute = spec_info_list[2]
                front_rule, end_rule = [], []
                try:
                    front_rule = entity_rule_list[front_attribute]
                except:
                    pass
                try:
                    end_rule = entity_rule_list[end_attribute]
                except:
                    pass
                anti_attribute_reasoning_res = anti_attribute_reasoning(property_satisfy, verify_time, states,
                                                                        para_entity_rule_list, round_count, property_cnt, spec, logically_eal)
                if anti_attribute_reasoning_res:
                    # entity_rule_list做更新
                    print('正在更新总规则......')
                    print('更新前：')
                    print(entity_rule_list)
                    print(fixrule)
                    for key, value in entity_rule_list.items():
                        try:
                            for key2, value2 in fixrule.items():
                                if key == key2:
                                    entity_rule_list.update({key2: value2})
                        except:
                            print(fixrule)
                    print('更新后：')
                    print(entity_rule_list)
                    print('检验结果为： 遵守属性')
                    end_time = time.time()
                    verify_time = round(float(end_time - begin_time) * 1000, 3)
                    print('总用时: ' + str(verify_time) + 'ms')
                    print('\n\n\n该属性共存在%d个漏洞!!!' % FIX_AMOUNT)
                    print('属性%d修复完毕!!!!!!!!!!!!!!!!!\n\n\n' % (property_cnt+1))
                    if FIX_AMOUNT:
                        spec_success_cnt += 1
                        group_success_cnt += 1
                    else:
                        spec_safe_cnt += 1
                        group_safe_cnt += 1
                    spec_fix_amount += FIX_AMOUNT
                    spec_fix_amount_semantics += FIX_SEMATICS_AMOUNT
                    spec_fix_amount_config += FIX_CONFIG_AMOUNT
                else:
                    print(anti_attribute_reasoning_res)
                    end_time = time.time()
                    verify_time = round(float(end_time - begin_time) * 1000, 3)
                    print('总用时: ' + str(verify_time) + 'ms')
                    print('达到最大round上限或其它情况，属性%d修复失败!\n\n\n' % (property_cnt+1))
                    spec_fail_cnt += 1
                    group_fail_cnt += 1

            # 寻找失踪的属性，一个失踪的，一个intruder
            if spec_group_cnt == 5:
                spec_safe_cnt += 2

            print_res = '安全属性集合%d修复完成，%d个安全属性满足，%d个安全属性存在漏洞。修复成功%d个安全属性，失败%d个安全属性，安全属性修复率%.2f%%。生成补丁数量%d个。其中规则语义%d个，规则配置%d个。' \
                        % (spec_group_cnt, spec_safe_cnt, len(spec_group)-spec_safe_cnt, spec_success_cnt, spec_fail_cnt, spec_success_cnt/(spec_success_cnt+spec_fail_cnt)*100, spec_fix_amount, spec_fix_amount_semantics, spec_fix_amount_config)
            total_print_res.append(print_res)
            print(print_res)

        end_time1 = time.time()
        verify_time = round(float(end_time1 - begin_time1) * 1000, 3)
        print('\n\n\n-----------总结-----------\n该案例共%d条规则，验证和修复总用时%d ms' % (entity_rule_list_num, verify_time))
        test_file = open(r'.\rule\test_result_compare9.txt', 'a', encoding="utf-8")
        test_file.write('-----------总结-----------\n该案例共%d条规则，验证和修复总用时%d ms' % (entity_rule_list_num, verify_time))
        for i in total_print_res:
            test_file.write(i + '\n')
            print(i)
        another_print = '总共53个安全属性，%d个安全属性满足，%d个安全属性存在漏洞。共修复成功%d个，失败%d个，总体修复率%.2f%%' % (group_safe_cnt, 53-group_safe_cnt, group_success_cnt, group_fail_cnt, group_success_cnt/(group_success_cnt+group_fail_cnt)*100)
        print(another_print)
        test_file.write(another_print + '\n\n\n')
        test_file.close()

        # 复制结果
        curr_dir = os.getcwd()
        src_dir = curr_dir + r'\smv'
        dst_dir = curr_dir + r'\smv%d' % group_num

        if not os.path.exists(dst_dir):
            # 调用copytree()函数复制源目录树到目标目录树中
            shutil.copytree(src_dir, dst_dir)
        else:
            shutil.rmtree(dst_dir)
            shutil.copytree(src_dir, dst_dir)

        group_success_cnt = 0
        group_fail_cnt = 0
    #except:
    #    test_file = open(r'.\rule\test_case1.txt', 'a', encoding="utf-8")
    #    test_file.write('上述规则集合有问题\n')
    #    test_file.close()
    #    continue
