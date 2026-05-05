# project

## main.py

这是整个程序的主入口

## window.py

该文件用来启动指定进程，获取窗口坐标等

### start类

负责启动/检查游戏进程

### WindowRect类

用于获取窗口坐标，相对坐标转绝对坐标

## Automatic.py

用于实现自动化的一些工具

### Automatic类

用于实现自动化的一些工具

- get_game_screenshot() -> (NDArray[Any] | None)

  **获取游戏内截图，成功返回图像，失败返回None**

- best_template(template_path, isCut=False, pos=None, threshold=0.8) -> (tuple[Any, Any] | None)

  **最佳模板匹配，匹配成功返回目标处中心坐标，否则返回None**

  - template_path 匹配模板的路径
  - isCut 是否裁切窗口图片
  - pos 裁切的区域，左上角和右下角坐标
  - threshold 匹配的最低置信度

- auto_click(template_path, px, py, flag=True, isCut=False, pos=None, threshold=0.8) -> bool

  **自动点击,flag=True进行模板匹配(px,py)为偏移量，否则直接点击目标点(px,py)，操作成功返回True，否则返回False**
  - 其余与best_template()参数相同

- auto_keyboard(key) -> None

  **键盘操作**
  - key为键盘按键对应的代号

- auto_wheel(cnt, distance, px, py) -> bool

  **滚轮操作，操作成功返回True，否则返回False**
  - cnt 滚动次数
  - distance 上滑/下滑
  - px, py 移动到对应位置（窗口相对位置）

- auto_move_mouse(px, py) -> bool

  **移动鼠标到指定位置，移动成功返回True，否则返回False**
  - px, py 移动到对应位置（窗口相对位置）

## ocr.py

用于文字识别

### GameOCR类

用于文字识别

- init_ocr() -> bool

  **初始化ocr模型，初始化失败返回False，否则返回True**

- release_ocr() -> None

  **释放ocr模型资源**

- recognize(img, pos=None) -> list

  **识别文字，返回list，list中的每个元素包含 【（左上角坐标，右下角坐标），识别出的文字，置信度】，失败返回空list**

  - img 待识别图像
  - pos None 非选区模式 传入（左上角坐标，右下角坐标），自动识别该矩形区域

- find_text(img, target_text, pos=None, threshold=0.7) -> (tuple | None)

  **找指定文字，并返回该文字中心点坐标，失败返回None**

  - img 待识别图像
  - target_text 目标文本
  - pos， None 非选区模式， 传入（左上角坐标，右下角坐标），自动识别该矩形区域
  - threshold 识别最低置信度，低于这个置信度的结果不予使用

## task.py

用来执行各类游戏内操作/任务

### Task类

用来执行各类游戏内操作/任务

- get_current_ui() -> str|None
  
  **当前界面判断, 返回页面标签，如未匹配到任何界面，返回None**

- istargetui(key) -> bool
  
  **判断目前是否是目标图片**

- all_task() -> bool

  **执行taskdic中设定的任务，设定任务全部执行，返回True，否则False**

- re_main_ui(trycnt=10) -> bool
  
  **返回主界面，成功回到主界面返回True，否则返回False**

  - trycnt:最大尝试返回次数

- choose_task(key) -> bool
  
  **选择具体的小任务，成功执行对应任务返回True， 否则返回False**

  - key 任务名称

- login() -> bool
  
  **登录界面处理，执行成功返回True，否则返回False**

- daily() -> bool
  
  **每日例行任务，执行act_dic中的任务，执行成功返回True，否则返回False**

- role_interaction() -> bool

  **每日任务分支-角色互动，点击角色进行互动，点击成功返回True，点击失败返回False （目前是直接点击窗口中心）**

- get_power() -> bool
  
  **每日任务分支-领取12点和18点的体力，成功返回True，失败返回False**

- clear_power(target, number, find_time=10, mode='mopup', consume_power=-1,is_exhausted=False, is_standby = True, standby_target='酬金委托', standby_target_number=5, joint_is_refresh=True, joint_must_s=True, use_class_parameter=True) -> bool

  **清体力, 成功返回True，失败返回False**

  - target 目标副本名
  - number 第几个难度的副本
  - find_time 最多查找次数，非必要无需修改
  - mode 清理副本使用 扫荡/战斗
  - consume_power 目标消耗体力，-1为直接点击最大按键
  - is_exhausted 是否将目前体力耗尽
  - is_standby 若联合特勤刷取失败，是否启用备用方案，
  - standby_target 备用方案的目标副本
  - standby_target_number 备用方案副本等级
  - joint_is_refresh，joint_must_s 联合特勤的相关参数，是否尝试刷新，是否必须为s级

- second_common_op(target='承托', number=1) -> bool

  **普通副本二级菜单对应内部操作，如酬金委托二级菜单，成功返回True，失败返回False**

  - target 普通副本二级菜单的名称
  - number 普通副本的难度
  - 总和名称形式应为 {target}-{number}
  
- get_curpower_minpower(is_reset=False) -> (tuple[int, int] | None)
  
  **在“通用体力界面”获取当前体力以及副本最小刷取体力 ，成功返回【current_power, min_power】，否怎返回None**

  - is_reset 是否在识别前重置副本刷取倍数
  
- common_power_panel(mode='mopup', consume_power=-1, is_exhausted=False, is_pd=True, is_joint_defense=False) -> bool
  
  **通用体力界面处理，开始刷取，成功返回True，失败返回False**

  - mode=mopup 为扫荡模式(默认),fight 为战斗模式
  - consume_power=-1 消耗目前全部体力 输入任意非负数为目标体力, 最终刷取所消耗体力会尽量向下靠近目标
  - is_exhausted 是否耗尽体力
  - is_pd 联合特勤专属参数，关闭时在体力刷取完毕后直接返回True，不做循环判断，此时consume_power，is_exhausted全部失效
  - is_joint_defense 联防协议参数，打开会将get_curpower_minpower()换成joint_defense_disorder_consume_panel_rec_curmincom()
  
- joint_second_panel(is_refresh=True, must_s=True, try_cnt=3) -> bool
  
  **联合特勤的相关处理，刷取优先级为优先级为S,A,B，成功返回True，失败返回False**

  - is_refresh 是否允许使用免费的刷新
  - must_s 必须要s才刷
  - try_cnt 最大尝试刷新的次数
  
- garden(try_find_s=True) -> bool
  
  **游园街，(之后新增每周跳舞，主要任务：派遣任务，喂饭)，成功返回True，失败返回False**

  - is_must_s 委托任务中如果不是S任务，则尝试刷新

- garden_entrustment_panel_findS() -> bool
  
  **刷新游园街非s级任务，成功返回True，失败返回False**

- shop_get_free_power() -> bool
  
  **商店免费体力获取，成功返回True，失败返回False**

- mimier(get_stack_time=6) -> bool

  **弥弥观测站，成功返回True，失败返回False**

  - get_stack_time 获取堆栈递归的时间Monday == 0 ... Sunday == 6

- get_daily_weekly_reward() -> bool
  
  **领取每日&每周奖励，成功返回True，失败返回False**

- joint_defense_disorder(mode='mopup',consume_communication=-1) -> bool

  **联防协议 失序关, 成功返回True，失败返回False**

  - mode 刷取模式，扫荡还是战斗
  - consume_communication 要消耗的求援通讯数，-1为消耗所有，其余非负数为目标消耗值

- joint_defense_disorder_consume_panel_rec_curmincom(is_reset=False) -> (tuple[int, int] | None)

  **联防协议 消耗面板 当前和最小求援通讯识别，识别成功返回【current_com, min_com】，识别失败返回None**
  
  - is_reset 在识别前是否重置关卡倍数
