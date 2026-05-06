import os
import configparser
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QFileDialog, QCheckBox, QListWidget, QPlainTextEdit, QSpinBox,
    QMessageBox
)
from PyQt6.QtCore import Qt, QSize,  QThread, pyqtSignal
from PyQt6.QtGui import QPixmap, QTextCursor, QFont
from qfluentwidgets import (
    FluentWindow, PushButton, FluentIcon, IconWidget,
    NavigationItemPosition, SwitchButton, ComboBox
)
from log import Log
import traceback


class MainWindow(FluentWindow): 
    def __init__(self):
        super().__init__()
        global_font = QFont("Microsoft YaHei")
        global_font.setPointSize(10)
        QApplication.instance().setFont(global_font)
        
        # ========== 先初始化所有核心变量（避免属性未定义） ==========
        # 游戏路径
        self.game_path = ""
        # 一条龙任务变量
        self.is_role_interaction = False
        self.is_get_power = False
        self.is_clear_power = False
        self.is_garden = False
        self.is_shop_get_free_power = False
        self.is_mimier = False
        self.is_get_daily_weekly_reward = False
        self.is_monthly_pass = False
        self.is_mail = False
        # 体力分配
        self.main_dungeon = "酬金委托"       # 主副本（默认值）
        self.sub_dungeon = "模拟作战"        # 备用副本（默认值）
        self.main_dungeon_level = 1          # 主副本等级（默认值） 
        self.sub_dungeon_level = 1           # 备用副本等级（默认值）
        self.deplete_power = False           # 是否耗尽体力
        self.target_power = "0"            # 目标体力（默认值）
        self.dungeon_max_level = {
            "酬金委托": 5,
            "模拟作战": 6,
            "因子采集": 5,
            "深层勘探": 5,
            "极限萃取": 5,
            "失落遗迹": 6,
            "战场清扫": 5,
            "神域解析": 5,
            "联防协议": 3
        }
        # 一条龙特殊设置
        self.is_standby = True
        self.joint_is_refresh = True
        self.joint_must_s = True
        self.mode = "扫荡"
        self.find_second_dengeon_panel_time = 10
        
        # 日志设置
        self.debug_log = False
        
        # 其他任务
        self.is_exhausted_com = True
        self.target_com = "0"
        
        
        # 任务参数设置
        self.interval_time = 2
        self.ocr_use_gpu = False
        self.ocr_collect_time = 20
        self.template_resolution = "1920*1200"

        # ========== 初始化配置文件相关 ==========
        self.config = configparser.ConfigParser()
        cur_dir = os.path.dirname(os.path.abspath(__file__))
        parent_dir = os.path.dirname(cur_dir)
        self.config_dir = os.path.join(parent_dir, 'config')
        self.config_path = os.path.join(self.config_dir, "config.ini")
        os.makedirs(self.config_dir, exist_ok=True)

        # ========== 先创建界面容器，再加载配置（关键顺序调整） ==========
        self._init_interface_containers()  # 先创建界面容器
        self.load_config()                 # 加载配置（此时还未创建界面元素，只加载到变量）
        self._init_navigation()            # 初始化侧边栏导航
        self._init_home_ui()               # 初始化首页UI
        self._init_oneDragon_setting_ui()     # 初始化一条龙设置UI
        self._init_other_task_ui()
        self._init_settings_ui()           # 初始化设置页UI（创建所有界面元素）
        self._bind_signals()               # 最后统一绑定信号（避免初始化时触发save_config）

        # ========== 窗口基础设置 ==========
        self.setWindowTitle('AG Assistant')
        self.resize(900, 650)
        
        # 设置日志回调函数
        from log import set_log_callback
        set_log_callback(self.append_log)
        
        

    def _init_interface_containers(self):
        """初始化界面容器（提前创建，避免空引用）"""
        self.homeInterface = QWidget()
        self.homeInterface.setObjectName("HomeInterface")
        self.oneDragonInterface = QWidget()
        self.oneDragonInterface.setObjectName("oneDragonInterface")
        self.otherTaskInterface = QWidget()
        self.otherTaskInterface.setObjectName("otherTaskInterface")
        self.setInterface = QWidget()
        self.setInterface.setObjectName('setInterface')

    def _init_navigation(self):
        """初始化侧边栏导航"""
        self.addSubInterface(
            interface=self.homeInterface,
            icon=FluentIcon.HOME,
            text="首页"
        )
        self.addSubInterface(
            interface=self.oneDragonInterface,
            icon=FluentIcon.SHARE,
            text="一条龙设置",
        )
        self.addSubInterface(
            interface=self.otherTaskInterface,
            icon=FluentIcon.LINK,
            text="其他任务",
        )
        self.addSubInterface(
            interface=self.setInterface,
            icon=FluentIcon.SETTING,
            text="通用设置",
            position=NavigationItemPosition.BOTTOM
        )

    # 窗口开启时的操作
    def showEvent(self, event):
        super().showEvent(event)
        nav = self.navigationInterface
        nav.setMinimumWidth(180)
        nav.setMaximumWidth(180)
        nav.setFixedWidth(180)
        nav.setExpandWidth(180)
        nav.setCollapsible(False)
        nav.update()
        self.update()
        
    # 窗口关闭时的操作
    def closeEvent(self, event):
        if hasattr(self, 'task_thread') and self.task_thread.isRunning():
            self.task_thread.terminate() 
            self.task_thread.wait()
        super().closeEvent(event)

    # ========== 配置文件操作 ==========
    def save_config(self):
        """保存配置文件（先同步类变量，再写配置，避免双数据源不一致）"""
        # 确保所有section存在
        for section in ["PATH", "onedragon", "POWER", "SETTINGS", "OtherTask","onedragonSpcial"]:
            if not self.config.has_section(section):
                self.config.add_section(section)

        # ========== 同步界面控件 → 类内变量 ==========
        # 游戏路径
        self.game_path = self.path_input.text().strip() if hasattr(self, 'path_input') else self.game_path
        
        # 一条龙设置
        self.is_role_interaction = getattr(self, 'check_role_interaction', None).isChecked() if hasattr(self, 'check_role_interaction') else self.is_role_interaction
        self.is_get_power = getattr(self, 'check_get_power', None).isChecked() if hasattr(self, 'check_get_power') else self.is_get_power
        self.is_clear_power = getattr(self, 'check_clear_power', None).isChecked() if hasattr(self, 'check_clear_power') else self.is_clear_power
        self.is_garden = getattr(self, 'check_garden', None).isChecked() if hasattr(self, 'check_garden') else self.is_garden
        self.is_shop_get_free_power = getattr(self, 'check_shop_get_free_power', None).isChecked() if hasattr(self, 'check_shop_get_free_power') else self.is_shop_get_free_power
        self.is_mimier = getattr(self, 'check_mimier', None).isChecked() if hasattr(self, 'check_mimier') else self.is_mimier
        self.is_get_daily_weekly_reward = getattr(self, 'check_get_daily_weekly_reward', None).isChecked() if hasattr(self, 'check_get_daily_weekly_reward') else self.is_get_daily_weekly_reward
        self.is_monthly_pass = getattr(self, 'check_monthly_pass', None).isChecked() if hasattr(self, 'check_monthly_pass') else self.is_monthly_pass
        self.is_mail = getattr(self, 'check_mail', None).isChecked() if hasattr(self, 'check_mail') else self.is_mail
 
        # 体力设置
        main_dungeon_text = self.main_dungeon
        if hasattr(self, 'main_dungeon_list') and self.main_dungeon_list.currentItem():
            main_dungeon_text = self.main_dungeon_list.currentItem().text()
        self.main_dungeon = main_dungeon_text  # 同步到类变量
        
        sub_dungeon_text = self.sub_dungeon
        if hasattr(self, 'sub_dungeon_list') and self.sub_dungeon_list.currentItem():
            sub_dungeon_text = self.sub_dungeon_list.currentItem().text()
        self.sub_dungeon = sub_dungeon_text  # 同步到类变量
        
        self.main_dungeon_level = getattr(self, 'main_dengeon_level_spin', None).value() if hasattr(self, 'main_dengeon_level_spin') else self.main_dungeon_level
        self.sub_dungeon_level = getattr(self, 'sub_dengeon_level_spin', None).value() if hasattr(self, 'sub_dengeon_level_spin') else self.sub_dungeon_level
        
        self.deplete_power = getattr(self, 'check_deplete_power', None).isChecked() if hasattr(self, 'check_deplete_power') else self.deplete_power
        
        target_power_val = self.target_power
        if hasattr(self, 'target_power_input') and self.target_power_input.text().strip():
            target_power_val = self.target_power_input.text().strip()
        self.target_power = target_power_val  # 同步到类变量
        
        # 一条龙特殊设置
        self.is_standby = getattr(self, 'is_standby_switch', None).isChecked() if hasattr(self, 'is_standby_switch') else self.deplete_power
        self.joint_is_refresh = getattr(self, 'joint_is_refresh_switch', None).isChecked() if hasattr(self, 'joint_is_refresh_switch') else self.joint_is_refresh
        self.joint_must_s = getattr(self, 'joint_must_s_switch', None).isChecked() if hasattr(self, 'joint_must_s_switch') else self.joint_must_s
        self.mode = getattr(self, 'mode_ComboBox', None).currentText() if hasattr(self, 'mode_ComboBox') else self.mode
        self.find_second_dengeon_panel_time = getattr(self, 'find_second_dengeon_panel_time_QSpinBox', None).value() if hasattr(self, 'find_second_dengeon_panel_time_QSpinBox') else self.find_second_dengeon_panel_time
        
        # 日志设置
        self.debug_log = getattr(self, 'debug_check', None).isChecked() if hasattr(self, 'debug_check') else self.debug_log

        # 其他任务
        self.is_exhausted_com = getattr(self, 'is_exhausted_com_switch', None).isChecked() if hasattr(self, 'is_exhausted_com_switch') else self.is_exhausted_com
        
        target_com_val = self.target_com
        if hasattr(self, 'target_com_input') and self.target_com_input.text().strip():
            target_com_val = self.target_com_input.text().strip()
        self.target_com = target_com_val  # 同步到类变量

        # 任务参数设置
        self.interval_time = getattr(self, 'interval_time_layout_QSpinBox', None).value() if hasattr(self, 'interval_time_layout_QSpinBox') else self.interval_time
        self.ocr_use_gpu = getattr(self, 'ocr_use_gpu_switch', None).isChecked() if hasattr(self, 'ocr_use_gpu_switch') else self.ocr_use_gpu
        self.ocr_collect_time = getattr(self, 'ocr_collect_time_QSpinBox', None).value() if hasattr(self, 'ocr_collect_time_QSpinBox') else self.ocr_collect_time
        self.template_resolution = getattr(self, 'template_resolution_ComboBox', None).currentText() if hasattr(self, 'template_resolution_ComboBox') else self.template_resolution



        # ========== 类变量 → 配置文件 ==========
        # 游戏路径配置
        self.config.set("PATH", "game_path", self.game_path)

        # 一条龙设置
        self.config.set("onedragon", "role_interaction", str(self.is_role_interaction))
        self.config.set("onedragon", "get_power", str(self.is_get_power))
        self.config.set("onedragon", "clear_power", str(self.is_clear_power))
        self.config.set("onedragon", "garden", str(self.is_garden))
        self.config.set("onedragon", "shop_get_free_power", str(self.is_shop_get_free_power))
        self.config.set("onedragon", "mimier", str(self.is_mimier))
        self.config.set("onedragon", "get_daily_weekly_reward", str(self.is_get_daily_weekly_reward))
        self.config.set("onedragon", "monthly_pass", str(self.is_monthly_pass))
        self.config.set("onedragon", "mail", str(self.is_mail))

        # 体力设置
        self.config.set("POWER", "main_dungeon", self.main_dungeon)
        self.config.set("POWER", "sub_dungeon", self.sub_dungeon)
        self.config.set("POWER", "main_dungeon_level", str(self.main_dungeon_level))
        self.config.set("POWER", "sub_dungeon_level", str(self.sub_dungeon_level))
        self.config.set("POWER", "deplete_power", str(self.deplete_power))
        self.config.set("POWER", "target_power", self.target_power)
        
        # 一条龙特殊设置
        self.config.set("onedragonSpcial", "is_standby", str(self.is_standby))
        self.config.set("onedragonSpcial", "mode", self.mode)
        self.config.set("onedragonSpcial", "find_second_dengeon_panel_time", str(self.find_second_dengeon_panel_time))
        self.config.set("onedragonSpcial", "joint_is_refresh", str(self.joint_is_refresh))
        self.config.set("onedragonSpcial", "joint_must_s", str(self.joint_must_s))

        # 日志设置
        self.config.set("SETTINGS", "debug_log", str(self.debug_log))
        
        # 其他任务
        self.config.set("OtherTask", "is_exhausted_com", str(self.is_exhausted_com))
        self.config.set("OtherTask", "target_com", self.target_com)

        # 任务参数设置
        self.config.set("SETTINGS", "interval_time", str(self.interval_time))
        self.config.set("SETTINGS", "ocr_use_gpu", str(self.ocr_use_gpu))
        self.config.set("SETTINGS", "ocr_collect_time", str(self.ocr_collect_time))
        self.config.set("SETTINGS", "template_resolution", self.template_resolution)

        # 写入文件
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                self.config.write(f)
        except Exception as e:
            Log(f"配置保存失败：{str(e)}", level="ERROR")

    def load_config(self):
        """加载配置文件到内存变量（不直接操作界面，避免界面未创建）"""
        try:
            self.config.read(self.config_path, encoding="utf-8")
            # 游戏路径
            self.game_path = self.config.get("PATH", "game_path", fallback="")
            # 一条龙配置
            self.is_role_interaction = self.config.getboolean("onedragon", "role_interaction", fallback=False)
            self.is_get_power = self.config.getboolean("onedragon", "get_power", fallback=False)
            self.is_clear_power = self.config.getboolean("onedragon", "clear_power", fallback=False)
            self.is_garden = self.config.getboolean("onedragon", "garden", fallback=False)
            self.is_shop_get_free_power = self.config.getboolean("onedragon", "shop_get_free_power", fallback=False)
            self.is_mimier = self.config.getboolean("onedragon", "mimier", fallback=False)
            self.is_get_daily_weekly_reward = self.config.getboolean("onedragon", "get_daily_weekly_reward", fallback=False)
            self.is_monthly_pass = self.config.getboolean("onedragon", "monthly_pass", fallback=False)
            self.is_mail = self.config.getboolean("onedragon", "mail", fallback=False)
            # 体力配置
            self.main_dungeon = self.config.get("POWER", "main_dungeon", fallback="酬金委托")
            self.sub_dungeon = self.config.get("POWER", "sub_dungeon", fallback="模拟作战")
            self.main_dungeon_level = self.config.getint("POWER", "main_dungeon_level", fallback=1)
            self.sub_dungeon_level = self.config.getint("POWER", "sub_dungeon_level", fallback=1)
            self.deplete_power = self.config.getboolean("POWER", "deplete_power", fallback=False)
            self.target_power = self.config.get("POWER", "target_power", fallback="100")
            # 一条龙特殊设置
            self.is_standby = self.config.getboolean("onedragonSpcial", "is_standby", fallback=True)
            self.joint_is_refresh = self.config.getboolean("onedragonSpcial", "joint_is_refresh", fallback=True)
            self.joint_must_s = self.config.getboolean("onedragonSpcial", "joint_must_s", fallback=True)
            self.mode = self.config.get("onedragonSpcial", "mode", fallback="扫荡")
            self.find_second_dengeon_panel_time = self.config.getint("onedragonSpcial", "find_second_dengeon_panel_time", fallback=10)
            # 日志设置
            self.debug_log = self.config.getboolean("SETTINGS", "debug_log", fallback=False)
            # 其他任务
            self.is_exhausted_com = self.config.getboolean("OtherTask", "is_exhausted_com", fallback=True)
            self.target_com = self.config.get("OtherTask", "target_com", fallback="0")
            # 任务参数设置
            self.interval_time = self.config.getint("SETTINGS", "interval_time", fallback=2)
            self.ocr_use_gpu = self.config.getboolean("SETTINGS", "ocr_use_gpu", fallback=False)
            self.ocr_collect_time = self.config.getint("SETTINGS", "ocr_collect_time", fallback=20)
            self.template_resolution = self.config.get("SETTINGS", "template_resolution", fallback="1920*1200")
            
            
        except Exception as e:
            Log(f"配置加载失败，使用默认值：{str(e)}", level="ERROR")
            # 重置为默认值
            self.game_path = ""
            # 一条龙配置
            self.is_role_interaction = False
            self.is_get_power = False
            self.is_clear_power = False
            self.is_garden = False
            self.is_shop_get_free_power = False
            self.is_mimier = False
            self.is_get_daily_weekly_reward = False
            self.is_monthly_pass = False
            self.is_mail = False
            # 体力配置
            self.main_dungeon = "酬金委托"
            self.sub_dungeon = "模拟作战"
            self.main_dungeon_level = 1
            self.sub_dungeon_level =1
            self.deplete_power = False
            self.target_power = "100"
            # 一条龙特殊设置
            self.is_standby = True
            self.joint_is_refresh = True
            self.joint_must_s = True
            self.mode = "扫荡"
            self.find_second_dengeon_panel_time = 10
            # 日志设置
            self.debug_log = False
            # 任务参数设置
            self.interval_time = 2
            self.ocr_use_gpu = False
            self.ocr_collect_time = 20
            self.template_resolution = "1920*1200"

    # ========== 界面初始化 ==========
    def _init_home_ui(self):
        """初始化首页UI"""
        layout = QVBoxLayout(self.homeInterface)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)

        # 顶部图片
        img_label = QLabel(self.homeInterface)
        try:
            pixmap = QPixmap(r'gui\\main_ui_top.png')
            pixmap = pixmap.scaled(750, 300, Qt.AspectRatioMode.KeepAspectRatio)
            img_label.setPixmap(pixmap)
        except Exception as e:
            img_label.setText("图片加载失败")
            Log(f"首页图片加载失败：{str(e)}", level="ERROR")
        layout.addWidget(img_label, alignment=Qt.AlignmentFlag.AlignCenter)

        layout.addStretch(1)

        button_layout =  QHBoxLayout()
        # 启动游戏按钮
        start_btn = PushButton("启动游戏", self.homeInterface)
        start_btn.setFixedSize(150, 50)
        start_btn.setIconSize(QSize(20, 20))
        start_btn.setIcon(FluentIcon.PLAY)
        #start_btn.setStyleSheet("qproperty-iconAlignment: AlignCenter;")
        start_btn.clicked.connect(self.start_game)
        button_layout.addWidget(start_btn)
        # 每日一条龙按钮
        start_oneDragon_btn = PushButton("每日一条龙", self.homeInterface)
        start_oneDragon_btn.setFixedSize(200, 50)
        start_oneDragon_btn.clicked.connect(self.start_oneDragon)
        button_layout.addWidget(start_oneDragon_btn)
        
        layout.addLayout(button_layout)

        # 日志设置行
        debug_layout = QHBoxLayout()
        self.debug_check = QCheckBox("开启Debug日志", self.homeInterface)
        self.debug_check.setChecked(self.debug_log)  # 从内存变量加载
        debug_layout.addWidget(self.debug_check)
        debug_layout.addStretch()
        debug_layout.addWidget(QLabel("运行日志", self.homeInterface))
        layout.addLayout(debug_layout)

        # 日志输出框
        self.log_text = QPlainTextEdit(self.homeInterface)
        self.log_text.setReadOnly(True)
        self.log_text.setFixedHeight(300)
        layout.addWidget(self.log_text)

    def _init_oneDragon_setting_ui(self):
        """初始化一条龙设置页UI（创建所有界面元素）"""
        main_layout = QVBoxLayout(self.oneDragonInterface)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # ========== 一条龙任务设置 ==========
        oneDargon_task_layout = QVBoxLayout()
        oneDargon_task_layout.setSpacing(12)

        # 标题行
        title_layout = QHBoxLayout()
        title_layout.setSpacing(15)
        task_icon = IconWidget(FluentIcon.LABEL, self.oneDragonInterface)
        task_icon.setFixedSize(24, 24)
        title_layout.addWidget(task_icon)
        title_layout.addWidget(QLabel("一条龙任务设置", self.oneDragonInterface))
        oneDargon_task_layout.addLayout(title_layout)

        oneDragon_le_ri_list = QHBoxLayout()
        oneDragon_left_list = QVBoxLayout()
        oneDragon_left_list.setSpacing(2)
        oneDragon_right_list = QVBoxLayout()
        oneDragon_right_list.setSpacing(2)
        
        # 复选框创建（从内存变量加载状态）
        self.check_role_interaction = QCheckBox("角色互动", self.oneDragonInterface)
        self.check_role_interaction.setChecked(self.is_role_interaction)

        self.check_get_power = QCheckBox("领取每日12:00和18:00的额外体力", self.oneDragonInterface)
        self.check_get_power.setChecked(self.is_get_power)

        self.check_clear_power = QCheckBox("清体力", self.oneDragonInterface)
        self.check_clear_power.setChecked(self.is_clear_power)

        self.check_garden = QCheckBox("游园街", self.oneDragonInterface)
        self.check_garden.setChecked(self.is_garden)

        self.check_shop_get_free_power = QCheckBox("领取商店免费体力", self.oneDragonInterface)
        self.check_shop_get_free_power.setChecked(self.is_shop_get_free_power)

        self.check_mimier = QCheckBox("弥弥尔观测站", self.oneDragonInterface)
        self.check_mimier.setChecked(self.is_mimier)

        self.check_get_daily_weekly_reward = QCheckBox("领取每日每周任务奖励", self.oneDragonInterface)
        self.check_get_daily_weekly_reward.setChecked(self.is_get_daily_weekly_reward)

        self.check_monthly_pass = QCheckBox("大月卡", self.oneDragonInterface)
        self.check_monthly_pass.setChecked(self.is_monthly_pass)

        self.check_mail = QCheckBox("邮件", self.oneDragonInterface)
        self.check_mail.setChecked(self.is_mail)

        # 添加复选框到布局
        for check_box in [
            self.check_role_interaction, self.check_get_power,
            self.check_clear_power, self.check_garden,
            self.check_shop_get_free_power
        ]:
            oneDragon_left_list.addWidget(check_box)
        for check_box in [
            self.check_mimier,
            self.check_get_daily_weekly_reward, self.check_monthly_pass,
            self.check_mail
        ]:
            oneDragon_right_list.addWidget(check_box)
        oneDragon_le_ri_list.addLayout(oneDragon_left_list)
        oneDragon_le_ri_list.addLayout(oneDragon_right_list)
        oneDargon_task_layout.addLayout(oneDragon_le_ri_list)

        main_layout.addLayout(oneDargon_task_layout)

        # ========== 体力分配设置 ==========
        power_layout = QVBoxLayout()
        power_layout.setSpacing(12)
        

        # 标题行
        power_title_layout = QHBoxLayout()
        power_title_layout.setSpacing(15)
        power_icon = IconWidget(FluentIcon.CHAT, self.oneDragonInterface)
        power_icon.setFixedSize(24, 24)
        power_title_layout.addWidget(power_icon)
        power_title_layout.addWidget(QLabel("体力分配设置", self.oneDragonInterface))
        power_layout.addLayout(power_title_layout)


        # 副本列表区域
        main_sub_dungeon_layout = QHBoxLayout()
        
        # 副本列表数据
        dungeon_list = [
            "酬金委托", "模拟作战", "因子采集", "深层勘探", "极限萃取",
            "失落遗迹", "战场清扫", "联合特勤", "神域解析", '联防协议'
        ]

        # 主副本选择
        main_dungeon_layout = QHBoxLayout()
        main_label = QLabel("主副本：", self.oneDragonInterface)
        main_label.setFixedWidth(60)
        self.main_dungeon_list = QListWidget(self.oneDragonInterface)
        self.main_dungeon_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.main_dungeon_list.addItems(dungeon_list)
        self.main_dungeon_list.setFixedHeight(100)
        # 选中配置中的主副本
        main_items = self.main_dungeon_list.findItems(self.main_dungeon, Qt.MatchFlag.MatchExactly)
        if main_items:
            self.main_dungeon_list.setCurrentItem(main_items[0])
        main_dungeon_layout.addWidget(main_label)
        main_dungeon_layout.addWidget(self.main_dungeon_list)
        main_sub_dungeon_layout.addLayout(main_dungeon_layout)

        # 备用副本选择
        sub_dungeon_layout = QHBoxLayout()
        sub_label = QLabel("备用副本：", self.oneDragonInterface)
        sub_label.setFixedWidth(60)
        self.sub_dungeon_list = QListWidget(self.oneDragonInterface)
        self.sub_dungeon_list.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.sub_dungeon_list.addItems(dungeon_list)
        self.sub_dungeon_list.setFixedHeight(100)
        # 选中配置中的备用副本
        sub_items = self.sub_dungeon_list.findItems(self.sub_dungeon, Qt.MatchFlag.MatchExactly)
        if sub_items:
            self.sub_dungeon_list.setCurrentItem(sub_items[0])
        sub_dungeon_layout.addWidget(sub_label)
        sub_dungeon_layout.addWidget(self.sub_dungeon_list)
        main_sub_dungeon_layout.addLayout(sub_dungeon_layout)
        
        power_layout.addLayout(main_sub_dungeon_layout)
        
        # 副本等级选择
        main_sub_dungeon_level_layout = QHBoxLayout()
        
        main_level_layout = QHBoxLayout()
        main_level_label = QLabel("主副本等级：", self.oneDragonInterface)
        #main_level_label.setFixedWidth(60)
        self.main_dengeon_level_spin = QSpinBox(self.oneDragonInterface)
        self.main_dengeon_level_spin.setRange(1, self.main_dungeon_level)
        self.main_dengeon_level_spin.setValue(self.main_dungeon_level)
        self.main_dengeon_level_spin.setFixedWidth(100)
        main_level_layout.addWidget(main_level_label)
        main_level_layout.addWidget(self.main_dengeon_level_spin)
        main_sub_dungeon_level_layout.addLayout(main_level_layout)
        
        sub_level_layout = QHBoxLayout()
        sub_level_label = QLabel("备用副本等级：", self.oneDragonInterface)
        #sub_level_label.setFixedWidth(60)
        self.sub_dengeon_level_spin = QSpinBox(self.oneDragonInterface)
        self.sub_dengeon_level_spin.setRange(1, self.sub_dungeon_level)
        self.sub_dengeon_level_spin.setValue(self.sub_dungeon_level)
        self.sub_dengeon_level_spin.setFixedWidth(100)
        sub_level_layout.addWidget(sub_level_label)
        sub_level_layout.addWidget(self.sub_dengeon_level_spin)
        main_sub_dungeon_level_layout.addLayout(sub_level_layout)
        
        power_layout.addLayout(main_sub_dungeon_level_layout)
        

        # 耗尽体力复选框
        self.check_deplete_power = QCheckBox("耗尽当前体力", self.oneDragonInterface)
        self.check_deplete_power.setChecked(self.deplete_power)
        power_layout.addWidget(self.check_deplete_power)

        # 目标体力输入框
        target_layout = QHBoxLayout()
        target_label = QLabel("目标体力：", self.oneDragonInterface)
        target_label.setFixedWidth(60)
        self.target_power_input = QLineEdit(self.oneDragonInterface)
        self.target_power_input.setPlaceholderText("请输入数字")
        self.target_power_input.setText(self.target_power)  # 从内存变量加载
        # 只允许输入数字
        self.target_power_input.textChanged.connect(
            lambda: self.target_power_input.setText(''.join(filter(str.isdigit, self.target_power_input.text())))
        )
        target_layout.addWidget(target_label)
        target_layout.addWidget(self.target_power_input)
        power_layout.addLayout(target_layout)

        # 初始化目标体力输入框状态
        self.toggle_power_input(self.deplete_power)

        main_layout.addLayout(power_layout)
        
        
        
        # ========== 一条龙特殊设置 ==========
        special_setting_layout = QVBoxLayout()
        special_setting_layout.setSpacing(15)
        
        special_setting_title_layout = QHBoxLayout()
        special_setting_icon = IconWidget(FluentIcon.SAVE_COPY, self.oneDragonInterface)
        special_setting_icon.setFixedSize(24, 24)
        special_setting_title_layout.addWidget(special_setting_icon)
        special_setting_title_layout.addWidget(QLabel("特殊设置", self.oneDragonInterface))
        special_setting_layout.addLayout(special_setting_title_layout)
        
        # 是否启用备用副本开关
        is_standby_layout = QHBoxLayout()
        self.is_standby_switch = SwitchButton(self.oneDragonInterface)
        self.is_standby_switch.setChecked(self.is_standby)
        self.is_standby_switch.setFixedWidth(100)
        is_standby_layout.addWidget(QLabel("是否启用备用副本(仅主副本为联合特勤时生效)", self.oneDragonInterface))
        is_standby_layout.addStretch(1)
        is_standby_layout.addWidget(self.is_standby_switch)
        special_setting_layout.addLayout(is_standby_layout)
        
        # 联合特勤参数，如果没有s副本是否尝试刷新，是否一定要s级副本
        joint_is_refresh_layout = QHBoxLayout()
        self.joint_is_refresh_switch = SwitchButton(self.oneDragonInterface)
        self.joint_is_refresh_switch.setChecked(self.joint_is_refresh)
        self.joint_is_refresh_switch.setFixedWidth(100)
        joint_is_refresh_layout.addWidget(QLabel("当联合特勤没有s副本是否尝试使用免费刷新次数刷新", self.oneDragonInterface))
        joint_is_refresh_layout.addStretch(1)
        joint_is_refresh_layout.addWidget(self.joint_is_refresh_switch)
        special_setting_layout.addLayout(joint_is_refresh_layout)
        
        joint_must_s_layout = QHBoxLayout()
        self.joint_must_s_switch = SwitchButton(self.oneDragonInterface)
        self.joint_must_s_switch.setChecked(self.joint_must_s)
        self.joint_must_s_switch.setFixedWidth(100)
        joint_must_s_layout.addWidget(QLabel("联合特勤是否一定要s级副本(当没有s副本且打开启用备用副本的开关时，则自动转为备用方案)", self.oneDragonInterface))
        joint_must_s_layout.addStretch(1)
        joint_must_s_layout.addWidget(self.joint_must_s_switch)
        special_setting_layout.addLayout(joint_must_s_layout)
        
        # 副本刷取模式
        mode_layout = QHBoxLayout()
        self.mode_ComboBox = ComboBox(self.oneDragonInterface)
        self.mode_ComboBox.addItems(["扫荡"])
        self.mode_ComboBox.setCurrentText(self.mode)
        self.mode_ComboBox.setFixedWidth(100)
        mode_layout.addWidget(QLabel("副本战斗模式", self.oneDragonInterface))
        mode_layout.addStretch(1)
        mode_layout.addWidget(self.mode_ComboBox)
        special_setting_layout.addLayout(mode_layout)
        
        # 副本二级界面最大寻找次数
        find_second_dengeon_panel_time_layout = QHBoxLayout()
        find_second_dengeon_panel_time_layout.addWidget(QLabel("副本二级界面最大寻找次数(一般不用管)", self.oneDragonInterface))
        find_second_dengeon_panel_time_layout.addStretch(1)
        self.find_second_dengeon_panel_time_QSpinBox = QSpinBox(self.oneDragonInterface)
        self.find_second_dengeon_panel_time_QSpinBox.setRange(10, 20)
        self.find_second_dengeon_panel_time_QSpinBox.setValue(self.find_second_dengeon_panel_time)
        self.find_second_dengeon_panel_time_QSpinBox.setSuffix(" 次")
        self.find_second_dengeon_panel_time_QSpinBox.setFixedWidth(100)
        find_second_dengeon_panel_time_layout.addWidget(self.find_second_dengeon_panel_time_QSpinBox)
        special_setting_layout.addLayout(find_second_dengeon_panel_time_layout)
        
        
        
        
        main_layout.addLayout(special_setting_layout)
        
        
        main_layout.addStretch(1)
        


    def _init_other_task_ui(self):
        '''初始化其他任务页UI'''
        main_layout = QVBoxLayout(self.otherTaskInterface)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        # ========== 联防协议——失序援区 ==========
        communication_layout = QVBoxLayout()
        communication_title_layout = QHBoxLayout()
        communication_icon = IconWidget(FluentIcon.ERASE_TOOL, self.otherTaskInterface)
        communication_icon.setFixedSize(24, 24)
        communication_title_layout.addWidget(communication_icon)
        communication_title_layout.addWidget(QLabel("联防协议——失序援区", self.otherTaskInterface))
        # 加入启动按钮
        communication_title_layout.addStretch(1)
        self.communication_PushButton = PushButton("启动任务", self.otherTaskInterface)
        self.communication_PushButton.clicked.connect(self.start_other_task_communication)
        self.communication_PushButton.clicked.connect(lambda: self.stackedWidget.setCurrentIndex(0))
        communication_title_layout.addWidget(self.communication_PushButton)
        communication_layout.addLayout(communication_title_layout)
        
        # 是否耗尽所有的求援通讯数
        is_exhausted_com_layout = QHBoxLayout()
        is_exhausted_com_layout.addWidget(QLabel("是否耗尽所有的求援通讯数", self.otherTaskInterface))
        is_exhausted_com_layout.addStretch(1)
        self.is_exhausted_com_switch = SwitchButton(self.otherTaskInterface)
        self.is_exhausted_com_switch.setChecked(self.is_exhausted_com)
        is_exhausted_com_layout.addWidget(self.is_exhausted_com_switch)
        
        communication_layout.addLayout(is_exhausted_com_layout)
        
        
        # 选择目标消耗的求援通讯数
        target_com_layout = QHBoxLayout()
        target_com_label = QLabel("目标消耗的求援通讯：", self.otherTaskInterface)
        self.target_com_input = QLineEdit(self.otherTaskInterface)
        self.target_com_input.setPlaceholderText("请输入数字")
        self.target_com_input.setText(self.target_com)  
        # 只允许输入数字
        self.target_com_input.textChanged.connect(
            lambda: self.target_com_input.setText(''.join(filter(str.isdigit, self.target_com_input.text())))
        )
        target_com_layout.addWidget(target_com_label)
        target_com_layout.addWidget(self.target_com_input)
        communication_layout.addLayout(target_com_layout)
        
        # 更新
        self.toggle_com_input(self.is_exhausted_com_switch.isChecked())
        
        main_layout.addLayout(communication_layout)

    def _init_settings_ui(self):
        """初始化设置页UI（创建所有界面元素）"""
        main_layout = QVBoxLayout(self.setInterface)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ========== 游戏路径设置 ==========
        layout_path = QHBoxLayout()
        layout_path.setSpacing(15)

        icon = IconWidget(FluentIcon.GAME, self.setInterface)
        icon.setFixedSize(24, 24)
        layout_path.addWidget(icon)

        path_label = QLabel("游戏路径", self.setInterface)
        layout_path.addWidget(path_label)

        self.path_input = QLineEdit(self.setInterface)
        self.path_input.setPlaceholderText("请选择游戏路径")
        self.path_input.setReadOnly(True)
        self.path_input.setText(self.game_path)  # 从内存变量加载
        layout_path.addWidget(self.path_input, stretch=1)

        modify_btn = PushButton("修改", self.setInterface)
        modify_btn.setFixedSize(80, 30)
        modify_btn.clicked.connect(self.select_game_path)
        layout_path.addWidget(modify_btn)
        main_layout.addLayout(layout_path)
        
        # ========== 任务参数设置 ==========
        task_parameter_layout = QVBoxLayout()
        task_parameter_layout.setSpacing(30)
        
        task_parameter_title_layout = QHBoxLayout()
        task_parameter_icon = IconWidget(FluentIcon.ADD_TO, self.setInterface)
        task_parameter_icon.setFixedSize(24, 24)
        task_parameter_title_layout.addWidget(task_parameter_icon)
        task_parameter_title_layout.addWidget(QLabel("任务参数设置", self.setInterface))
        task_parameter_layout.addLayout(task_parameter_title_layout)
        # 操作间隔时间
        interval_time_layout = QHBoxLayout()
        interval_time_label = QLabel("操作间隔时间\n解释：该参数调整的是操作与操作间的间隔，如果发现游戏的页面加载时间较长，可以尝试增加该值", self.setInterface)
        interval_time_layout.addWidget(interval_time_label)
        interval_time_layout.addStretch(1)
        
        self.interval_time_layout_QSpinBox = QSpinBox(self.setInterface)
        self.interval_time_layout_QSpinBox.setRange(1, 5)
        self.interval_time_layout_QSpinBox.setValue(self.interval_time)
        self.interval_time_layout_QSpinBox.setSuffix(" s")
        interval_time_layout.addWidget(self.interval_time_layout_QSpinBox)
        
        task_parameter_layout.addLayout(interval_time_layout)
        
        # ocr模型是否启用GPU加速
        ocr_use_gpu_layout = QHBoxLayout()
        
        ocr_use_gpu_layout.addWidget(QLabel("OCR启用GPU"))
        ocr_use_gpu_layout.addStretch(1)
        self.ocr_use_gpu_switch = SwitchButton(self.setInterface)
        self.ocr_use_gpu_switch.setChecked(self.ocr_use_gpu)
        ocr_use_gpu_layout.addWidget(self.ocr_use_gpu_switch)
        
        task_parameter_layout.addLayout(ocr_use_gpu_layout)
        
        # ocr模型内存清理间隔
        
        ocr_collect_time_layout = QHBoxLayout()
        
        ocr_collect_time_layout.addWidget(QLabel("OCR模型内存清理间隔(调用n次模型时清理一次)"))
        ocr_collect_time_layout.addStretch(1)
        self.ocr_collect_time_QSpinBox = QSpinBox(self.setInterface)
        self.ocr_collect_time_QSpinBox.setRange(10, 50)
        self.ocr_collect_time_QSpinBox.setSuffix(" 次")
        self.ocr_collect_time_QSpinBox.setValue(self.ocr_collect_time)
        ocr_collect_time_layout.addWidget(self.ocr_collect_time_QSpinBox)
        
        task_parameter_layout.addLayout(ocr_collect_time_layout)
        
        # 游戏分辨率
        template_resolution_layout = QHBoxLayout()
        
        template_resolution_layout.addWidget(QLabel("游戏分辨率"))
        template_resolution_layout.addStretch(1)
        self.template_resolution_ComboBox = ComboBox(self.setInterface)
        self.template_resolution_ComboBox.addItems(["1920*1200"])
        self.template_resolution_ComboBox.setCurrentText(self.template_resolution)
        template_resolution_layout.addWidget(self.template_resolution_ComboBox)
        
        task_parameter_layout.addLayout(template_resolution_layout)
        
        
        main_layout.addLayout(task_parameter_layout)
        

        

    def _bind_signals(self):
        """统一绑定所有信号（最后执行，避免初始化时触发save_config）"""
        # 首页信号
        self.debug_check.stateChanged.connect(self.save_config)

        # 设置页-一条龙任务复选框
        self.check_role_interaction.stateChanged.connect(self.save_config)
        self.check_get_power.stateChanged.connect(self.save_config)
        self.check_clear_power.stateChanged.connect(self.save_config)
        self.check_garden.stateChanged.connect(self.save_config)
        self.check_shop_get_free_power.stateChanged.connect(self.save_config)
        self.check_mimier.stateChanged.connect(self.save_config)
        self.check_get_daily_weekly_reward.stateChanged.connect(self.save_config)
        self.check_monthly_pass.stateChanged.connect(self.save_config)
        self.check_mail.stateChanged.connect(self.save_config)

        # 设置页-体力分配
        self.main_dungeon_list.itemSelectionChanged.connect(self.save_config)
        self.sub_dungeon_list.itemSelectionChanged.connect(self.save_config)
        self.main_dungeon_list.currentItemChanged.connect(self.update_main_dungeon_level)
        self.sub_dungeon_list.currentItemChanged.connect(self.update_sub_dungeon_level)
        self.main_dengeon_level_spin.valueChanged.connect(lambda v: setattr(self, 'main_dungeon_level', v))
        self.sub_dengeon_level_spin.valueChanged.connect(lambda v: setattr(self, 'sub_dungeon_level', v))
        self.main_dengeon_level_spin.valueChanged.connect(self.save_config)
        self.main_dengeon_level_spin.valueChanged.connect(self.save_config)
        self.check_deplete_power.stateChanged.connect(self.save_config)
        self.check_deplete_power.stateChanged.connect(self.toggle_power_input)
        self.target_power_input.textChanged.connect(self.save_config)
        # 一条龙特殊设置
        self.is_standby_switch.checkedChanged.connect(self.save_config)
        self.joint_is_refresh_switch.checkedChanged.connect(self.save_config)
        self.joint_must_s_switch.checkedChanged.connect(self.save_config)
        self.mode_ComboBox.currentTextChanged.connect(self.save_config)
        self.find_second_dengeon_panel_time_QSpinBox.valueChanged.connect(self.save_config)
        # 其他任务
        self.is_exhausted_com_switch.checkedChanged.connect(self.save_config)
        self.is_exhausted_com_switch.checkedChanged.connect(self.toggle_com_input)
        self.target_com_input.textChanged.connect(self.save_config)
        # 任务参数设置
        self.interval_time_layout_QSpinBox.valueChanged.connect(self.save_config)
        self.ocr_use_gpu_switch.checkedChanged.connect(self.save_config)
        self.ocr_collect_time_QSpinBox.valueChanged.connect(self.save_config)
        self.template_resolution_ComboBox.currentTextChanged.connect(self.save_config)

    # ========== 业务方法 ==========
    def select_game_path(self):
        """选择游戏路径"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择游戏路径", "", "可执行文件(*.exe)")
        if file_path:
            self.path_input.setText(file_path)
            self.game_path = file_path
            self.save_config()
            Log(f"游戏路径已设置：{file_path}")

    def toggle_power_input(self, state):
        """切换目标体力输入框启用状态"""
        # 统一将状态转为布尔值：勾选=True，未勾选=False
        if isinstance(state, bool):
            is_checked = state
        elif isinstance(state, int):
            is_checked = state == Qt.CheckState.Checked.value
        elif isinstance(state, Qt.CheckState):
            is_checked = state == Qt.CheckState.Checked
        else:
            is_checked = False

        self.target_power_input.setEnabled(not is_checked)
        
    def toggle_com_input(self, state):
        """切换求援通讯输入框启用状态"""
        # 统一将状态转为布尔值：勾选=True，未勾选=False
        if isinstance(state, bool):
            is_checked = state
        elif isinstance(state, int):
            is_checked = state == Qt.CheckState.Checked.value
        elif isinstance(state, Qt.CheckState):
            is_checked = state == Qt.CheckState.Checked
        else:
            is_checked = False

        self.target_com_input.setEnabled(not is_checked)
        
    def update_main_dungeon_level(self, current_item):
        """更新主副本等级控件的值"""
        dungeon_name = current_item.text()
        max_level = self.dungeon_max_level.get(dungeon_name, 1)
        self.main_dengeon_level_spin.setRange(1, max_level)
        # 如果更改时当前值超范围了，就取该范围的最大值
        if self.main_dengeon_level_spin.value() > max_level:
            self.main_dengeon_level_spin.setValue(max_level)
        self.main_dungeon_level = self.main_dengeon_level_spin.value()
        
    def update_sub_dungeon_level(self, current_item):
        """更新备用副本等级控件的值"""
        dungeon_name = current_item.text()
        max_level = self.dungeon_max_level.get(dungeon_name, 1)
        self.sub_dengeon_level_spin.setRange(1, max_level)
        # 如果更改时当前值超范围了，就取该范围的最大值
        if self.sub_dengeon_level_spin.value() > max_level:
            self.sub_dengeon_level_spin.setValue(max_level)
        self.sub_dungeon_level = self.sub_dengeon_level_spin.value()

    def append_log(self, content, level="INFO"):
        """添加日志到日志框（容错：日志框未创建时不报错）"""
        if hasattr(self, 'log_text'):
            if self.debug_log or level != 'DEBUG':
                self.log_text.appendPlainText(content)
                cursor = self.log_text.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.End)
                self.log_text.setTextCursor(cursor)
                
    def show_error_dialog(self, error_msg):
        QMessageBox.critical(
            self,
            "致命错误",
            f"{error_msg}"
        )

    # 启动进程
    def start_game(self):
        import window
        winSt = window.Start(
            title="AetherGazer",
            game_path=self.game_path,
            process_name="AetherGazer.exe",
        )
    
        if winSt.auto_launch_game():
            Log("启动成功")
        else:
            Log("启动失败")

    # 启用一条龙
    def start_oneDragon(self):
        self.save_config()
        
        # 创建并启动线程
        if not hasattr(self, 'task_thread') or not self.task_thread.isRunning():
            self.task_thread = TaskThread(self, "oneDragon")
            self.task_thread.start() # 拉起新的进程，调用run()
        else:
            Log("任务正在运行中，请勿重复点击！", level="ERROR")
            
    # 启动 联防协议——始序援区
    def start_other_task_communication(self):
        self.save_config()
        
        # 创建并启动线程
        if not hasattr(self, 'task_thread') or not self.task_thread.isRunning():
            self.task_thread = TaskThread(self, "communication")
            self.task_thread.start() # 拉起新的进程，调用run()
        else:
            Log("任务正在运行中，请勿重复点击！", level="ERROR")
        


# 线程类
class TaskThread(QThread):
    """专门跑 task 的线程"""
    # 异常捕获
    error_singal = pyqtSignal(str, str)
    
    def __init__(self, main_window, select_task):
        super().__init__()
        self.main_window = main_window  # 保存 MainWindow 的引用
        self.select_task = select_task
        
        # 连接异常信号到日志窗口
        self.error_singal.connect(Log)
        self.error_singal.connect(lambda error_msg, _: self.main_window.show_error_dialog(error_msg))
        
        from task import Task
        mode_translate = {
            "扫荡": "mopup"
        }
        self.t = Task(
            title="AetherGazer",
            game_path=self.main_window.game_path,
            process_name="AetherGazer.exe",
            target=self.main_window.main_dungeon,
            number=self.main_window.main_dungeon_level,
            find_time=self.main_window.find_second_dengeon_panel_time,
            mode=mode_translate.get(self.main_window.mode, "mopup"),
            consume_power=int(self.main_window.target_power),
            is_exhausted=self.main_window.deplete_power,
            is_standby=self.main_window.is_standby,
            standby_target=self.main_window.sub_dungeon,
            standby_target_number=self.main_window.main_dungeon_level,
            joint_is_refresh=self.main_window.joint_is_refresh,
            joint_must_s=self.main_window.joint_must_s,
            interval_time=self.main_window.interval_time,
            ocr_use_gpu=self.main_window.ocr_use_gpu,
            ocr_collect_time=self.main_window.ocr_collect_time,
            template_resolution=self.main_window.template_resolution
        )
        
        self.t.taskdic = {
            "登录界面": True,
            "每日活跃度": True,
        }
        self.t.act_dic = {
            "角色互动": self.main_window.is_role_interaction,
            "尝试领取额外体力": self.main_window.is_get_power,
            "进入指定副本并消耗体力": self.main_window.is_clear_power,
            "游园街": self.main_window.is_garden,
            "商店免费体力": self.main_window.is_shop_get_free_power,
            "弥弥尔": self.main_window.is_mimier,
            "领取每日每周任务奖励": self.main_window.is_get_daily_weekly_reward,
            "大月卡": self.main_window.is_monthly_pass,
            "邮件": self.main_window.is_mail
        }

    def run(self):
        """线程执行的入口"""
        try:
            if self.select_task == "oneDragon":
                self.main_window.start_game()
                self.oneDragon()
            elif self.select_task == 'communication':
                import time
                self.main_window.start_game()
                time.sleep(self.t.interval_time)
                self.t.login()
                time.sleep(self.t.interval_time)
                self.t.re_main_ui()
                self.communication()
        except Exception as e:
            error_msg = f"【子线程异常】{self.select_task} 任务失败：\n{traceback.format_exc()}"
            self.error_singal.emit(error_msg, 'CRITICAL')

        
    def oneDragon(self):
        from log import Log
        Log("==============每日一条龙启动==============")
  
        self.t.all_task()
        
        Log("==============每日一条龙执行完毕==============")
        
    def communication(self):
        from log import Log
        Log("==============联防协议启动==============")
        t_com = self.main_window.target_com
        if self.main_window.is_exhausted_com == True:
            t_com = -1
        self.t.joint_defense_disorder(consume_communication=int(t_com))
        
        Log("==============联防协议执行完毕==============")

