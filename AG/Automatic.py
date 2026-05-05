import win32gui
import win32con
import win32ui
import win32api
import ctypes
import cv2
import numpy as np
from mss import mss
from PIL import Image
import log
import pyautogui
import time


from window import Start, WindowRect

class Automatic(WindowRect):
    def __init__(self, title, game_path, process_name):
        WindowRect.__init__(self, title, game_path, process_name)
        self.myMss = None

    def init_mss(self):
        if self.myMss is None:
            self.myMss = mss()

    # 获取游戏内截图
    def get_game_screenshot(self):
        # 更换为MSS
        rect = self.get_window_rect()
        if not rect:
            return None
        
        self.init_mss()
        
        left, top, right, bottom = rect
        img = self.myMss.grab({'top': top, 'left': left, 'width': right - left, 'height': bottom - top})
        img = np.array(img);
        #cv2.imshow('img', img)

        return img
    
    # isCut是否指定匹配位置（是否指定区域）， pos=[x1,y1,x2,y2] 左上角和右下角的坐标
    # 若边界传入的数值越界，自动使用边界值
    def best_template(self, template_path, isCut=False, pos=None, threshold=0.8):
        # 待匹配图片
        img = self.get_game_screenshot()
        if img is None or img.size == 0:
            log.Log("未获取到图片", level='DEBUG')
            return None
        img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY) # 转灰度图像
        
        
        # 模板图片
        template = cv2.imread(template_path, 0)
        if template is None:
            log.Log(f'无对应模板图片', level='DEBUG')
            return None

        # 获取模板图片的大小
        w, h = template.shape[::-1]

        offset_x, offset_y = 0, 0
        # 匹配
        if isCut:
            if pos is None or len(pos) != 4:
                log.Log(f"目前为裁剪模式，未传入/传入参数数量有误！", level='DEBUG')
                return None
            else:
                img_h, img_w = img.shape
                x1, y1, x2, y2 = pos
            
                # 边界修正
                x1, x2 = max(0, x1), min(x2, img_w)
                y1, y2 = max(0, y1), min(y2, img_h)

                if x1 >= x2 or y1 >= y2:
                    log.Log(f"pos应为[左上角，右下角]，且x1<x2、y1<y2！", level='DEBUG')
                    return None

                img = img[y1:y2, x1:x2]
                offset_x, offset_y = x1, y1
            
        res = cv2.matchTemplate(img, template, cv2.TM_CCOEFF_NORMED) #归一化相关系数匹配，值越大匹配度越高
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res) 

        if max_val < threshold:
            #log.Log(f'未匹配到目标，相似度：{max_val:.2f}', level='DEBUG')
            return None

        #计算中心坐标
        x, y = max_loc
        center_x = offset_x + x + w // 2
        center_y = offset_y + y + h // 2

        return center_x, center_y
    
    # 自动点击,flag=True进行模板匹配(px,py)为偏移量，否则直接点击目标点(px,py)
    def auto_click(self, template_path, px, py, flag=True, isCut=False, pos=None, threshold=0.8):
        rect = self.get_window_rect()
        if rect is None:
            log.Log(f"窗口坐标获取失败", level='DEBUG')
            return False
        left, top, right, bottom = rect
        
        if flag:
            if self.best_template(template_path, isCut, pos, threshold) is None:
                #log.Log(f'点击失败', level='DEBUG')
                return False
                
            x, y = self.best_template(template_path, isCut, pos, threshold)
                
            x = x + left + px
            y = y + top + py
            # 设置坐标
            log.Log(f"尝试移动鼠标到：({x}, {y})", level='DEBUG')
            win32api.SetCursorPos((x, y))
        else:
            log.Log(f"尝试移动鼠标到：({left + px}, {top + py})", level='DEBUG')
            win32api.SetCursorPos((left + px, top + py))

        # 点击(相对位移x，y，滚轮，事件，额外信息)
        time.sleep(0.5)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
        time.sleep(0.05)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
        # win32api.mouse_event(dx=0, dy=0, dwData=0, dwFlags=win32con.MOUSEEVENTF_LEFTDOWN, dwExtraInfo=0)
        # win32api.mouse_event(dx=0, dy=0, dwData=0, dwFlags=win32con.MOUSEEVENTF_LEFTUP, dwExtraInfo=0)
        return True


    def auto_keyboard(self, key):
        win32api.keybd_event(key, 0, 0, 0)
        time.sleep(0.05)
        win32api.keybd_event(key, 0, 2, 0)

    # 滚轮操作
    def auto_wheel(self, cnt, distance, px, py):
        if self.auto_move_mouse(px, py):
            time.sleep(1)
            for _ in range(cnt):
                win32api.mouse_event(win32con.MOUSEEVENTF_WHEEL, 0, 0, distance, 0)
                time.sleep(0.01)
            return True
        return False

    # 移动鼠标到指定位置
    def auto_move_mouse(self, px, py):
        rect = self.get_window_rect()
        if rect is None:
            log.Log(f"窗口坐标获取失败", level='DEBUG')
            return False
        left, top, right, bottom = rect

        x = left + px
        y = top + py

        log.Log(f"尝试移动鼠标到：({x}, {y})", level='DEBUG')
        win32api.SetCursorPos((x, y))

        return True
        

