import window
import Automatic
import cv2
import task
import time
import win32gui
import win32con
import win32api
import pyautogui

if __name__ == "__main__":
    
    tit = "AetherGazer"
    path = r"F:\\AetherGazerStarter\\AetherGazer\\AetherGazer.exe"
    pn = "AetherGazer.exe"
    
    '''
    tit = "Edge"
    path = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    pn = "msedge.exe"
    '''


    
    winSt = window.Start(
        title=tit,
        game_path=path,
        process_name=pn
    )
    
    winSt.auto_launch_game()

    # while not winSt.is_running():
    #     pass

    winRect = window.WindowRect(
        title=tit,
        game_path=path,
        process_name=pn
    )
        
    p = Automatic.Automatic(
        title=tit,
        game_path=path,
        process_name=pn
    )



    t = task.Task(
        title=tit,
        game_path=path,
        process_name=pn,
        target="联合特勤",
        number=1,
        consume_power=160,
        is_exhausted=True,
        joint_must_s=False,
        template_resolution='1920*1200',
        is_standby=False,
        standby_target='联防协议',
        standby_target_number=3
    )

    t.taskdic = {
            "登录界面": True,
            "每日活跃度": True,
        }

    t.act_dic = {
            "角色互动": True,
            "尝试领取额外体力": True,
            "进入指定副本并消耗体力": True,
            "游园街": True,
            "商店免费体力": True,
            "弥弥尔": True,
            "领取每日每周任务奖励": True,
            "大月卡": True,
            "邮件": True
        }

    # t.clear_power('酬金委托', 1, use_class_parameter=False,is_exhausted=True)
    t.all_task()
    # t.clear_power("联防协议", 3 , is_exhausted=True, use_class_parameter=False)
    # t.garden()
    
    #t.joint_defense_disorder(mode='mopup', consume_communication=25)
    #t.monthly_pass()
    # t.mail()
    # t.re_main_ui()
    # t.joint_defense_disorder(consume_communication=-1)
    

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
    # time.sleep(1)
    # t.login()
    # for idx, name in enumerate(name_dic.keys()):
    #     print(f"当前目标副本 {name}, 难度 {(idx + 1) % 5}")
    #     t.re_main_ui()
    #     time.sleep(1)
    #     t.clear_power(name, (idx + 1) % 5, consume_power=45, use_class_parameter=False)
    #     time.sleep(1)

    # # 110, 540, 172, 610
    # time.sleep(2)
    # t.medium_second_panel(must_s=False, try_cnt=1)

    #t.clear_power('联合特勤', 1, consume_power=-1, is_exhausted=True, joint_must_s=True)
