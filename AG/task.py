# 该文件用来执行行为决策
from Automatic import Automatic
import log
import time
from ocr import GameOCR



# 遍历总任务字典，True代表需要执行
class Task(Automatic, GameOCR):
    def __init__(self, title, game_path, process_name, target, number, find_time=10, mode='mopup', \
                    consume_power=-1, is_exhausted=False, is_standby=True, \
                    standby_target='酬金委托', standby_target_number=5, joint_is_refresh=True,\
                          joint_must_s=True, get_stack_time=6, interval_time=0.02, time_out=10, task_interval_time=2, delay=0.5,\
                 ocr_use_gpu=False, ocr_collect_time=20, template_resolution='1920*1200', pause_stop_check=None,\
                     awcnt_clear_power_target_step2=5):
        '''
        target 目标副本
        number 目标副本等级
        find_time 二级页面寻找最大次数
        mode  副本执行模式
        consume_power 消耗的目标体力
        is_exhausted 是否耗尽全部体力
        is_standby 是否启用备用副本，仅联合特勤生效
        standby_target 备用副本
        standby_target_number 备用副本等级
        joint_is_refresh 联合特勤是否允许刷新
        joint_must_s 联合特勤是否必须s
        get_stack_time 堆栈递归领取时间
        task_interval_time 任务间的间隔
        
        template_resolution 匹配的模板分辨率
        
        awcnt_clear_power_target_step2 清体力任务普通副本界面选择滚轮的滚动次数
        
        Automatic::interval_time, time_out, delay, pause_stop_check
        GameOCR::ocr_use_gpu, ocr_collect_time
        '''
        
        
        
        
        
        Automatic.__init__(self, title, game_path, process_name, time_out, interval_time, delay ,pause_stop_check)
        GameOCR.__init__(self, ocr_use_gpu, ocr_collect_time)
        
        # 模板匹配的分辨率
        self.rootpic = 'pic_1920_1200'
        if template_resolution == '1920*1200':
            self.rootpic = 'pic_1920_1200'
        elif template_resolution == '1920*1080':
            self.rootpic = 'pic_1920_1080'
        else:
            log.Log(f"模板分辨率匹配失败，正在使用1920*1200分辨率模板！", level='WARNING')
        
        
        
        # 任务间隔
        self.interval_time = interval_time # 截图间隔
        self.task_interval_time = task_interval_time
        # 总任务
        self.taskdic = {
            "登录界面": True,
            "每日活跃度": True,
        }

        # 每日活跃任务细节
        self.act_dic = {
            "角色互动": True,
            "尝试领取额外体力": True,
            "进入指定副本并消耗体力": True,
            "联防协议 奖励领取": True,
            "游园街": True,
            "商店免费体力": True,
            "弥弥尔": True,
            "领取每日每周任务奖励": True,
            "大月卡": True,
            "邮件": True
        }

        # 模板图片路径及标签
        self.template_path = {
            "登录界面": f'{self.rootpic}\\login\\loginui.png',
            "主界面": f'{self.rootpic}\\mainui\\mainui.png',
            #"通用体力消耗面板": r''
        }

        self.template_button_path = {
            "登录界面按钮": f'{self.rootpic}\\login\\loginbutton.png',
            "体力入口": f'{self.rootpic}\\dailytask\\power\\entrance.png',
            "体力左": f'{self.rootpic}\\dailytask\\power\\left.png',
            "体力右": f'{self.rootpic}\\dailytask\\power\\right.png'
        }
        
        # re_main_ui() 参数
        self.trycnt = 50
        
        # clear_power()的相关参数
        self.target = target 
        self.number = number 
        self.find_time = find_time 
        self.mode = mode 
        self.consume_power = consume_power
        self.is_exhausted = is_exhausted 
        self.is_standby = is_standby        
        self.standby_target = standby_target
        self.standby_target_number = standby_target_number
        self.joint_is_refresh = joint_is_refresh              
        self.joint_must_s = joint_must_s
        self.get_stack_time = get_stack_time
        
        self.awcnt_clear_power_target_step2 = awcnt_clear_power_target_step2

        # 常用区域
        # 主界面下操作栏（修正者，探测...)
        self.main_ui_down_column = [750, 1120, 1600, 1220] 
        # 主界面点击 “前往作战” 后的界面的下操作栏
        self.tofight_down_column = [120, 1100, 1800, 1200]       
        # 商店补给区左选择栏(补给组合，角色换装...)
        self.shop_supply_left_column = [30, 170, 300, 660]       
        # 商店补给区上选择栏(限时补给，日常补给...)
        self.shop_supply_up_column = [400, 170, 1450, 260]
        # 游园街派遣4任务区域
        self.garden_task_entrustment_region = [
            [55, 210, 630, 1050], # 滑动到最左侧，第一个任务
            [630, 210, 1200, 1050], # 滑动到最左侧，第二个任务
            [725, 210, 1300, 1050], # 滑动到最右侧，第三个任务
            [1300, 210, 1870, 1050]  # 滑动到最右侧，第四个任务
        ]
        # 主界面点击TAP出来的界面
        self.main_ui_Tap = [1300, 80, 1900, 1215]
        # 活动左侧菜单
        self.act_left_region = [25, 165, 320, 1170]
        # 联防协议主界面的一键领取区域
        self.jointDefense_main_oneclick_region = [1254, 1026, 1883, 1110]
        # 返回键区域
        self.re_region = [0, 55, 240, 150]
        # clear_power() 二级界面寻找区域
        self.clear_power_sec_find_region = [850, 980, 1050, 1050]
        # get_curpower_minpower() 重置体力的界面，点击最小值的界面
        self.get_curpower_minpower_panel_region = [1350, 970, 1900, 1060]
        # get_curpower_minpower() 识别当前体力的区域
        self.curpower_region = [1250, 60, 1365, 120]
        # get_curpower_minpower() 识别关卡体力的区域
        self.minpower_region = [1650, 1080, 1700, 1120]
        # 联合特勤三个关卡的位置
        self.joint_second_panel_level_region = [[50, 500, 300, 700], [690, 420, 830, 530], [1300, 540, 1470, 660]]
        # 联合特勤识别有无刷新次数区域
        self.joint_second_panel_ishave_refresh_region = [1490, 1120, 1760, 1200]
        # 联合特勤识别刷新次数的区域
        self.joint_second_panel_refresh_time_region = [1680, 1145, 1745, 1190]
        # 联防协议 消耗面板 当前资源识别区域
        self.joint_defense_disorder_consume_panel_curcom_region = [1500, 80, 1600, 120]
        # 联防协议 消耗面板 关卡最低资源识别区域
        self.joint_defense_disorder_consume_panel_mincom_region = [1643, 1082, 1680, 1120]
        
        
        
        
        if template_resolution == '1920*1080':
            self.main_ui_down_column = [750, 1000, 1600, 1100] 
            self.tofight_down_column = [120, 1000, 1800, 1100]       
            self.shop_supply_left_column = [30, 170, 300, 660]       
            self.shop_supply_up_column = [355, 170, 1450, 250]
            
    


    # 当前界面判断, 返回页面标签
    def get_current_ui(self) -> str|None: 
        for key, path in self.template_path.items():
            if self.istargetui(key):
                log.Log(f"检测到当前界面在:{key}")
                return key
            else:
                log.Log(f"当前界面不是：{key}")
        log.Log(f"不在任何目标界面内！", level='WARNING')
        return None

    # 判断目前是否是目标图片
    def istargetui(self, key, judge_time=1, delay_judge=0):
        time.sleep(delay_judge)
        if self.wait(self.template_path[key], time_out=judge_time, is_Log=False):
            return True
        return False


    # 遍历任务列表
    def all_task(self):
        for key, value in self.taskdic.items():
            if value:
                # # 先回到主界面, 排除登录
                # if key != "登录界面" and not self.re_main_ui():
                #     return False

                if not self.choose_task(key):
                    log.Log(f"{key} 执行失败", level='WARNING')
                    continue
                else:
                    log.Log(f"{key} 执行完成")
                
        return True

    # 尝试返回主界面,trycnt:尝试次数
    def re_main_ui(self, istargetui_judge_time=0, istargetui_delay_judge=0):
        trycnt = self.trycnt
        px, py = 750, 80
        cnt = 0
        while not self.istargetui('主界面', istargetui_judge_time, istargetui_delay_judge):
            if cnt >= trycnt:
                log.Log(f"尝试返回主界面{trycnt}次未成功", level='ERROR')
                return False
            
            
            if self.auto_click(f'{self.rootpic}\\dailytask\\ret\\ret.png', \
                                   0, 0, True, True, self.re_region):
                log.Log(f"点击返回键")
                continue
            
            elif self.best_template(f'{self.rootpic}\\dailytask\\ret\\exit.png'):
                if self.auto_click(f'{self.rootpic}\\dailytask\\ret\\cancel.png', \
                                    0, 0, True):
                    log.Log(f"点击取消")
                    continue
            
            else:
                self.auto_click('-', px, py, False)
            
            time.sleep(self.interval_time)

        # 重置鼠标位置防止遮挡
        self.auto_move_mouse(px, py)
        
        log.Log(f"成功返回主界面")
        return True

    # 选择具体任务
    def choose_task(self, key):
        if key != "登录界面" and key != "每日活跃度": # 排除登录界面 和 每日活跃度（因为这个函数是多个任务的起点，无需先返回main_ui）
            # 先回到主界面
            if not self.re_main_ui():
                return False
        
        if key == "登录界面":
            return self.login()
        elif key == "每日活跃度":
            return self.daily()
        elif key == "角色互动":
            return self.role_interaction()
        elif key == "尝试领取额外体力":
            return self.get_power()
        elif key == "进入指定副本并消耗体力":
            return self.clear_power('酬金委托', number=5)
        elif key == "联防协议 奖励领取":
            return self.joint_defense_reward()
        elif key == "游园街":
            return self.garden()
        elif key == "商店免费体力":
            return self.shop_get_free_power()
        elif key == "弥弥尔":
            return self.mimier()
        elif key == "领取每日每周任务奖励":
            return self.get_daily_weekly_reward()
        elif key == "大月卡":
            return self.monthly_pass()
        elif key == "邮件":
            return self.mail()

        
        log.Log(f"无对应匹配任务", level='DEBUG')
        return False

    def login(self):
        # 循环等待加载界面
        waitlist = [f'{self.rootpic}\\login\\load1.png', f'{self.rootpic}\\login\\load2.png', 
                    f'{self.rootpic}\\login\\load3.png', f'{self.rootpic}\\login\\load4.png', 
                    f'{self.rootpic}\\login\\load5.png']
        while True:
            time.sleep(self.task_interval_time)
            if self.best_template(waitlist[0]) is None and self.best_template(waitlist[1]) is None\
                and self.best_template(waitlist[2]) is None and self.best_template(waitlist[3]) is None\
                and self.best_template(waitlist[4]) is None:
                break
            log.Log(f"等待加载")
            

        # 是否在登录界面
        
        if not self.istargetui('登录界面'):
            # 判断所有模板，判断是否在游戏内
            if self.get_current_ui() is None:
                return False
            return True
        else:
            # 点击
            self.wait_and_click(self.template_button_path['登录界面按钮'], 0, 0, True)
            return self.re_main_ui(0, self.task_interval_time)




    def daily(self):
        #log.Log(f"已执行Daily")
        f = []
        for key, value in self.act_dic.items():
            if value:
                # # 先回到主界面
                # if not self.re_main_ui():
                #     return False
                
                if self.choose_task(key):
                    log.Log(f"{key} 执行完成")
                else:
                    log.Log(f"{key} 执行失败", level='WARNING')
                    f.append(key)

        # 先回到主界面
        if not self.re_main_ui():
            return False


        for info in f: 
            log.Log(f"注意：每日活跃度任务中 {info} 任务未成功执行", level='WARNING')
        if len(f) != 0:
            return False
        
        return True


    # 每日任务分支-角色互动
    def role_interaction(self):
        log.Log(f"==============正在执行：角色互动==============")
        time.sleep(self.task_interval_time)
        
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        
        rect = self.get_window_rect()
        if rect is None:
            return False
        left, top, right, bottom = rect
        # 点击游戏中心
        if not self.auto_click('-', (right - left) // 2, (bottom - top) // 2, False):
            log.Log(f"角色点击失败", level='ERROR')
            return False
        
        return True

    # 每日任务分支-领取体力
    def get_power(self):
        log.Log(f"==============正在执行：获取体力==============")
        time.sleep(self.task_interval_time)
        
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        
        # 任务名 + (px, py)点击偏移
        adict = {
            '体力入口':(50, 0),
            '体力左':(0, 0), 
            '体力右':(0, 0)
        }
        for name, pxy in adict.items():
            if not self.wait_and_click(self.template_button_path[name], pxy[0], pxy[1], True, time_out=self.task_interval_time, is_Log=False):
                log.Log(f"未找到{name}, 可能体力已经领取", level='WARNING')
                break
            

        return True
    
    # 清体力 (最后做，多分枝, 所有体力副本)
    def clear_power(self, target, number, find_time=10, mode='mopup', \
                    consume_power=-1, is_exhausted=False, is_standby = True, \
                    standby_target='酬金委托', standby_target_number=5, joint_is_refresh=True,\
                          joint_must_s=True, use_class_parameter=True):
        
        if use_class_parameter:
            target = self.target 
            number = self.number
            find_time = self.find_time
            mode = self.mode 
            consume_power = self.consume_power 
            is_exhausted = self.is_exhausted 
            is_standby = self.is_standby        
            standby_target = self.standby_target
            standby_target_number = self.standby_target_number
            joint_is_refresh = self.joint_is_refresh              
            joint_must_s = self.joint_must_s

        
        '''
        target 目标副本名
        number 第几个难度的副本
        find_time 最多查找次数，非必要无需修改
        mode 清理副本使用 扫荡/战斗
        consume_power 目标消耗体力，-1为直接点击最大按键
        is_exhausted 是否将目前体力耗尽
        is_standby 若联合特勤刷取失败，是否启用备用方案，
        standby_target 备用方案的目标副本
        standby_target_number 备用方案副本等级
        joint_is_refresh，joint_must_s 联合特勤的相关参数，是否尝试刷新，是否必须为s级
        '''
        
        log.Log(f"==============正在执行：清体力==============")
        log.Log(f"目标副本 {target}, 备用副本 {standby_target}, 是否启用备用方案: {is_standby}")
        time.sleep(self.task_interval_time)
        
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False

        # 目标副本字典
        target_step1 = {
            "物资": f'{self.rootpic}\\dailytask\\clear_power\\materials.png',
            "刻印": f'{self.rootpic}\\dailytask\\clear_power\\engrave.png'
        }
        target_step2 = {
            "酬金委托": f'{self.rootpic}\\dailytask\\clear_power\\coins.png',
            "模拟作战": f'{self.rootpic}\\dailytask\\clear_power\\combat.png',
            "因子采集": f'{self.rootpic}\\dailytask\\clear_power\\factor_collection.png',
            "深层勘探": f'{self.rootpic}\\dailytask\\clear_power\\deep_exploration.png',
            "极限萃取": f'{self.rootpic}\\dailytask\\clear_power\\limit_extraction.png',
            "失落遗迹": f'{self.rootpic}\\dailytask\\clear_power\\lost_relics.png',
            "战场清扫": f'{self.rootpic}\\dailytask\\clear_power\\battlefield_cleaning.png',
            "联合特勤": f'{self.rootpic}\\dailytask\\clear_power\\joint.png',
            "神域解析": f'{self.rootpic}\\dailytask\\clear_power\\parse.png',
        }
        
        materials_list = ["酬金委托", "模拟作战", "因子采集", "深层勘探", "极限萃取", "失落遗迹"]
        engrave_list = ["战场清扫", "联合特勤", "神域解析", "介质"]


        # 目标是联防协议
        if target == '联防协议':
            # 点击活动 （使用菜单键进行定位）
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\tap.png', 0, 160, True):
                log.Log(f'活动点击失败', level='ERROR')
                return False
            
            # 先返回顶部
            
            self.auto_wheel(50, 1, 200, 300)

            # 遍历菜单，使用ocr，点击联防协议
            for i in range(10):
                time.sleep(self.task_interval_time)
                img = self.get_game_screenshot()
                if img is None or img.size == 0:
                    log.Log("未获取到图片", level='ERROR')
                    return False
                
                rect = self.find_text(img, '联防协议', self.act_left_region)
                if rect is not None:
                    if not self.auto_click('-', rect[0], rect[1], False):
                        log.Log(f"联防协议点击失败", level="ERROR")
                        return False
                    else:
                        break
            
                # 下滑
                self.auto_wheel(10, -1, 200, 300)
                
                
            # 一键领取资源
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\joint_defense_main_oneclick.png', \
                0, 0, True, True, self.jointDefense_main_oneclick_region, time_out=self.task_interval_time, is_Log=False):
                log.Log(f"一键领取资源失败，可能是无资源领取", level="WARNING")
            else:  
                self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\continue.png', \
                0, 0, True)
                
            # 前往作战
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\joint_defense_main_gotofight.png', 0, 0, True):
                log.Log(f"点击 前往作战 失败", level="ERROR")
                return False
                
            # 选择关卡
            # 点击 信息采纳
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\joint_defense_info_collect.png', 0, 0, True):
                log.Log(f"点击 信息采纳 失败", level="ERROR")
                return False
            
            # 点击目标关卡
            time.sleep(self.task_interval_time)
            if number == 1:
                
                if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\joint_defense_first.png', 0, 0, True):
                    log.Log(f"点击 目标关卡{number} 失败", level="ERROR")
                    return False
            elif number == 2:
                
                if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\joint_defense_sec.png', 0, 0, True):
                    log.Log(f"点击 目标关卡{number} 失败", level="ERROR")
                    return False
            elif number == 3:
                
                if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\joint_defense_sec.png', 0, 0, True):
                    log.Log(f"点击 目标关卡{number} 失败", level="ERROR")
                    return False
            else:
                log.Log(f"无对应关卡等级", level="DEBUG")
                return False
            
            # 交给通用体力面板
            
            if not self.common_power_panel(mode, consume_power, is_exhausted):
                return False
            
        else:            
            # 进入一级界面
            if self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\button.png', 0, 0, True):
                log.Log(f"点击 前往作战")
            else:
                log.Log("前往作战 点击失败", level='ERROR')
                return False
            
            

            # 第一层点击
            if target in materials_list:
                if self.wait_and_click(target_step1["物资"], 0, 0, True):
                    log.Log(f"点击 物资")
                else:
                    log.Log("物资 点击失败", level='ERROR')
                    return False
                
            elif target in engrave_list:
                if self.wait_and_click(target_step1["刻印"], 0, 0, True):
                    log.Log(f"点击 刻印")
                else:
                    log.Log("刻印 点击失败", level='ERROR')
                    return False

            else:
                log.Log(f"无匹配副本，请检查target的属性值", level='DEBUG')

            
            # 第二层点击, 加入ocr
            if target in target_step2.keys():
                # 返回最左侧

                self.auto_wheel(80, -1, 500, 900)
                

                # 循环遍历目标，若上一个识别的目标与下一个识别的目标相同，则结束
                pre_text = '#'
                for i in range(find_time):
                    time.sleep(self.task_interval_time)
                    
                    img = self.get_game_screenshot()
                    if img is None or img.size == 0:
                        log.Log("未获取到图片", level='ERROR')
                        return False
                    

                    #找位置
                    pos = self.find_text(img, target_text=target, pos=self.clear_power_sec_find_region)


                    if pos is not None:
                        if self.auto_click('-', pos[0], pos[1], False):
                            log.Log(f"点击：{target}")
                            break

                    #若上一个识别的目标与下一个识别的目标相同，则结束
                    res = self.recognize(img, pos=self.clear_power_sec_find_region)
                    if(pre_text == res[0][1]):
                        log.Log(f"未找到：{target}", level='ERROR')
                        return False
                    pre_text = res[0][1]

                    # 滚轮滑动
                    self.auto_wheel(self.awcnt_clear_power_target_step2, 1, 500, 900)
                    

                    if i == find_time - 1: 
                        return False

            else:
                log.Log(f"对应路径字典无匹配项", level='DEBUG')
                return False
        
            # 对应副本的应对策略
            name_dic = {
                '酬金委托': '承托',
                '模拟作战': '表征',
                '因子采集': '调和',
                '深层勘探': '探测',
                '极限萃取': '提纯',
                '失落遗迹': '共鸣',
                '战场清扫': '镌铭3',
                '神域解析': '分析'
            }
            
            # 是普通副本
            if target in name_dic.keys():
                
                if not self.second_common_op(name_dic[target], number):
                    return False
                
                
                if not self.common_power_panel(mode, consume_power, is_exhausted):
                    return False
                
            # 联合特勤
            elif target == '联合特勤':
                time.sleep(self.task_interval_time)
                if not self.joint_second_panel(joint_is_refresh, joint_must_s):
                    # 是否启用备用方案
                    if is_standby:
                        if standby_target == target:
                            log.Log(f"备用方案与原方案副本相同 或 备用方案已经尝试但失效", level='ERROR')
                            return False
                            
                        log.Log(f"尝试使用备用方案")
                        self.re_main_ui()
                        
                            
                        
                        return self.clear_power(standby_target, standby_target_number, \
                                            find_time, mode, consume_power, is_exhausted, \
                                                is_standby, standby_target, standby_target_number,\
                                                    joint_is_refresh, joint_must_s, use_class_parameter=False)
                    else:
                        log.Log(f"联合特勤刷取失败，且未启用备用方案", level='WARNING')
                        return False
                else:
                    # 重置，将体力消耗调整为最低
                    is_clear_flag = False # 用来存储是否执行过清体力
                    
                    log.Log(f"重置体力")
                    if not self.wait_and_click(f'{self.rootpic}\\dailytask\\power_panel\\to_min.png', 0, 0, True, True, self.get_curpower_minpower_panel_region, 0.7):
                        log.Log(f"点击失败", level='ERROR')
                        return False
                    
                    self.auto_move_mouse(600, 1000)
                    
                    # 获取当前体力情况
                    
                    cmp = self.get_curpower_minpower()
                    if cmp is None:
                        return False
                    cur_p, min_p = cmp
                    
                    consume_power = min(consume_power, cur_p) # 取最小，防止死循环
                    
                    pre_power = cur_p
                    
                    sum_power = 0
                    
                    
                    # 清体力
                    if not self.common_power_panel(mode, consume_power, is_exhausted, is_pd=False):
                        return False
                    else:
                        is_clear_flag = True
                    
                    
                    # 清除指定体力
                    while not is_exhausted:
                        # 循环选择副本
                        time.sleep(self.task_interval_time)
                        if not self.joint_second_panel(joint_is_refresh, joint_must_s):
                            if is_clear_flag:
                                return True
                            else:
                                return False

                        # 重置，将体力消耗调整为最低
                        
                        log.Log(f"重置体力")
                        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\power_panel\\to_min.png', 0, 0, True, True, self.get_curpower_minpower_panel_region, 0.7):
                            if is_clear_flag:
                                return True
                            else:
                                log.Log(f"点击最小值失败", level='ERROR')
                                return False
                        
                        self.auto_move_mouse(600, 1000)


                        
                        cmp = self.get_curpower_minpower()
                        if cmp is None:
                            return False
                            
                        cur_p, min_p = cmp
                        consume_power -= (pre_power - cur_p)
                        sum_power += (pre_power - cur_p)
                        pre_power = cur_p
                        
                        if consume_power < min_p:
                            log.Log(f"已清除 {sum_power} 吨吨值")
                            return True
                        
                        # 清体力
                        
                        if not self.common_power_panel(mode, consume_power, is_exhausted, is_pd=False):
                            if is_clear_flag:
                                return True
                            else:
                                return False
                        
                        
                    # 耗尽模式,在指定值下无效
                    while is_exhausted:
                        # 循环选择副本
                        time.sleep(self.task_interval_time)
                        if not self.joint_second_panel(joint_is_refresh, joint_must_s):
                            if is_clear_flag:
                                return True
                            else:
                                return False
                        
                        
                        
                        # 重置，将体力消耗调整为最低
                        
                        log.Log(f"重置体力")
                        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\power_panel\\to_min.png', 0, 0, True, True, self.get_curpower_minpower_panel_region, 0.7):
                            if is_clear_flag:
                                return True
                            else:
                                log.Log(f"点击最小值失败", level='ERROR')
                                return False
                        
                        self.auto_move_mouse(600, 1000)
                        
                        
                        cmp = self.get_curpower_minpower()
                        if cmp is None:
                            return False
                            
                        cur_p, min_p = cmp
                        if cur_p < min_p:
                            log.Log(f'体力耗尽')
                            return True
                        
                        # 清体力
                        
                        if not self.common_power_panel(mode, consume_power, is_exhausted, False):
                            if is_clear_flag:
                                return True
                            else:
                                return False
                        

            else:
                log.Log(f"无对应副本二级界面", level='DEBUG')
                return False

        return True

    # 副本二级菜单对应内部操作，如酬金委托二级菜单
    def second_common_op(self, target='承托', number=1):
    
        target_s = f"{target}-{number}"

        # 最左侧检测
        self.auto_wheel(50, -1, 500, 900)
        time.sleep(self.task_interval_time)

        img = self.get_game_screenshot()
        if img is None or img.size == 0:
            log.Log("未获取到图片", level='ERROR')
            return False

        pos = self.find_text(img, target_s)
        if pos is None:
            log.Log(f"左侧匹配失败", level='WARNING')
            # 最右侧检测
            self.auto_wheel(50, 1, 500, 900)
            time.sleep(self.task_interval_time)
            


            img = self.get_game_screenshot()
            if img is None or img.size == 0:
                log.Log("未获取到图片", level='ERROR')
                return False
            
            pos = self.find_text(img, target_s)
            if pos is None:
                log.Log(f"右侧执行失败, 未找到指定副本关卡", level='ERROR')
                return False
            else:
                if self.auto_click('-', pos[0], pos[1], False):
                    log.Log(f"点击 {target_s}")
                else:
                    log.Log(f"点击 {target_s} 失败", level='ERROR')
                    return False

        else:
            if self.auto_click('-', pos[0], pos[1], False):
                log.Log(f"点击 {target_s}")
            else:
                log.Log(f"点击 {target_s} 失败", level='ERROR')
                return False
            
        
        return True


    # 获取当前体力和最小花费体力
    def get_curpower_minpower(self, is_reset=False):
        '''
        is_reset 是否在识别前重置副本刷取倍数
        '''
        
        # 获取当前体力 和 副本所需最低体力
        
        # 重置，将体力消耗调整为最低
        if is_reset:
            log.Log(f"重置体力")
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\power_panel\\to_min.png',\
                0, 0, True, True, self.get_curpower_minpower_panel_region):
                log.Log(f"点击失败", level='ERROR')
                return None
            
        
        img = self.get_game_screenshot()
        if img is None or img.size == 0:
            log.Log("未获取到图片", level='ERROR')
            return None

        res = self.recognize(img, self.curpower_region)
        if len(res) == 0:
            log.Log(f"当前体力识别失败", level='ERROR')
            return None
        s = res[0][1]
        log.Log(f"当前体力：{s}")
        current_power = int(s.split('/')[0])

        res = self.recognize(img, self.minpower_region)
        if len(res) == 0:
            log.Log(f"最小消耗体力识别失败", level='ERROR')
            return None
        min_power = int(res[0][1])
        log.Log(f"副本最低所需体力：{min_power}")
        

        return current_power, min_power


    # 通用体力界面 
    def common_power_panel(self, mode='mopup', consume_power=-1, is_exhausted=False, is_pd=True, is_joint_defense=False):
        '''
        - mode=mopup 为扫荡模式(默认),fight 为战斗模式
        - consume_power=-1 消耗目前全部体力 输入任意非负数为目标体力, 最终刷取所消耗体力会尽量向下靠近目标
        - is_exhausted 是否耗尽体力
        - is_pd 联合特勤专属参数，关闭时在体力刷取完毕后直接返回True，不做循环判断，此时consume_power，is_exhausted全部失效
        - is_joint_defense 联防协议参数，打开会将get_curpower_minpower()换成joint_defense_disorder_consume_panel_rec_curmincom()
        '''
        cpp_dic = {
            'min':f'{self.rootpic}\\dailytask\\power_panel\\min.png',
            'max':f'{self.rootpic}\\dailytask\\power_panel\\max.png',
            'single_down':f'{self.rootpic}\\dailytask\\power_panel\\single_down.png',
            'single_up':f'{self.rootpic}\\dailytask\\power_panel\\single_up.png',
            'to_max':f'{self.rootpic}\\dailytask\\power_panel\\to_max.png',
            'to_min':f'{self.rootpic}\\dailytask\\power_panel\\to_min.png',
            'mopup':f'{self.rootpic}\\dailytask\\power_panel\\mopup.png',
            'confirm1':f'{self.rootpic}\\dailytask\\power_panel\\confirm1.png',
            'confirm2':f'{self.rootpic}\\dailytask\\power_panel\\confirm2.png'
        }

        # 重置，将体力消耗调整为最低
        log.Log(f"重置体力")
        if not self.wait_and_click(cpp_dic['to_min'], 0, 0, True, True, self.get_curpower_minpower_panel_region):
            log.Log(f"点击失败", level='ERROR')
            return False
        

        all_used_power = 0

        while True: 
            # 执行至目标体力
            # 获取当前体力 和 副本所需最低体力
            
            cm_power = None
            if is_joint_defense:
                cm_power = self.joint_defense_disorder_consume_panel_rec_curmincom()
            else:
                cm_power = self.get_curpower_minpower()
            if cm_power is None:
                return False
            current_power, min_power = cm_power
            

            # 判断是否满足最低体力要求
            if current_power < min_power:
                log.Log(f"未满足最低体力要求", level='WARNING')
                return True
            
            if consume_power == -1 or is_exhausted:
                # 点击最大值按键
                if not self.wait_and_click(cpp_dic["to_max"], 0, 0, True, True, self.get_curpower_minpower_panel_region):
                    log.Log(f"点击失败", level='ERROR')
                    return False
                


            elif consume_power > 0:
                # 如果超限，按当前体力算
                if consume_power > current_power:
                    consume_power = current_power

                point_cnt = min(10, consume_power // min_power)
                log.Log(f"该次目标清理 {point_cnt * min_power} 吨吨值")
                if point_cnt == 0:
                    log.Log(f"目标体力任务已完成，本次清理{all_used_power}吨吨值")
                    return True

                for _ in range(point_cnt-1):
                    self.auto_move_mouse(700, 1080)
                    
                    # 点击+1按键
                    if not self.wait_and_click(cpp_dic["single_up"], 0, 0, True, True, self.get_curpower_minpower_panel_region):
                        log.Log(f"点击失败", level='ERROR')
                        return False
                    
                
                consume_power -= point_cnt * min_power
                all_used_power += point_cnt * min_power
                    
                

            else:
                log.Log(f"目标体力应该为正数！", level='ERROR')
                return False

            
            # 扫荡或战斗
            if mode == 'mopup':
                # 点击扫荡
                if not self.wait_and_click(cpp_dic["mopup"], 0, 0, True):
                    log.Log(f"点击失败", level='ERROR')
                    return False

                # 点击确认
                if not self.wait_and_click(cpp_dic["confirm1"], 0, 0, True, \
                    time_out=self.task_interval_time, is_Log=False):
                    log.Log(f"点击失败 或 无该项", level='WARNING')
                    
                # 点击确认
                
                if not self.wait_and_click(cpp_dic["confirm2"], 0, 0, True, \
                    time_out=self.task_interval_time, is_Log=False, delay_click=self.task_interval_time):
                    log.Log(f"点击失败", level='ERROR')
                    return False

                
            elif mode == 'fight':
                log.Log(f"抱歉，该功能正在研发中，敬请期待", level='WARNING')
                return False
            else:
                log.Log(f"模式选择错误", level='DEBUG')
                return False


            
            if is_pd:
                # 不耗尽, 且未指定体力消耗
                if not is_exhausted and consume_power == -1:
                    break
                # 耗尽用剩余体力判断
                else:
                    '''联防协议专属，适配弹窗缩回'''
                    if is_joint_defense:
                        # 再次点击副本
                        # 
                        if not self.wait_and_click(f'{self.rootpic}\\joint_defense\\level.png', 0, 0, True):
                            log.Log(f"点击 关卡 失败", level="ERROR")
                            return False
                    
                    
                    # 重置，将体力消耗调整为最低, 为了获得最小体力
                    
                    log.Log(f"重置体力")
                    if not self.wait_and_click(cpp_dic['to_min'], 0, 0, True, True, self.get_curpower_minpower_panel_region):
                        log.Log(f"点击失败", level='ERROR')
                        return False
                    
                    
                    cm_power = None
                    if is_joint_defense:
                        cm_power = self.joint_defense_disorder_consume_panel_rec_curmincom()
                    else:
                        cm_power = self.get_curpower_minpower()
                    if cm_power is None:
                        return False
                    current_power, min_power = cm_power

                    # 当前体力是否完成
                    if not is_exhausted:
                        if consume_power < min_power:
                            log.Log(f"目标体力任务已完成，本次清理{all_used_power}吨吨值")
                            break
                    
                    # 体力是否耗尽
                    if current_power < min_power:
                        log.Log(f"体力已耗尽")
                        break
            else:
                return True

        return True

    # 联合特勤的相关处理
    def joint_second_panel(self, is_refresh=True, must_s=True, try_cnt=3):
        '''
        priority 优先级为S,A,B
        is_refresh 是否允许使用免费的刷新
        must_s 必须要s才刷
        try_cnt 最大尝试刷新的次数
        '''
        priority_dic = {
            'S': [f'{self.rootpic}\\dailytask\\clear_power\\level_S.png', 
                  f'{self.rootpic}\\dailytask\\clear_power\\level_S2.png'],
            'A': [f'{self.rootpic}\\dailytask\\clear_power\\level_A.png', 
                  f'{self.rootpic}\\dailytask\\clear_power\\level_A2.png'],
            'B': [f'{self.rootpic}\\dailytask\\clear_power\\level_B.png', 
                  f'{self.rootpic}\\dailytask\\clear_power\\level_B2.png',
                  f'{self.rootpic}\\dailytask\\clear_power\\level_B3.png'],
        }
        pos_list = self.joint_second_panel_level_region
        # 获取当前界面等级
        res_level = []
        res_pos = []
        for pos in pos_list:
            f = False
            for level, path in priority_dic.items():
                for p in path:
                    if self.best_template(p, True, pos, threshold=0.9) is not None:
                        res_level.append(level)
                        res_pos.append(pos)
                        f = True
                        break
                if f:
                    break

        if len(res_level) == 0:
            log.Log(f"关卡等级识别失败，请检查当前界面！", level='ERROR')
            return False
        log.Log(f"识别到当前的关卡等级为 {res_level}")

        for i in range(len(res_level)):
            if res_level[i] == 'S':
                if self.auto_click(priority_dic['S'][0], 0, 0, True, True, res_pos[i], 0.9) or\
                    self.auto_click(priority_dic['S'][1], 0, 0, True, True, res_pos[i], 0.9):
                    
                    return True
                
        # 允许刷新
        if is_refresh:
            for _ in range(try_cnt):
                self.auto_move_mouse(600, 1000)
                
                if self.best_template(f'{self.rootpic}\\dailytask\\clear_power\\notfree.png',\
                                       True, self.joint_second_panel_ishave_refresh_region) is not None:
                    log.Log(f"刷新次数已经耗尽")
                    break


                self.auto_move_mouse(600, 1000)
                
                img = self.get_game_screenshot()
                if img is None or img.size == 0:
                    log.Log("未获取到图片", level='ERROR')
                    return None
                free_cnt = self.recognize(img, self.joint_second_panel_refresh_time_region)
                if len(free_cnt) == 0:
                    log.Log(f"未识别到文字", level='ERROR')
                    return False
                        
                free_cnt = int(free_cnt[0][1].split('/')[0])
                # 有条件刷新
                log.Log(f"当前剩余的免费刷新次数：{free_cnt}")
                if free_cnt > 0:
                    
                    if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\refresh.png', \
                                            0, 0, True, True, self.joint_second_panel_ishave_refresh_region):
                        return False
                    
                    if not self.wait_and_click(f'{self.rootpic}\\dailytask\\power_panel\\cancel1.png', 0, 0, True, \
                        time_out=self.task_interval_time, is_Log=False):
                        log.Log(f'无需二次确认 或 点击失败', level='WARNING')
                # 条件不足
                else:
                    log.Log(f"无剩余免费刷新次数")
                    break
                        
                # 更新列表
                res_level = []
                res_pos = []
                for pos in pos_list:
                    f = False
                    for level, path in priority_dic.items():
                        for p in path:
                            if self.best_template(p, True, pos, threshold=0.9) is not None:
                                res_level.append(level)
                                res_pos.append(pos)
                                f = True
                                break
                        if f:
                            break
                            
                if len(res_level) == 0:
                    log.Log(f"关卡等级识别失败，请检查当前界面！", level='ERROR')
                    return False
                log.Log(f"识别到当前的关卡等级为 {res_level}")
                            
                #判断是否有s
                for i in range(len(res_level)):
                    if self.auto_click(priority_dic['S'][0], 0, 0, True, True, res_pos[i], 0.9) or\
                    self.auto_click(priority_dic['S'][1], 0, 0, True, True, res_pos[i], 0.9):
                        
                        return True
                
                
        
        # 此时列表里无s，按优先级来
        if must_s:
            log.Log(f"无S级的副本")
            return False
        else:
            # 找A
            for i in range(len(res_level)):
                if self.auto_click(priority_dic['A'][0], 0, 0, True, True, res_pos[i], 0.9) or\
                    self.auto_click(priority_dic['A'][1], 0, 0, True, True, res_pos[i], 0.9):
                    
                    return True
            
            # 找B
            for i in range(len(res_level)):
                if self.auto_click(priority_dic['B'][0], 0, 0, True, True, res_pos[i], 0.9) or\
                    self.auto_click(priority_dic['B'][1], 0, 0, True, True, res_pos[i], 0.9) or\
                    self.auto_click(priority_dic['B'][2], 0, 0, True, True, res_pos[i], 0.9)    :
                    
                    return True
        
        log.Log(f'未找到任何匹配等级', level='ERROR')
        return False
        


    # 游园街，(之后新增每周跳舞，主要任务：派遣任务，喂饭)
    def garden(self, try_find_s=True):
        '''
        is_must_s 委托任务中如果不是S任务，则尝试刷新
        '''

        log.Log(f"==============正在执行：游园街任务，派遣，喂饭，领取奖励==============")
        time.sleep(self.task_interval_time)
        
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        
        # 点击 游园街
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\garden.png', \
            0, 0, True, True, self.main_ui_down_column):
            log.Log('未找到 游园街', level='ERROR')
            return False
        
        # 点击 游园街面板
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\garden_panel.png', \
            0, 0, True, delay_click=0.5):
            log.Log('未找到 游园街面板', level='ERROR')
            return False
        
        # 点击 收益领取
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\income_receipt.png', \
            0, 0, True):
            log.Log('未找到 收益领取', level='ERROR')
            return False
        
        # 点击 一键投喂
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\feeding.png', \
            0, 0, True):
            log.Log('未找到 一键投喂', level='ERROR')
            return False
        
        # 点击 自动放置
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\auto_put.png', \
            0, 0, True):
            log.Log('未找到 自动放置', level='ERROR')
            return False
        
        
        # 点击 委托任务
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\entrustment.png', \
            0, 0, True):
            log.Log('未找到 委托任务', level='ERROR')
            return False
        
        # 点击 确定按钮（派遣完成会跳出）
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\confirm.png', \
            0, 0, True, time_out=self.task_interval_time, is_Log=False):
            log.Log('未找到 确定按钮，如正常运行无需关注', level='WARNING')
        
        # 处理委托任务相关
        if try_find_s:
            if not self.garden_entrustment_panel_findS():
                log.Log(f"找S任务失败", level="ERROR")
                return False
            
        # 点击 一键派遣
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\one_click_dispatch.png', \
            0, 0, True):
            log.Log('未找到 一件派遣', level='ERROR')
            return False
        

        
        #=========================================
        # 返回 主界面重置
        
        if not self.re_main_ui():
            return False
        
        # 点击 游园街
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\garden.png', \
            0, 0, True, True, self.main_ui_down_column):
            log.Log('未找到 游园街', level='ERROR')
            return False
        
        # 点击 游园任务
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\garden_task.png', \
            0, 0, True):
            log.Log('未找到 游园任务', level='ERROR')
            return False
        
        # 点击 一键领取
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\one_click_get.png', \
            0, 0, True, time_out=self.task_interval_time, is_Log=False):
            log.Log('未找到 一键领取，可能无领取项', level='WARNING')
            
        #  处理弹窗
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\popup_confirm.png', \
            0, 0, True, time_out=self.task_interval_time, is_Log=False):
            log.Log('未发现弹窗', level='WARNING')
            
        return True
        
    # 刷新游园街非s级任务
    def garden_entrustment_panel_findS(self):

        # 识别左侧两个任务
        # 第一个任务
        # 是否为S
        for i in range(4):
            if i < 2:
                # 滑倒最左边
                
                self.auto_wheel(50, -1, 100, 450)
            else:
                # 滑倒最右边
                
                self.auto_wheel(50, 1, 100, 450)
                
            
            if self.best_template(f'{self.rootpic}\\dailytask\\garden\\S.png',\
                True, self.garden_task_entrustment_region[i]) is None:
                # 是否有刷新次数
                if self.best_template(f'{self.rootpic}\\dailytask\\garden\\refresh.png',\
                    True, self.garden_task_entrustment_region[i]) is None:
                    log.Log(f'第 {i+1} 个任务无刷新次数', level="WARNING")
                else:
                    # 执行刷新
                    if not self.wait_and_click(f'{self.rootpic}\\dailytask\\garden\\refresh.png',\
                        0, 0, True, True, self.garden_task_entrustment_region[i]):
                        log.Log('未找到 刷新', level='ERROR')
                        
                    # 点击确认
                    
                    if not self.wait_and_click(f'{self.rootpic}\\dailytask\\power_panel\\confirm3.png', \
                        0, 0, True):
                        log.Log('点击确认失败', level='ERROR')
                        return False
                    
            else:
                log.Log(f'第 {i+1} 个任务已是 S')
                    
        
        return True
        



    # 商店免费体力获取
    def shop_get_free_power(self):
        log.Log(f"==============正在执行：商店免费体力==============")
        time.sleep(self.task_interval_time)
        
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        
        # 点击 商店
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\buy_free_power\\shop.png', \
            0, 0, True, True, self.main_ui_down_column):
            log.Log('未找到 商店', level='ERROR')
            return False
        
        # 点击 补给区
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\buy_free_power\\supply_area.png', \
            0, 0, True):
            log.Log('未找到 补给区', level='ERROR')
            return False
            
        # 点击 组合补给
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\buy_free_power\\combination_supply.png', \
            0, 0, True, True, self.shop_supply_left_column):
            log.Log('未找到 组合补给', level='ERROR')
            return False         
        
        # 点击 日常补给
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\buy_free_power\\daily_supply.png', \
            0, 0, True, True, self.shop_supply_up_column):
            log.Log('未找到 日常补给', level='ERROR')
            return False
        
        # 点击 免费体力
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\buy_free_power\\free_power.png', \
            0, 0, True, threshold=0.92, time_out=self.task_interval_time, is_Log=False):
            log.Log('未找到 免费体力，请检查是否已经领取', level='WARNING')
            return True
        
        # 点击确定
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\power_panel\\confirm3.png', \
            0, 0, True):
            log.Log('点击确认失败', level='ERROR')
            return False
        
        return True

        
    # 弥弥观测站
    def mimier(self, get_stack_time=6):
        '''
        get_stack_time 获取堆栈递归的时间Monday == 0 ... Sunday == 6
        '''
        log.Log(f"==============正在执行：弥弥观测站==============")
        time.sleep(self.task_interval_time)
        get_stack_time = self.get_stack_time
        
        
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        
        # 点击tap的区域
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\tap.png', \
            0, 0, True):
            log.Log('点击tap菜单失败', level='ERROR')
            return False
        
        # 点击弥弥观测站
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\mimier_station.png', \
            0, 0, True, True, self.main_ui_Tap):
            log.Log('点击 弥弥观测站 失败', level='ERROR')
            return False
        
        # =====点击空白区域，关闭弹窗=====
        
        time.sleep(self.task_interval_time)
        self.auto_click('-', 750, 80, False)
        
        # 点击一键领取
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\one_click_receive.png', \
            0, 0, True, threshold=0.9, time_out=self.task_interval_time, is_Log=False):
            log.Log('未派遣 或 当前派遣未结束 或 点击一键领取失败，如正常运行无需关注', level='WARNING')
        
        # 点击 "空白处继续"
        for _ in range(20):
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\click_blank.png', \
                0, 0, True, time_out=self.task_interval_time, is_Log=False):
                log.Log('无空白处继续 或 点击 空白处继续 失败，如正常运行无需关注', level='WARNING')
                break
            
        # 点击 一键派遣
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\one_click_dispatch.png', \
            0, 0, True, threshold=0.9, time_out=self.task_interval_time, is_Log=False):
            log.Log('点击 一键派遣 失败', level='ERROR')
        
        
        
        
        # 每周六或周日领取 堆栈递归
        import datetime
        now = datetime.datetime.now()
        if now.weekday() == get_stack_time:
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\stack.png', \
                0, 0, True):
                log.Log('点击 堆栈递归 失败', level='ERROR')
                return False
        
            # 然后相关操作
            # 点击 开启演算
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\enable_computation.png', \
                0, 0, True, time_out= self.task_interval_time, is_Log=False):
                log.Log('点击 开启演算 失败', level='ERROR')
                return True
            
            # 点击 递归演算中
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\stacking.png', \
                0, 0, True):
                log.Log('点击 递归演算中 失败', level='ERROR')
                return False
            
        else:
            log.Log(f"未到堆栈递归的设定领取时间")
    
        return True
    
    # 领取每日&每周奖励
    def get_daily_weekly_reward(self):
        log.Log(f"==============正在执行：领取每日&每周奖励==============")
        time.sleep(self.task_interval_time)
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        
        l = ['daily_task', 'week_task']
        for name in l:
            # 回到主界面
            
            if not self.re_main_ui():
                return False
            
            # 点击任务
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\task\\task.png', \
                0, 0, True):
                log.Log('点击 任务 失败', level='ERROR')
                return False
            
            # 点击每日 / 周常任务
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\task\\{name}.png', \
                0, 0, True):
                log.Log('点击 {name} 失败', level='ERROR')
                return False
            
            
            # 点击 一键领取 应二次领取
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\task\\one_click_get.png', \
                0, 0, True, time_out=self.task_interval_time, is_Log=False):
                log.Log('点击 一键领取 失败，可能无待领取项', level='WARNING')
                continue
            
            
            self.wait_and_click(f'{self.rootpic}\\dailytask\\task\\continue.png', \
                0, 0, True, time_out=self.task_interval_time, is_Log=False)
            
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\task\\one_click_get.png', \
                0, 0, True, time_out=self.task_interval_time, is_Log=False):
                log.Log('点击 一键领取 失败，可能无待领取项', level='WARNING')
                continue
                
        return True
            
    # 联防协议 奖励领取
    def joint_defense_reward(self):
        log.Log(f"==============正在执行：联防协议 每日奖励领取==============")
        time.sleep(self.task_interval_time)
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        
        # 点击活动 （使用菜单键进行定位）
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\tap.png', 0, 160, True):
            log.Log(f'活动点击失败', level='ERROR')
            return False
        
        # 先返回顶部
        
        self.auto_wheel(50, 1, 200, 300)

        # 遍历菜单，使用ocr，点击联防协议
        for i in range(10):
            time.sleep(self.task_interval_time)
            img = self.get_game_screenshot()
            if img is None or img.size == 0:
                log.Log("未获取到图片", level='ERROR')
                return False
            
            rect = self.find_text(img, '联防协议', self.act_left_region)
            if rect is not None:
                if not self.auto_click('-', rect[0], rect[1], False):
                    log.Log(f"联防协议点击失败", level="ERROR")
                    return False
                else:
                    break
        
            # 下滑
            self.auto_wheel(10, -1, 200, 300)
            
            
        # 一键领取资源
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\joint_defense_main_oneclick.png', \
            0, 0, True, True, self.jointDefense_main_oneclick_region, time_out=self.task_interval_time, is_Log=False):
            log.Log(f"一键领取资源失败，可能是无资源领取", level="WARNING")
        else:  
            self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\continue.png', \
                0, 0, True)
            
        return True
    
    
    # 联防协议 失序关
    def joint_defense_disorder(self, mode='mopup',consume_communication=-1):
        '''
        mode 刷取模式，扫荡还是战斗
        consume_communication 要消耗的求援通讯数，-1为消耗所有，其余非负数为目标消耗值
        '''
        
        log.Log(f"==============正在执行：联防协议 失序关==============")
        time.sleep(self.task_interval_time)
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        
        # 点击活动 （使用菜单键进行定位）
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mimier\\tap.png', 0, 160, True):
            log.Log(f'活动点击失败', level='ERROR')
            return False
        
        # 先返回顶部
        
        self.auto_wheel(50, 1, 200, 300)

        # 遍历菜单，使用ocr，点击联防协议
        for i in range(10):
            time.sleep(self.task_interval_time)
            img = self.get_game_screenshot()
            if img is None or img.size == 0:
                log.Log("未获取到图片", level='ERROR')
                return False
            
            rect = self.find_text(img, '联防协议', self.act_left_region)
            if rect is not None:
                if not self.auto_click('-', rect[0], rect[1], False):
                    log.Log(f"联防协议点击失败", level="ERROR")
                    return False
                else:
                    break
        
            # 下滑
            self.auto_wheel(10, -1, 200, 300)
            
            
        # 一键领取资源
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\joint_defense_main_oneclick.png', \
            0, 0, True, True, self.jointDefense_main_oneclick_region, time_out=self.task_interval_time, is_Log=False):
            log.Log(f"一键领取资源失败，可能是无资源领取", level="WARNING")
        else:  
            self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\continue.png', \
                0, 0, True)
            
        # 前往作战
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\clear_power\\joint_defense_main_gotofight.png', 0, 0, True):
            log.Log(f"点击 前往作战 失败", level="ERROR")
            return False
            
        # 点击 失序援区
        
        if not self.wait_and_click(f'{self.rootpic}\\joint_defense\\joint_defense_disorder.png', 0, 0, True):
            log.Log(f"点击 失序援区 失败", level="ERROR")
            return False
        
        # 首次进入可能会弹窗，关闭弹窗
        
        if not self.wait_and_click(f'{self.rootpic}\\joint_defense\\click_blank.png', 0, 0, True, time_out=self.task_interval_time, is_Log=False):
            log.Log(f"未检测到弹窗，如正常运行无需关注", level="WARNING")

        
        
        # 点击 关卡
        
        if not self.wait_and_click(f'{self.rootpic}\\joint_defense\\level.png', 0, 0, True):
            log.Log(f"点击 关卡 失败", level="ERROR")
            return False
        
        # 交给通用体力面板，并改为联防协议模式
        
        if consume_communication == -1:
            if not self.common_power_panel(mode, consume_communication, True, is_joint_defense=True):
                return False
        elif consume_communication > 0:
            if not self.common_power_panel(mode, consume_communication, False, is_joint_defense=True):
                return False
        else:
            log.Log(f"目标体力应该为正数！", level='ERROR')
            return False
        
        
        return True
        

    # 联防协议 消耗面板 当前和最小求援通讯识别
    def joint_defense_disorder_consume_panel_rec_curmincom(self, is_reset=False):
        '''
        is_reset 在识别前是否重置关卡倍数
        '''
        
        # 重置体力
        if is_reset:
            
            log.Log(f"重置体力")
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\power_panel\\to_min.png',\
                0, 0, True, True, self.get_curpower_minpower_panel_region):
                log.Log(f"点击失败", level='ERROR')
                return None
            
        
        # 获取当前和最小求援通讯
        img = self.get_game_screenshot()
        if img is None or img.size == 0:
            log.Log("未获取到图片", level='ERROR')
            return None

        res = self.recognize(img, self.joint_defense_disorder_consume_panel_curcom_region)
        if len(res) == 0:
            log.Log(f"当前 求援通讯 识别失败", level='ERROR')
            return None
        current_com = int(res[0][1])
        log.Log(f"当前求援通讯数：{current_com}")

        res = self.recognize(img, self.joint_defense_disorder_consume_panel_mincom_region)
        if len(res) == 0:
            log.Log(f"最小消耗求援通讯识别失败", level='ERROR')
            return None
        min_com = int(res[0][1])
        log.Log(f"副本最低所需求援通讯：{min_com}")
        
        return current_com, min_com
    
    '''
    debug：joint_defense_disorder() 进行弹窗缩回的适配
    '''
    
    # 领取大月卡奖励
    def monthly_pass(self):
        log.Log(f"==============正在执行：大月卡奖励领取==============")
        time.sleep(self.task_interval_time)
        # 做主界面判断
        
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        
        # 点击大月卡
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\monthly_pass\\monthly_pass.png',\
            0, 0, True):
            log.Log(f"点击 大月卡 失败", level="ERROR")
            return False
        
        # 首次进入会有空白区域，点击空白区域
        time.sleep(self.task_interval_time)
        if not self.auto_click('-', 750, 80, False):
            log.Log(f"点击空白处失败", level="WARNING")
            
        # 遍历三个任务   
        l = ['daily_task', 'weekly_task', 'challenge_task']
        
        # 点击任务
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\monthly_pass\\task.png',\
            0, 0, True):
            log.Log(f"点击 任务 失败", level="ERROR")
            return False
        
        for name in l:      
            # 点击每日 / 周常任务 / 挑战任务
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\monthly_pass\\{name}.png', \
                0, 0, True):
                log.Log('点击 {name} 失败', level='ERROR')
                return False
            
            
            # 点击 一键领取 应二次领取
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\monthly_pass\\oneclick_receive.png', \
                0, 0, True, time_out=self.task_interval_time, is_Log=False):
                log.Log('点击 一键领取 失败，可能无待领取项', level='WARNING')
                continue
            
            self.wait_and_click(f'{self.rootpic}\\dailytask\\monthly_pass\\continue.png', \
                0, 0, True, time_out=self.task_interval_time, is_Log=False)
            
            
            if not self.wait_and_click(f'{self.rootpic}\\dailytask\\monthly_pass\\oneclick_receive.png', \
                0, 0, True, time_out=self.task_interval_time, is_Log=False):
                log.Log('点击 一键领取 失败，可能无待领取项', level='WARNING')
                continue         
        
        
        # 返回主界面，重置状态
        
        if not self.re_main_ui():
            return False
        
        # 点击大月卡
        time.sleep(self.task_interval_time)
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\monthly_pass\\monthly_pass.png',\
            0, 0, True):
            log.Log(f"点击 大月卡 失败", level="ERROR")
            return False
        
        # 点击一键领取
        
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\monthly_pass\\oneclick_receive.png',\
            0, 0, True, time_out=self.task_interval_time, is_Log=False):
            log.Log(f"点击 一键领取 失败，可能无领取项", level="WARNING")
        else:
            
            self.auto_keyboard(0x1B)
        
        return True
    
    
    # 邮件领取
    def mail(self):
        log.Log(f"==============正在执行：邮件领取==============")
        time.sleep(self.task_interval_time)
        # 做主界面判断
        if not self.istargetui('主界面'):
            log.Log(f'当前界面不在 主界面，该任务请返回到主界面再尝试', level='ERROR')
            return False
        

        # 点击邮件
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mail\\mail.png',\
            0, 0, True):
            log.Log(f"点击 邮件 失败", level="ERROR")
            return False
        
        # 点击一键领取
        if not self.wait_and_click(f'{self.rootpic}\\dailytask\\mail\\oneclick_receive.png',\
            0, 0, True, time_out=self.task_interval_time, is_Log=False):
            log.Log(f"点击 一键领取 失败，可能无领取项", level="WARNING")
        else:
            self.auto_keyboard(0x1B)
            
        return True
            


    
    
    # 每周四的商店碎片
    
    
    # 每日的商店碎片