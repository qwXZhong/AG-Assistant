from GUI import MainWindow, QApplication
import sys
import traceback
from log import Log


def global_exception_hook(exc_type, exc_value, exc_traceback):
    '''全局异常钩子'''
    error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    Log(f"程序发生异常：\n{error_msg}", level='CRITICAL')
    # 打印到控制台
    # print(f"程序发生异常：\n{error_msg}", file=sys.stderr)
    # 调用GUI弹窗
    MainWindow().show_error_dialog(error_msg)

 

    
if __name__ == '__main__':
    
    
    sys.excepthook = global_exception_hook
    
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
    
    