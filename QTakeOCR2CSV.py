'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-10-27 15:48:12
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-10-31 04:22:48
Description: 
pip install xattr

執行這個程式
python QTakeOCR2CSV.py
會要你輸入
1- input的QTake的folder裡面有很多QTake的檔案
    然後會把名稱解析出來，並且做OCR。輸出成為一個csv 在相同路徑下
2- 是否要Rename原本QTake的檔名
    把[]以外的刪除，並且把[]裡面，底線分隔的幾個元素，加上OCR的檔名在最後
3- 是否要備份一份還沒有改變的檔名   
    如果選擇要，就會在原目錄的同一級建立一個同名字的但是後面加上_BK的folder
'''
import cv2
from paddleocr import PaddleOCR
import re
import os
import csv
from datetime import datetime
import shutil
import xattr

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
                # new_filename = f"{bracket_content}_{vfx_no}.mov"
                new_filename = f"{bracket_content}.mov"
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


def process_folder(input_folder, do_backup, do_rename):
    ocr_processor = OCR_GET_VFXNO()
    results = []

    for filename in os.listdir(input_folder):
        if filename.lower().endswith('.mov'):
            file_path = os.path.join(input_folder, filename)
            vfx_no = ocr_processor.process_mov(file_path)
            parsed = parse_filename(filename)
            color_tag = get_file_color_tag(file_path)
            results.append((filename, vfx_no, parsed, color_tag))


            print(f"Processed: {filename}")
            print(f"Parsed result: {parsed}")
    # 創建輸出CSV文件
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    csv_filename = f"FilenameMapping_{timestamp}.csv"
    csv_path = os.path.join(input_folder, csv_filename)

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['QTake Filename',
                           'Scene', 'Shot', 'Take', 'CamNo', 'OCR Result', 'Rating'])
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
    print(f"CSV文件已保存: {csv_path}")

    if do_backup:
        backup_files(input_folder)

    if do_rename:
        rename_files(input_folder, results)

# 主程序
while True:
    input_folder = input("請輸入QTake文件夾的路徑: ").strip()
    if os.path.isdir(input_folder):
        break
    else:
        print("輸入的路徑不存在或不是一個文件夾。請重新輸入。")

print(f"您選擇的文件夾路徑是: {input_folder}")

# 詢問是否要備份
do_backup = input("是否要備份原始檔案？(Y/N，預設Y): ").strip().upper()
do_backup = do_backup != 'N'

# 詢問是否要重命名
do_rename = input("是否要重命名檔案？(Y/N，預設Y): ").strip().upper()
do_rename = do_rename != 'N'

process_folder(input_folder, do_backup, do_rename)

