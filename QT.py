# pip install PyQt5
import sys
import cv2
import numpy as np
from paddleocr import PaddleOCR
import re
import os
import csv
from datetime import datetime
import shutil
import xattr
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QFileDialog, QCheckBox, QTextEdit, QLabel
from PyQt5.QtCore import QThread, pyqtSignal


class OCR_GET_VFXNO():
    def __init__(self):
        self.ocr = PaddleOCR(use_angle_cls=True, lang='en')

    def is_valid_format(self, text):
        pattern = r'^([A-Z]\d{3})[ _]?([A-Z]\d{3})$'
        match = re.match(pattern, text)
        if match:
            # 如果匹配成功，確保使用下劃線分隔
            return f"{match.group(1)}_{match.group(2)}"
        return None

    def extract_valid_text(self, result):
        for item in result:
            if isinstance(item, list):
                for subitem in item:
                    if isinstance(subitem, list) and len(subitem) == 2:
                        if isinstance(subitem[1], tuple) and len(subitem[1]) == 2:
                            text, confidence = subitem[1]
                            if isinstance(text, str):
                                valid_text = self.is_valid_format(text)
                                if valid_text:
                                    return valid_text, confidence
        return None, None

    def process_mov(self, file_path):
        ocr = PaddleOCR(use_angle_cls=True, lang='en')
        video = cv2.VideoCapture(file_path)

        # 讀取第一幀
        ret, frame = video.read()
        if not ret:
            print("無法讀取視頻")
            exit()

        total_frames = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        sample_positions = [0, 0.25, 0.5, 0.75, 0.99]  # 在視頻的不同位置取樣

        for pos in sample_positions:
            frame_number = int(total_frames * pos)
            video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            ret, frame = video.read()
            if not ret:
                continue

            # 獲取幀的尺寸
            height, width = frame.shape[:2]

            # 計算裁剪區域
            crop_height = int(height * 0.2)  # 下方1/5的高度
            crop_width = int(width * 0.25)   # 左側1/4的寬度
            crop = frame[height-crop_height:height, 0:crop_width]

            # 對裁剪區域進行OCR
            result = ocr.ocr(crop, cls=False)

            # 提取符合格式的文字
            valid_text, confidence = self.extract_valid_text(result)

            # 可選：顯示裁剪區域（用於調試）
            # cv2.imshow('Cropped Region', crop)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
            if valid_text:
                print(f"在 frame {frame_number} 找到符合格式的文字: {valid_text}, 置信度: {confidence}")
                video.release()
                return valid_text

        # 釋放視頻對象
        video.release()
        print(f"在視頻中未找到符合格式的文字: {file_path}")
        return ''


def parse_filename(filename):
    # 嘗試匹配方括號內的內容
    match = re.search(r'\[(.*?)\]', filename)
    if match:
        bracket_content = match.group(1)
        # 嘗試按下划線分割
        parts = bracket_content.split('_')
        if len(parts) >= 4:
            scene = parts[0].replace('#sc', '').strip()
            shot = parts[1]
            take = parts[2]
            cam_no = parts[3]

            # 處理可能的特殊情況
            if scene.startswith('sc'):
                scene = scene[2:].strip()

            return {
                'Scene': scene,
                'Shot': shot,
                'Take': take,
                'CamNo': cam_no
            }

    # 如果無法正確分割，嘗試其他可能的格式
    match = re.search(r'(\d+)_(\w+)_(\d+)_(\w+)', filename)
    if match:
        return {
            'Scene': match.group(1),
            'Shot': match.group(2),
            'Take': match.group(3),
            'CamNo': match.group(4)
        }

    # 如果仍然無法解析，返回空值
    print(f"無法解析檔名: {filename}")
    return {'Scene': '', 'Shot': '', 'Take': '', 'CamNo': ''}


def backup_files(input_folder):
    backup_folder = f"{input_folder}_BK"
    if not os.path.exists(backup_folder):
        os.makedirs(backup_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.mov'):
            src = os.path.join(input_folder, filename)
            dst = os.path.join(backup_folder, filename)
            shutil.copy2(src, dst)

    print(f"檔案已備份到: {backup_folder}")


def rename_files(input_folder, results):
    for old_filename, vfx_no, parsed, _ in results:  # 添加 _ 來忽略顏色標籤
        if old_filename.lower().endswith('.mov'):
            # 提取方括號內的內容
            match = re.search(r'\[(.*?)\]', old_filename)
            if match:
                bracket_content = match.group(1)
                # 移除 '#' 符號
                bracket_content = bracket_content.replace('#', '')
                # 構建新的檔名
                new_filename = f"{bracket_content}_{vfx_no}.mov"
                old_path = os.path.join(input_folder, old_filename)
                new_path = os.path.join(input_folder, new_filename)
                os.rename(old_path, new_path)
                print(f"已重命名: {old_filename} -> {new_filename}")


def get_file_color_tag(file_path):
    try:
        attrs = xattr.xattr(file_path)
        tag_data = attrs.get('com.apple.metadata:_kMDItemUserTags')
        if tag_data:
            # 解析標籤數據
            import plistlib
            tags = plistlib.loads(tag_data)
            if tags:
                # 假設我們只關心第一個標籤
                color = tags[0].split('\n')[0]
                return color
    except:
        pass
    return ''


class ProcessThread(QThread):
    update_log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, input_folder, do_backup, do_rename):
        super().__init__()
        self.input_folder = input_folder
        self.do_backup = do_backup
        self.do_rename = do_rename

    def run(self):
        self.process_folder()
        self.finished.emit()

    def process_folder(self):
        ocr_processor = OCR_GET_VFXNO()
        results = []

        for filename in os.listdir(self.input_folder):
            if filename.lower().endswith('.mov'):
                file_path = os.path.join(self.input_folder, filename)
                vfx_no = ocr_processor.process_mov(file_path)
                parsed = parse_filename(filename)
                color_tag = get_file_color_tag(file_path)
                results.append((filename, vfx_no, parsed, color_tag))
                self.update_log.emit(f"處理: {filename}\n解析結果: {parsed}")

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        csv_filename = f"FilenameMapping_{timestamp}.csv"
        csv_path = os.path.join(self.input_folder, csv_filename)

        with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(
                ['QTake Filename', 'Scene', 'Shot', 'Take', 'CamNo', 'OCR Result', 'Rating'])
            for filename, vfx_no, parsed, color_tag in results:
                csvwriter.writerow([
                    filename,
                    parsed['Scene'],
                    parsed['Shot'],
                    parsed['Take'],
                    parsed['CamNo'],
                    vfx_no,
                    color_tag
                ])
        self.update_log.emit(f"CSV文件已保存: {csv_path}")

        if self.do_backup:
            backup_files(self.input_folder)
            self.update_log.emit("備份完成")

        if self.do_rename:
            rename_files(self.input_folder, results)
            self.update_log.emit("重命名完成")


class App(QWidget):
    def __init__(self):
        super().__init__()
        self.title = 'QTake OCR 處理器'
        self.initUI()

    def initUI(self):
        self.setWindowTitle(self.title)
        layout = QVBoxLayout()

        # 選擇文件夾按鈕
        self.folder_btn = QPushButton('選擇 QTake 文件夾')
        self.folder_btn.clicked.connect(self.select_folder)
        layout.addWidget(self.folder_btn)

        # 顯示選擇的文件夾路徑
        self.folder_label = QLabel('未選擇文件夾')
        layout.addWidget(self.folder_label)

        # 備份選項
        self.backup_checkbox = QCheckBox('備份原始檔案')
        self.backup_checkbox.setChecked(True)
        layout.addWidget(self.backup_checkbox)

        # 重命名選項
        self.rename_checkbox = QCheckBox('重命名檔案')
        self.rename_checkbox.setChecked(True)
        layout.addWidget(self.rename_checkbox)

        # 開始處理按鈕
        self.process_btn = QPushButton('開始處理')
        self.process_btn.clicked.connect(self.start_processing)
        layout.addWidget(self.process_btn)

        # 日誌窗口
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

        self.setLayout(layout)
        self.show()

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇 QTake 文件夾")
        if folder:
            self.folder_label.setText(folder)

    def start_processing(self):
        input_folder = self.folder_label.text()
        if input_folder == '未選擇文件夾':
            self.log_text.append("請先選擇一個文件夾")
            return

        do_backup = self.backup_checkbox.isChecked()
        do_rename = self.rename_checkbox.isChecked()

        self.process_thread = ProcessThread(input_folder, do_backup, do_rename)
        self.process_thread.update_log.connect(self.update_log)
        self.process_thread.finished.connect(self.processing_finished)
        self.process_thread.start()

        self.process_btn.setEnabled(False)
        self.folder_btn.setEnabled(False)

    def update_log(self, message):
        self.log_text.append(message)

    def processing_finished(self):
        self.process_btn.setEnabled(True)
        self.folder_btn.setEnabled(True)
        self.log_text.append("處理完成")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
