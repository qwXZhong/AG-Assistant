import datetime
from PyQt6.QtCore import QObject, pyqtSignal, Qt

# 全局线程日志发射器
class LogSignal(QObject):
    log_signal = pyqtSignal(str, str)
log_sender = LogSignal()


# 全局存储日志输出函数（由GUI传入）
_log_callback = None

def set_log_callback(callback):
    """GUI 调用这个方法，把自己的日志函数传进来"""
    global _log_callback
    _log_callback = callback
    # 绑定信号到回调函数
    log_sender.log_signal.connect(callback, Qt.ConnectionType.QueuedConnection)

def Log(content, level='INFO'):
    global _log_callback
    
    '''
    level 日志等级 为DEBUG调试级, INFO信息级, WARNING警告级, ERROR错误级, CRITICAL致命级    
    '''
    
    
    level_is_norm = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    if level not in level_is_norm:
        Log(f"日志等级错误，请检查日志规范 | 目标日志信息为：{content}", level='DEBUG')
        return False
    
    # 关闭debug
    # if level == 'DEBUG':
    #     return True
    
    
    now = datetime.datetime.now()
    time_str = now.strftime("%Y-%m-%d %H:%M:%S")
    log_str = f"[{level:<8}| {time_str:<20}] {content}"
    
    # 如果有回调函数, 就把信号发到回调函数中
    if _log_callback is not None:
        log_sender.log_signal.emit(log_str, level)
    else:
        print(log_str)
    
    return True

