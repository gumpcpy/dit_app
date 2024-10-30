'''
Author: gumpcpy gumpcpy@gmail.com
Date: 2024-10-31 04:45:03
LastEditors: gumpcpy gumpcpy@gmail.com
LastEditTime: 2024-10-31 04:50:58
Description: 
'''
import sys
import os
import time
import shutil
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from QT_QTakeOCR2CSV import OCR_GET_VFXNO


class FileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.mov'):
            self.callback(event.src_path)


class WatcherThread:
    def __init__(self, path):
        self.path = path
        self.observer = Observer()
        self.ocr_processor = OCR_GET_VFXNO()

    def start(self):
        event_handler = FileHandler(self.process_file)
        self.observer.schedule(event_handler, self.path, recursive=False)
        self.observer.start()
        print(f"開始監聽Folder: {self.path}")

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    def process_file(self, file_path):
        print(f"處理檔案: {os.path.basename(file_path)}")

        # OCR
        vfx_no = self.ocr_processor.process_mov(file_path)
        print(f"OCR 结果: {vfx_no}")

        # Backup
        self.backup_file(file_path)

        # Rename
        new_filename = self.rename_file(file_path, vfx_no)

        print(f"處理完成: {os.path.basename(file_path)} -> {new_filename}")

    def backup_file(self, file_path):
        original_folder = os.path.dirname(file_path)
        backup_folder = f"{original_folder}_BK"

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        backup_file_path = os.path.join(
            backup_folder, os.path.basename(file_path))
        shutil.copy2(file_path, backup_file_path)
        print(f"已經備份到: {backup_file_path}")

    def rename_file(self, file_path, vfx_no):
        filename = os.path.basename(file_path)
        match = re.search(r'\[(.*?)\]', filename)

        if match and vfx_no:
            bracket_content = match.group(1).replace('#', '')
            new_filename = f"{bracket_content}.mov"
            new_path = os.path.join(os.path.dirname(file_path), new_filename)
            os.rename(file_path, new_path)
            print(f"已重命名為: {new_filename}")
            return new_filename

        return filename


if __name__ == '__main__':
    folder = input("請輸入要監聽的Folder Path: ").strip()

    if not os.path.exists(folder) or not os.path.isdir(folder):
        print("無效的Folder Path, 請重新輸入")
        sys.exit(1)

    watcher_thread = WatcherThread(folder)
    watcher_thread.start()
