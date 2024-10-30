import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTextEdit, QFileDialog
from PyQt5.QtCore import QThread, pyqtSignal
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from QTakeOCR2CSV_QT import OCR_GET_VFXNO
import shutil
import re


class FileHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback

    def on_created(self, event):
        if not event.is_directory and event.src_path.lower().endswith('.mov'):
            self.callback(event.src_path)


class WatcherThread(QThread):
    file_processed = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.observer = Observer()
        self.ocr_processor = OCR_GET_VFXNO()

    def run(self):
        event_handler = FileHandler(self.process_file)
        self.observer.schedule(event_handler, self.path, recursive=False)
        self.observer.start()
        try:
            while self.observer.is_alive():
                self.observer.join(1)
        except KeyboardInterrupt:
            self.observer.stop()
        self.observer.join()

    def process_file(self, file_path):
        self.file_processed.emit(f"Processing: {os.path.basename(file_path)}")

        # OCR处理
        vfx_no = self.ocr_processor.process_mov(file_path)
        self.file_processed.emit(f"OCR Result: {vfx_no}")

        # 备份文件
        self.backup_file(file_path)

        # 重命名文件
        new_filename = self.rename_file(file_path, vfx_no)

        self.file_processed.emit(
            f"Processed: {os.path.basename(file_path)} -> {new_filename}")

    def backup_file(self, file_path):
        original_folder = os.path.dirname(file_path)
        parent_folder = os.path.dirname(original_folder)
        backup_folder = f"{original_folder}_BK"

        if not os.path.exists(backup_folder):
            os.makedirs(backup_folder)

        backup_file_path = os.path.join(
            backup_folder, os.path.basename(file_path))
        shutil.copy2(file_path, backup_file_path)
        self.file_processed.emit(f"Backed up to: {backup_file_path}")

    def rename_file(self, file_path, vfx_no):
        filename = os.path.basename(file_path)
        match = re.search(r'\[(.*?)\]', filename)
        if match and vfx_no:
            bracket_content = match.group(1).replace('#', '')
            # new_filename = f"{bracket_content}_{vfx_no}.mov"
            new_filename = f"{bracket_content}.mov"
            new_path = os.path.join(os.path.dirname(file_path), new_filename)
            os.rename(file_path, new_path)
            self.file_processed.emit(f"Renamed to: {new_filename}")
            return new_filename
        return filename


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        input_layout = QHBoxLayout()
        self.folder_input = QLineEdit()
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_folder)
        input_layout.addWidget(self.folder_input)
        input_layout.addWidget(browse_button)

        self.start_button = QPushButton("Start Watching")
        self.start_button.clicked.connect(self.start_watching)

        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)

        layout.addLayout(input_layout)
        layout.addWidget(self.start_button)
        layout.addWidget(self.log_output)

        self.setLayout(layout)
        self.setWindowTitle('QT Watch Folder')
        self.setGeometry(300, 300, 500, 400)

    def browse_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:
            self.folder_input.setText(folder)

    def start_watching(self):
        folder = self.folder_input.text()
        if not folder:
            self.log_output.append("Please select a folder to watch.")
            return

        self.watcher_thread = WatcherThread(folder)
        self.watcher_thread.file_processed.connect(self.update_log)
        self.watcher_thread.start()

        self.log_output.append(f"Watching folder: {folder}")
        self.start_button.setEnabled(False)

    def update_log(self, message):
        self.log_output.append(message)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec_())
