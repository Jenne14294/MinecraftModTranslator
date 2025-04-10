import sys
import os
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QFileDialog, QLabel, QComboBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QIcon, QColor, QPalette, QFont
from deep_translator import GoogleTranslator
from main import Translator_function

# 自訂的執行翻譯的後台執行緒
class TranslateThread(QThread):
    # 用來通知UI更新的信號
    update_signal = pyqtSignal(str)

    def __init__(self, folder_path, language, parent=None):
        super().__init__(parent)
        self.folder_path = folder_path
        self.language = language
        self.translator = Translator_function()

    def run(self):
        Translator_function.start_translate(self.translator, self.folder_path, self.language, self.update_signal)

class TranslatorApp(QWidget):
    def __init__(self):
        super().__init__()
        Translator_function.__init__(self)

        self.setWindowTitle("Minecraft 模組自動翻譯器")
        self.setGeometry(100, 100, 600, 400)  # 視窗大小
        self.setWindowIcon(QIcon("./icon.ico"))  # 替換為你的圖示

        # 設定界面顏色和風格
        self.set_style()

        # 設置布局
        layout = QVBoxLayout()

        # 資料夾選擇顯示
        self.folder_label = QLabel("未選擇資料夾", self)
        self.folder_label.setStyleSheet("color: #FFFFFF; font-size: 16px; font-weight: bold;")
        layout.addWidget(self.folder_label)

        # 選擇資料夾的按鈕
        folder_button = QPushButton("選擇資料夾", self)
        folder_button.setStyleSheet(self.button_style())
        folder_button.clicked.connect(self.select_folder)
        layout.addWidget(folder_button)

        # 語言選單
        self.language_combo = QComboBox(self)
        self.language_combo.addItem("繁體中文", "zh_tw")
        self.language_combo.addItem("簡體中文", "zh_cn")
        self.language_combo.addItem("英文", "en_us")
        self.language_combo.setStyleSheet(self.combo_box_style())
        layout.addWidget(self.language_combo)

        # 開始翻譯的按鈕
        translate_button = QPushButton("開始翻譯", self)
        translate_button.setStyleSheet(self.button_style())
        translate_button.clicked.connect(self.start_translation)
        layout.addWidget(translate_button)

        # 顯示結果
        self.result_label = QLabel("", self)
        self.result_label.setStyleSheet("color: #FFFFFF; font-size: 14px;")
        layout.addWidget(self.result_label)

        # 顯示翻譯資訊
        self.info_label1 = QLabel("", self)
        self.info_label2 = QLabel("", self)
        self.info_label1.setStyleSheet("color: #A8A8A8; font-size: 14px;")
        self.info_label2.setStyleSheet("color: #A8A8A8; font-size: 14px;")
        layout.addWidget(self.info_label1)
        layout.addWidget(self.info_label2)

        # 設定布局
        self.setLayout(layout)

        # 預設語言設定
        self.current_lang = self.language_combo.currentData()  # 預設為繁體中文

        # 初始化翻譯文字
        self.update_translation_info()

    def set_style(self):
        # 設置背景顏色，加入漸層背景
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(26, 32, 44))  # 深藍色背景
        self.setAutoFillBackground(True)
        self.setPalette(palette)

        # 設定字型
        font = QFont("Roboto", 16)
        self.setFont(font)

    def button_style(self):
        # 按鈕樣式，加入圓角、漸層和陰影
        return """
        QPushButton {
            background-color: #4CAF50;
            color: white;
            font-size: 16px;
            padding: 12px;
            border-radius: 12px;
            border: none;
            box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.2);
        }
        QPushButton:hover {
            background-color: #45a049;
            box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.3);
        }
        QPushButton:pressed {
            background-color: #388E3C;
        }
        """

    def combo_box_style(self):
        # 設置語言選單樣式
        return """
        QComboBox {
            background-color: #333333;
            color: #FFFFFF;
            font-size: 14px;
            border-radius: 8px;
            padding: 8px;
        }
        QComboBox::drop-down {
            border: none;
        }
        """

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "選擇資料夾")
        if folder:
            self.folder_label.setText(f"選擇的資料夾: {folder}")
            self.folder_path = folder

    def start_translation(self):
        # 取得語言選項
        selected_language = self.language_combo.currentData()

        if hasattr(self, 'folder_path'):
            # 創建並啟動翻譯後台執行緒
            self.translation_thread = TranslateThread(self.folder_path, selected_language)
            self.translation_thread.update_signal.connect(self.update_result)
            self.translation_thread.start()
        else:
            self.result_label.setText("請先選擇資料夾！")

    def update_result(self, message):
        self.result_label.setText(message)

    def update_translation_info(self):
        # 提供預設翻譯資訊
        info1 = "選擇要翻譯的模組資料夾，按下開始就開始進行翻譯"
        info2 = "使用前建議將模組額外複製一份再進行翻譯，否則可能會出現模組損毀"

        # 顯示翻譯資訊
        self.info_label1.setText(info1)
        self.info_label2.setText(info2)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = TranslatorApp()
    window.show()
    sys.exit(app.exec_())
