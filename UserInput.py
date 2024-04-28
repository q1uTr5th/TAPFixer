from CONST import SPEC_LIST_SITUATION, SPEC_LIST_PRIORITY, SPEC_LIST_NEARBY

RULE_SET_USER = [{'fan.switch': [[['smokeDetector.smoke=detected'], ['none'], ['on', 'off'], [4, 0, 'none']],
                 [['presenceSensor.presence=present'], ['none'], ['on', 'off'], [3, 0, 'none']]]}]

SPEC_LIST_USER = [[[r'--LTLSPEC G((home.mode = home & home.mode != home.mode_last)->X(light.switch = on))', 'state-event'],
[r'--LTLSPEC G((home.mode = home & home.mode != home.mode_last)->X(garageDoorControl.door = open))', 'state-event']]]

#[[[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke != smokeDetector.smoke_last)->X(fan.switch = on))', 'state-event'],
#[r'--LTLSPEC G((smokeDetector.smoke = detected & smokeDetector.smoke = smokeDetector.smoke_last)->(fan.switch = on))', 'state-state']]]


