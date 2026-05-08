from rapidocr_onnxruntime import RapidOCR
import log
import cv2
import gc


class GameOCR():
    def __init__(self, use_gpu=False, collect_time=20):
        self.ocr = None
        self.use_gpu = use_gpu
        self.collect_time = collect_time # 识别collect_time次，执行一次回收
        self.collect_time_now = 0 # 目前识别次数
        

    #初始化
    def init_ocr(self):
        if self.ocr is None:
            log.Log("正在初始化 RapidOCR", level='DEBUG')
            try:
                self.ocr = RapidOCR(
                    use_angle_cls=False,  # 关闭方向分类，游戏文字都是正的
                    use_gpu=self.use_gpu,      # 自动 GPU 加速（需要 onnxruntime-gpu）
                    show_log=False,       # 关闭详细日志
                    det_thresh=0.3,       # 检测阈值，调低避免漏检
                    det_box_thresh=0.5,   # 检测框阈值
                )
            except Exception as e:
                mode = "GPU" if self.use_gpu else "CPU"
                log.Log(f"RapidOCR 初始化失败：{e}，模式：{mode}", level='WARNING')
                if self.use_gpu:
                    log.Log(f"目前为GPU模式，尝试降级为CPU模式", level='WARNING')
                    self.use_gpu = False
                    self.init_ocr()
                else:
                    log.Log(f"RapidOCR 初始化失败", level='ERROR')
                    return False
        return True

    # 释放资源
    def release_ocr(self):
        if self.collect_time <= self.collect_time_now:
            if self.ocr is not None:
                try:
                    gc.collect()
                    log.Log(f"RapidOCR 资源已释放", level='DEBUG')
                    self.collect_time_now = 0

                except Exception as e:
                    log.Log(f"RapidOCR 资源释放失败", level='DEBUG')

    # 识别
    def recognize(self, img, pos=None):
        if not self.init_ocr():
            return []

        img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR)
        # 裁剪
        offset_x, offset_y = 0, 0
        if pos is not None:
            if len(pos) != 4:
                log.Log(f"目前为裁剪模式，未传入/传入参数数量有误！", level='DEBUG')
                return []
            else:
                img_h, img_w = img.shape[:2]
                x1, y1, x2, y2 = pos
                
                # 边界修正
                x1, x2 = max(0, x1), min(x2, img_w)
                y1, y2 = max(0, y1), min(y2, img_h)
                if x1 >= x2 or y1 >= y2:
                    log.Log(f"pos应为[左上角，右下角]，且x1<x2、y1<y2！", level='DEBUG')
                    return []
                
                img = img[y1:y2, x1:x2]
                offset_x, offset_y = x1, y1

        res, elapse = self.ocr(img) # elapse：耗时

        if not res:
            return []
        
        # 格式化结果
        format_res = []
        for box, text, score in res:
            x_coords = [p[0] for p in box] # 四个点的x值
            y_coords = [p[1] for p in box] # 四个点的y值
            x1, x2 = min(x_coords), max(x_coords)
            y1, y2 = min(y_coords), max(y_coords)

            # 加上偏移
            x1 += offset_x
            x2 += offset_x
            y1 += offset_y
            y2 += offset_y
        
            format_res.append([[int(x1), int(y1), int(x2), int(y2)], text, score])

        # 资源释放
        self.collect_time_now += 1
        self.release_ocr()

        return format_res

    # 找指定文字，并返回该文字中心点坐标
    def find_text(self, img, target_text, pos=None, threshold=0.7):
        res = self.recognize(img, pos)
        
        for box, t, score in res:
            if target_text in t and score >= threshold:
                x1, y1, x2, y2 = box
                center_x = (x1 + x2) // 2
                center_y = (y1 + y2) // 2
                log.Log(f"识别到{t} 中 含有 {target_text}", level='DEBUG')
                return center_x, center_y
            
            log.Log(f"识别到{t} 中 未含有 {target_text}", level='DEBUG')
            
        
        return None












    





