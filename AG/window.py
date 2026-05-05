import win32gui
import win32con
import pyautogui
import psutil
import os
import subprocess
import time
import log

class Start:
    def __init__(self, title, game_path, process_name):
        self.title = title
        self.hwnd = None
        self.game_path = game_path
        self.process_name = process_name

    # 回调函数，配合win32gui.EnumWindows(self.callback, None)
    def callback(self, hwnd_, extra):
        try:
            window_text = win32gui.GetWindowText(hwnd_)
            if self.title in window_text:
                self.hwnd = hwnd_
                return False
        except:
            pass
        
        return True

    #获取窗口
    def get_window(self):
        self.hwnd = None #防止查找失败时残留无效句柄
        try:
            win32gui.EnumWindows(self.callback, None)
        except:
            pass
        return self.hwnd
     
    # 激活窗口
    def activate_window(self):
        self.get_window()

        if not self.hwnd:
            log.Log(f"未找到窗口", level='ERROR')
            return False

        # 恢复目标窗口
        win32gui.ShowWindow(self.hwnd, win32con.SW_RESTORE)
        # 置顶目标窗口
        win32gui.SetForegroundWindow(self.hwnd)

        log.Log(f"已激活窗口：{win32gui.GetWindowText(self.hwnd)}")

        return True

    # 判断游戏进程是否正在运行
    def is_running(self):
        for proc in psutil.process_iter(["name"]):
            # try用来忽略无权限进程
            try:
                if proc.info["name"] == self.process_name:
                    log.Log(f"目标进程正在运行中")
                    return True, proc.pid
            except:
                continue
        return False, None
    
    def start_game(self):
        #判断路径是否存在
        if not os.path.exists(self.game_path):
            raise FileNotFoundError(f"该路径不存在：{self.game_path}", level='ERROR')
        
        #创建独立控制台
        game_process = subprocess.Popen(
            [self.game_path],
            creationflags=subprocess.CREATE_NEW_CONSOLE, # 独立运行
            shell=False  # 安全启动
        )

        return game_process
    
    # 等待窗口出现,最多30s
    def wait_window(self, timeout=30):
        start_time = time.time()
        while timeout > time.time() - start_time:
            if self.get_window() != None:
                return True
            time.sleep(1)
        return False
        

    # 总启动模块
    def auto_launch_game(self):
        # 检测路径
        if not self.game_path:
            raise ValueError("game_path 未配置", level='ERROR')
        
        #检测游戏是否运行
        f, pid = self.is_running()
        if f:
            log.Log("游戏已运行")
            if self.activate_window():
                log.Log(f"成功激活目标窗口")
            
            return True
        
        log.Log(f"正在启动游戏")
        game_process = self.start_game()  

        if self.wait_window():
            if self.activate_window():
                log.Log(f"成功激活目标窗口")
                return True
            return False
        else:
            log.Log(f"寻找窗口超时", level='ERROR')
            return False
        



class WindowRect(Start):
    def __init__(self, title, game_path, process_name):
        super().__init__(title, game_path, process_name)
        
        self.win_left = None
        self.win_top = None
        self.win_right = None
        self.win_bottom = None
        
        # 客户端位置
        self.client_left = None
        self.client_top = None

    #获取游戏窗口位置
    def get_window_rect(self):
        self.get_window()

        if not self.hwnd:
            log.Log("坐标获取失败", level='ERROR')
            return None
        
        
        #(左,上,右,下)
        self.win_left, self.win_top, self.win_right, self.win_bottom = win32gui.GetWindowRect(self.hwnd)
        return self.win_left, self.win_top, self.win_right, self.win_bottom
    
    #获取客户端的真实位置
    def get_client_rect(self):
        rect = self.get_window_rect()
        if not rect:
            return None
        
        point = win32gui.ClientToScreen(self.hwnd, (self.win_left, self.win_top))
        self.client_left, self.client_top = point
        return point
    
    #获取图片在屏幕上的坐标
    def find_image(self,img_path,confidence=0.8):
        '''
        图像识别
        '''
        screen_x, screen_y = None, None

        return screen_x, screen_y
    
    #把屏幕坐标转化为游戏内相对坐标
    def calculate_relative_pos(self, screen_x, screen_y):
        rect = self.get_window_rect()
        if not rect:
            return None
        
        rx = screen_x - self.win_left
        ry = screen_y - self.win_top

        return rx, ry

    # 坐标越界判断
    def is_in_window(self, screen_x, screen_y):
        rect = self.get_window_rect()
        if not rect:
            return False
        
        return self.win_left <= screen_x <= self.win_right and self.win_top <= screen_y <= self.win_bottom

