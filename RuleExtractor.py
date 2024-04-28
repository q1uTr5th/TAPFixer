import re
import json
import os
from DevieceCapExtractor import DevieceCapExtractor


class RuleExtractor(object):
    def __init__(self, path):
        self.path = path
        self.dce = DevieceCapExtractor()
        self.device_capbilities = self.dce.data_dic
        #print(self.device_capbilities)
        self.rule = {}
        for key, value in self.dce.data_dic.items():
            self.rule.update({key.replace(' ', '').replace('\n', ''): []})
        #print(rule)
        #print(len(rule))
        self.extract_IFTTT_rule()
        #print(self.rule)
        cnt = 0
        for key, value in self.rule.items():
            if len(value)!=0:
                cnt += 1
        #print(cnt)
        #print(len(self.rule))
        #print(len(rule))
        #print(rule['airConditioner.switch'])
        #print(dce.data_dic)
        #print(len(dce.data_dic))

    # IFTTT没condition
    def extract_SmartThings(self):
        pass
        # IF [triggerChannelTitle] [triggerTitle] WHILE none, THEN [actionChannelTitle] [actionTitle];

    def get_device_capbilities(self):
        return self.device_capbilities

    def get_rules(self):
        return self.rule

    def extract_IFTTT_rule(self):
        #print(self.rule)
        f = open(self.path, 'r', encoding='utf-8')
        lines = f.readlines()
        # 提取T,C,A
        for single_rule in lines:
            extract_rule = []
            single_rule = single_rule.replace(' ', '').replace(',', '')
            #print(single_rule)
            re1 = 'IF(.*?)THEN'
            trigger = re.findall(re1, single_rule)[0].split('&')
            #print(trigger)
            re3 = 'THEN(.*?)\n'
            action = re.findall(re3, single_rule)[0].split('&')
            extract_rule.append(trigger)
            extract_rule.append(['none'])
            extract_rule.append([action[0].split('=')[1]])
            extract_rule.append([0, 'none'])
            #print(action[0].split('=')[0])
            try:
                # print(self.rule[action[0].split('=')[0]])
                self.rule[action[0].split('=')[0]].append(extract_rule)
            except:
                print(single_rule)
        '''entity_attribute_list={
            entity_attribute: [on,off],
            entity_attribute: '0..5',
            entity_attribute: 'boolean'}

            entity_rule_list={
            entity_attribute: [[trigger,condition,action]],
            entity_attribute: [[[trigger1,trigger2],condition,[action1,action2],[time1,time2,0,5,-1]] , rule2 ] }
        '''
        '''ngramDict = {}
        for item in ngramSet:

            ngramDict.update({item: ngramList.count(item)})'''



# r = RuleExtractor(path)


