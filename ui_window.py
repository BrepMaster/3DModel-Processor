"""
用户界面模块 - 综合工具箱 (完整实现)
"""

import os
import traceback
import time
import json
from pathlib import Path
from types import SimpleNamespace
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFileDialog,
    QMessageBox, QProgressBar, QComboBox, QDialog,
    QTextEdit, QDialogButtonBox, QGroupBox, QScrollArea,
    QTabWidget, QCheckBox, QSpinBox, QSizePolicy,
    QRadioButton
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer, QSize, QUrl
from PyQt5.QtGui import QFont, QColor, QPalette, QTextDocument, QPixmap
from file_operations import (
    count_files_in_subfolders,
    delete_large_files,
    delete_folders_by_file_count
)
from dataset_processor import (
    split_dataset,
    classify_files_by_name,
    copy_files_by_suffix
)
from graph_processor import init
from statistics_analyzer import StatisticsAnalyzer
from model_processor import ModelProcessor
from PyQt5.QtWidgets import (
    QRadioButton, QDateTimeEdit, QSpinBox, QGridLayout
)
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QPixmap
from system_tools import SystemMonitor, LogAnalyzer
from visualization import VisualizationTab
from help_functions import get_visualization_help

class CustomMessageBox(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setSizeGripEnabled(True)
        self.setStyleSheet("""
            QMessageBox {
                min-width: 400px;
                min-height: 200px;
            }
            QLabel#qt_msgbox_label {
                min-width: 350px;
                min-height: 150px;
            }
            QScrollArea {
                min-width: 350px;
                min-height: 150px;
            }
            QMessageBox QLabel {
                min-width: 300px;
                min-height: 80px;
            }
        """)

    def setText(self, text):
        super().setText(text)
        self.adjustSize()

    def setDetailedText(self, text):
        super().setDetailedText(text)
        self.adjustSize()

    def sizeHint(self):
        # 计算文本所需的空间
        doc = QTextDocument()
        doc.setHtml(self.text())
        text_width = doc.idealWidth() + 30  # 减少边距
        text_height = doc.size().height() + 30

        if self.detailedText():
            doc.setPlainText(self.detailedText())
            text_width = max(text_width, doc.idealWidth() + 30)
            text_height += doc.size().height() + 30

        # 确保最小尺寸
        text_width = max(text_width, 400)  # 减小最小宽度
        text_height = max(text_height, 200)  # 减小最小高度

        # 限制最大尺寸不超过屏幕的60%
        screen = QApplication.primaryScreen().availableGeometry()
        max_width = screen.width() * 0.6  # 从80%减小到60%
        max_height = screen.height() * 0.6

        return QSize(
            min(int(text_width), int(max_width)),
            min(int(text_height), int(max_height))
        )

class WorkerThread(QThread):
    finished = pyqtSignal(object)
    error = pyqtSignal(str)
    progress = pyqtSignal(int, int)  # 当前值, 最大值

    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._is_running = True

    def run(self):
        try:
            # 如果函数支持进度回调，则传入回调函数
            if hasattr(self.func, '__code__') and 'progress_callback' in self.func.__code__.co_varnames:
                self.kwargs['progress_callback'] = self.progress_callback

            result = self.func(*self.args, **self.kwargs)
            if self._is_running:
                self.finished.emit(result)
        except Exception as e:
            if self._is_running:
                self.error.emit(str(e))

    def progress_callback(self, current, total=None):
        """处理进度回调"""
        if self._is_running:
            self.progress.emit(current, total or 100)

    def stop(self):
        """停止线程"""
        self._is_running = False
        self.quit()

class MainWindow(QWidget):
    """主窗口 - 综合工具箱"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("综合工具箱")
        self.resize(1200, 800)  # 增大窗口尺寸
        self.setStyle()
        self.init_ui()
        self.center()

    def setStyle(self):
        """设置窗口样式"""
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#f0f0f0"))
        self.setPalette(palette)

        self.setStyleSheet("""
            QWidget {
                font-family: "Microsoft YaHei";
                font-size: 14px;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 3px;
            }
            QLineEdit, QComboBox {
                padding: 6px;
                border: 1px solid #ccc;
                border-radius: 4px;
                min-width: 200px;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                padding: 6px 14px;
                border: none;
                border-radius: 4px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
            QLabel {
                min-width: 120px;
            }
            QProgressBar {
                height: 20px;
                border: 1px solid #aaa;
                border-radius: 5px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #00c853;
                width: 20px;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                font-family: "Courier New";
                font-size: 12px;
            }
            QTabWidget::pane {
                border: 1px solid #ccc;
                padding: 5px;
            }
            QTabBar::tab {
                padding: 8px 15px;
                background: #e0e0e0;
                border: 1px solid #ccc;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background: #f0f0f0;
                border-bottom: 1px solid #f0f0f0;
                margin-bottom: -1px;
            }
            HelpDialog {
                background-color: #f9f9f9;
            }
            HelpDialog QTextEdit {
                background-color: white;
                border: 1px solid #ddd;
                padding: 10px;
                font-size: 13px;
            }
            QPushButton[text="帮助"] {
                background-color: #6c757d;
            }
            QPushButton[text="帮助"]:hover {
                background-color: #5a6268;
            }
        """)

    def init_ui(self):
        """初始化用户界面"""
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # 创建标签页
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.tabs.setDocumentMode(True)

        # 数据集处理标签页
        self.data_tab = DataProcessingTab(self)
        self.tabs.addTab(self.data_tab, "数据集处理工具")

        # 图数据处理标签页
        self.graph_tab = GraphProcessingTab(self)
        self.tabs.addTab(self.graph_tab, "图数据处理工具")

        # 3D模型处理标签页
        self.model_tab = ModelProcessingTab(self)
        self.tabs.addTab(self.model_tab, "3D模型处理工具")

        # 可视化标签页
        self.viz_tab = VisualizationTab(self)
        self.tabs.addTab(self.viz_tab, "可视化工具")

        # 系统工具标签页
        self.system_tab = SystemToolsTab(self)
        self.tabs.addTab(self.system_tab, "系统工具")


        main_layout.addWidget(self.tabs, stretch=1)

        # 进度条
        self.progress = QProgressBar()
        self.progress.setRange(0, 100)
        self.progress.setAlignment(Qt.AlignCenter)
        self.progress.setFixedHeight(25)
        self.progress.setFormat("准备就绪")
        main_layout.addWidget(self.progress)

        self.setLayout(main_layout)

    def center(self):
        """居中窗口"""
        screen = QApplication.desktop().screenGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def closeEvent(self, event):
        """关闭窗口时确保所有线程停止"""
        for tab in [self.data_tab, self.graph_tab, self.model_tab, self.system_tab]:
            if hasattr(tab, 'thread') and tab.thread is not None and isinstance(tab.thread, WorkerThread):
                tab.thread.stop()
        event.accept()


class DataProcessingTab(QWidget):
    """数据集处理功能标签页 - 完整版"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 功能选择
        mode_layout = QHBoxLayout()
        self.mode_label = QLabel("选择功能:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            '划分数据集',
            '根据文件名划分到子文件夹',
            '按后缀提取文件到目标目录',
            '统计子文件夹中的文件数量',
            '删除大文件（按大小）',
            '删除文件夹（文件数小于阈值）',
            '根据txt文件组织数据集',
            '分析数据集平衡性',
            '删除指定后缀的文件',
            '对比两个路径差异'
        ])
        self.mode_combo.currentIndexChanged.connect(self.toggle_mode_inputs)
        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # 路径设置组
        path_group = QGroupBox("路径设置")
        path_layout = QVBoxLayout()

        # 输入路径1（用于对比功能）
        self.input1_layout = QHBoxLayout()
        self.input1_label = QLabel('路径1:')
        self.input1_line = QLineEdit()
        self.input1_btn = QPushButton('浏览...')
        self.input1_btn.clicked.connect(lambda: self.select_input_dir(self.input1_line))
        self.input1_layout.addWidget(self.input1_label)
        self.input1_layout.addWidget(self.input1_line)
        self.input1_layout.addWidget(self.input1_btn)
        path_layout.addLayout(self.input1_layout)

        # 输入路径2（用于对比功能）
        self.input2_layout = QHBoxLayout()
        self.input2_label = QLabel('路径2:')
        self.input2_line = QLineEdit()
        self.input2_btn = QPushButton('浏览...')
        self.input2_btn.clicked.connect(lambda: self.select_input_dir(self.input2_line))
        self.input2_layout.addWidget(self.input2_label)
        self.input2_layout.addWidget(self.input2_line)
        self.input2_layout.addWidget(self.input2_btn)
        path_layout.addLayout(self.input2_layout)

        # 输入路径（用于其他功能）
        self.input_layout = QHBoxLayout()
        self.input_label = QLabel('输入目录:')
        self.input_line = QLineEdit()
        self.input_btn = QPushButton('浏览...')
        self.input_btn.clicked.connect(lambda: self.select_input_dir(self.input_line))
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_line)
        self.input_layout.addWidget(self.input_btn)
        path_layout.addLayout(self.input_layout)

        # 训练集txt路径
        self.train_txt_layout = QHBoxLayout()
        self.train_txt_label = QLabel('训练集txt:')
        self.train_txt_line = QLineEdit()
        self.train_txt_btn = QPushButton('浏览...')
        self.train_txt_btn.clicked.connect(self.select_train_txt)
        self.train_txt_layout.addWidget(self.train_txt_label)
        self.train_txt_layout.addWidget(self.train_txt_line)
        self.train_txt_layout.addWidget(self.train_txt_btn)
        path_layout.addLayout(self.train_txt_layout)

        # 测试集txt路径
        self.test_txt_layout = QHBoxLayout()
        self.test_txt_label = QLabel('测试集txt:')
        self.test_txt_line = QLineEdit()
        self.test_txt_btn = QPushButton('浏览...')
        self.test_txt_btn.clicked.connect(self.select_test_txt)
        self.test_txt_layout.addWidget(self.test_txt_label)
        self.test_txt_layout.addWidget(self.test_txt_line)
        self.test_txt_layout.addWidget(self.test_txt_btn)
        path_layout.addLayout(self.test_txt_layout)

        # 输出路径
        self.output_layout = QHBoxLayout()
        self.output_label = QLabel('输出目录:')
        self.output_line = QLineEdit()
        self.output_btn = QPushButton('浏览...')
        self.output_btn.clicked.connect(self.select_output_dir)
        self.output_layout.addWidget(self.output_label)
        self.output_layout.addWidget(self.output_line)
        self.output_layout.addWidget(self.output_btn)
        path_layout.addLayout(self.output_layout)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # 参数设置组
        param_group = QGroupBox("参数设置")
        param_layout = QVBoxLayout()

        # 测试集比例
        self.ratio_layout = QHBoxLayout()
        self.ratio_label = QLabel('测试集比例 (0-1):')
        self.ratio_line = QLineEdit('0.2')
        self.ratio_layout.addWidget(self.ratio_label)
        self.ratio_layout.addWidget(self.ratio_line)
        param_layout.addLayout(self.ratio_layout)

        # 文件后缀
        self.suffix_layout = QHBoxLayout()
        self.suffix_label = QLabel('文件后缀 (如 .jpg,.png):')
        self.suffix_line = QLineEdit('.jpg')
        self.suffix_layout.addWidget(self.suffix_label)
        self.suffix_layout.addWidget(self.suffix_line)
        param_layout.addLayout(self.suffix_layout)

        # 大文件大小阈值
        self.size_layout = QHBoxLayout()
        self.size_label = QLabel('大小阈值 (MB):')
        self.size_line = QLineEdit('5')
        self.size_layout.addWidget(self.size_label)
        self.size_layout.addWidget(self.size_line)
        param_layout.addLayout(self.size_layout)

        # 文件夹文件数下限
        self.count_threshold_layout = QHBoxLayout()
        self.count_threshold_label = QLabel('文件数量下限:')
        self.count_threshold_line = QLineEdit('5')
        self.count_threshold_layout.addWidget(self.count_threshold_label)
        self.count_threshold_layout.addWidget(self.count_threshold_line)
        param_layout.addLayout(self.count_threshold_layout)

        # 删除确认复选框
        self.confirm_delete_layout = QHBoxLayout()
        self.confirm_delete_check = QCheckBox('确认删除操作（此操作不可逆）')
        self.confirm_delete_check.setChecked(False)
        param_layout.addLayout(self.confirm_delete_layout)
        param_layout.addWidget(self.confirm_delete_check)

        # 对比选项
        self.compare_options_layout = QHBoxLayout()
        self.compare_name_check = QCheckBox('比较文件名')
        self.compare_name_check.setChecked(True)
        self.compare_size_check = QCheckBox('比较文件大小')
        self.compare_size_check.setChecked(True)
        self.compare_mtime_check = QCheckBox('比较修改时间')
        self.compare_mtime_check.setChecked(False)
        self.compare_content_check = QCheckBox('比较文件内容')
        self.compare_content_check.setChecked(False)
        self.compare_options_layout.addWidget(self.compare_name_check)
        self.compare_options_layout.addWidget(self.compare_size_check)
        self.compare_options_layout.addWidget(self.compare_mtime_check)
        self.compare_options_layout.addWidget(self.compare_content_check)
        param_layout.addLayout(self.compare_options_layout)

        param_group.setLayout(param_layout)
        layout.addWidget(param_group)

        # 按钮布局
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton('开始处理')
        self.run_btn.clicked.connect(self.run_tool)
        self.help_btn = QPushButton('帮助')
        self.help_btn.clicked.connect(self.show_help)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.help_btn)
        layout.addLayout(btn_layout)

        # 结果展示区域
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        layout.addWidget(self.result_text)

        self.setLayout(layout)
        self.toggle_mode_inputs()

    def toggle_mode_inputs(self):
        mode = self.mode_combo.currentText()
        is_split = mode == '划分数据集'
        is_suffix = mode in ['按后缀提取文件到目标目录', '统计子文件夹中的文件数量', '删除指定后缀的文件']
        is_large_file_delete = mode == '删除大文件（按大小）'
        is_folder_delete = mode == '删除文件夹（文件数小于阈值）'
        is_organize_by_txt = mode == '根据txt文件组织数据集'
        is_balance_analysis = mode == '分析数据集平衡性'
        is_delete_by_suffix = mode == '删除指定后缀的文件'
        is_compare = mode == '对比两个路径差异'
        has_output = mode in ['划分数据集', '根据文件名划分到子文件夹',
                              '按后缀提取文件到目标目录', '分析数据集平衡性']

        # 显示/隐藏路径输入控件
        self.input1_label.setVisible(is_compare)
        self.input1_line.setVisible(is_compare)
        self.input1_btn.setVisible(is_compare)
        self.input2_label.setVisible(is_compare)
        self.input2_line.setVisible(is_compare)
        self.input2_btn.setVisible(is_compare)
        self.input_label.setVisible(not is_compare)
        self.input_line.setVisible(not is_compare)
        self.input_btn.setVisible(not is_compare)

        # 其他控件可见性
        self.ratio_label.setVisible(is_split)
        self.ratio_line.setVisible(is_split)
        self.suffix_label.setVisible(is_suffix)
        self.suffix_line.setVisible(is_suffix)
        self.size_label.setVisible(is_large_file_delete)
        self.size_line.setVisible(is_large_file_delete)
        self.count_threshold_label.setVisible(is_folder_delete)
        self.count_threshold_line.setVisible(is_folder_delete)
        self.confirm_delete_check.setVisible(is_delete_by_suffix)

        # 对比选项可见性
        self.compare_name_check.setVisible(is_compare)
        self.compare_size_check.setVisible(is_compare)
        self.compare_mtime_check.setVisible(is_compare)
        self.compare_content_check.setVisible(is_compare)

        self.train_txt_label.setVisible(is_organize_by_txt)
        self.train_txt_line.setVisible(is_organize_by_txt)
        self.train_txt_btn.setVisible(is_organize_by_txt)
        self.test_txt_label.setVisible(is_organize_by_txt)
        self.test_txt_line.setVisible(is_organize_by_txt)
        self.test_txt_btn.setVisible(is_organize_by_txt)
        self.output_label.setVisible(has_output or is_organize_by_txt)
        self.output_line.setVisible(has_output or is_organize_by_txt)
        self.output_btn.setVisible(has_output or is_organize_by_txt)

    def show_help(self):
        """显示当前功能的帮助信息"""
        from help_functions import get_data_processing_help
        mode = self.mode_combo.currentText()
        help_text = get_data_processing_help(mode)
        dialog = HelpDialog(mode, help_text, self)
        dialog.exec_()

    def select_input_dir(self, line_edit):
        dir_path = QFileDialog.getExistingDirectory(self, '选择目录')
        if dir_path:
            line_edit.setText(dir_path)

    def select_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, '选择输出目录')
        if dir_path:
            self.output_line.setText(dir_path)

    def select_train_txt(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 train.txt 文件", "", "Text Files (*.txt)"
        )
        if file_path:
            self.train_txt_line.setText(file_path)

    def select_test_txt(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择 test.txt 文件", "", "Text Files (*.txt)"
        )
        if file_path:
            self.test_txt_line.setText(file_path)

    def validate_inputs(self, mode, input_dir, output_dir):
        if mode == '对比两个路径差异':
            path1 = self.input1_line.text().strip()
            path2 = self.input2_line.text().strip()

            if not path1 or not path2:
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('请输入两个路径进行对比！')
                msg.exec_()
                return False

            if not os.path.exists(path1):
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('路径1不存在！')
                msg.exec_()
                return False

            if not os.path.exists(path2):
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('路径2不存在！')
                msg.exec_()
                return False

            return True

        if not input_dir:
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle('警告')
            msg.setText('请输入输入目录！')
            msg.exec_()
            return False
        if not os.path.exists(input_dir):
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle('警告')
            msg.setText('输入目录不存在！')
            msg.exec_()
            return False

        if mode in ['划分数据集', '根据文件名划分到子文件夹', '按后缀提取文件到目标目录', '分析数据集平衡性']:
            if not output_dir:
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('请输入输出目录！')
                msg.exec_()
                return False
            os.makedirs(output_dir, exist_ok=True)

        if mode == '划分数据集':
            try:
                test_ratio = float(self.ratio_line.text())
                if not 0 < test_ratio < 1:
                    raise ValueError
            except ValueError:
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('测试集比例必须是0到1之间的小数！')
                msg.exec_()
                return False

        if mode in ['删除大文件（按大小）']:
            try:
                size_threshold = float(self.size_line.text())
                if size_threshold <= 0:
                    raise ValueError
            except ValueError:
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('文件大小阈值必须是大于0的数字！')
                msg.exec_()
                return False

        if mode in ['删除文件夹（文件数小于阈值）']:
            try:
                threshold = int(self.count_threshold_line.text())
                if threshold < 0:
                    raise ValueError
            except ValueError:
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('文件数量阈值必须是非负整数！')
                msg.exec_()
                return False

        if mode == '根据txt文件组织数据集':
            train_txt = self.train_txt_line.text().strip()
            test_txt = self.test_txt_line.text().strip()

            if not train_txt or not test_txt:
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('请选择train.txt和test.txt文件！')
                msg.exec_()
                return False

            if not os.path.exists(train_txt):
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('train.txt文件不存在！')
                msg.exec_()
                return False

            if not os.path.exists(test_txt):
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('test.txt文件不存在！')
                msg.exec_()
                return False

            if not output_dir:
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('请输入输出目录！')
                msg.exec_()
                return False

            os.makedirs(output_dir, exist_ok=True)

        if mode == '删除指定后缀的文件':
            suffixes = [s.strip().lower() for s in self.suffix_line.text().split(',') if s.strip()]
            if not suffixes:
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('必须提供至少一个后缀！')
                msg.exec_()
                return False

            if not self.confirm_delete_check.isChecked():
                msg = CustomMessageBox(self)
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle('警告')
                msg.setText('请先勾选"确认删除操作"复选框！')
                msg.exec_()
                return False

        return True

    def run_tool(self):
        mode = self.mode_combo.currentText()

        if mode == '对比两个路径差异':
            path1 = self.input1_line.text().strip()
            path2 = self.input2_line.text().strip()

            if not self.validate_inputs(mode, path1, path2):
                return

            self.parent.progress.setValue(0)
            self.parent.progress.setFormat("对比中...")

            compare_options = {
                'name': self.compare_name_check.isChecked(),
                'size': self.compare_size_check.isChecked(),
                'mtime': self.compare_mtime_check.isChecked(),
                'content': self.compare_content_check.isChecked()
            }

            self.execute_compare_paths(path1, path2, compare_options)
        else:
            input_dir = self.input_line.text().strip()
            output_dir = self.output_line.text().strip()

            if not self.validate_inputs(mode, input_dir, output_dir):
                return

            self.parent.progress.setValue(0)
            self.parent.progress.setFormat("处理中...")

            if mode == '划分数据集':
                self.execute_split_dataset(input_dir, output_dir)
            elif mode == '根据文件名划分到子文件夹':
                self.execute_classify_files(input_dir, output_dir)
            elif mode == '按后缀提取文件到目标目录':
                self.execute_copy_by_suffix(input_dir, output_dir)
            elif mode == '统计子文件夹中的文件数量':
                self.execute_count_files(input_dir)
            elif mode == '删除大文件（按大小）':
                self.execute_delete_large_files(input_dir)
            elif mode == '删除文件夹（文件数小于阈值）':
                self.execute_delete_folders(input_dir)
            elif mode == '根据txt文件组织数据集':
                self.organize_by_txt(input_dir, output_dir)
            elif mode == '分析数据集平衡性':
                self.analyze_dataset_balance(input_dir, output_dir)
            elif mode == '删除指定后缀的文件':
                self.execute_delete_files_by_suffix(input_dir)

    def execute_split_dataset(self, input_dir, output_dir):
        test_ratio = float(self.ratio_line.text())

        def _split():
            from dataset_processor import split_dataset
            return split_dataset(input_dir, output_dir, test_ratio)

        self.run_in_thread(_split, self.on_split_complete)

    def on_split_complete(self, result):
        train_list, test_list = result
        msg = CustomMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('完成')
        msg.setText(f'数据集划分完成！\n训练集: {len(train_list)} 个样本\n测试集: {len(test_list)} 个样本')
        msg.exec_()
        self.parent.progress.setFormat("完成")

    def execute_classify_files(self, input_dir, output_dir):
        def _classify():
            from dataset_processor import classify_files_by_name
            return classify_files_by_name(input_dir, output_dir)

        self.run_in_thread(_classify, self.on_classify_complete)

    def on_classify_complete(self, processed):
        msg = CustomMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('完成')
        msg.setText(f'文件分类完成！\n共处理 {processed} 个文件')
        msg.exec_()
        self.parent.progress.setFormat("完成")

    def execute_copy_by_suffix(self, input_dir, output_dir):
        suffixes = [s.strip().lower() for s in self.suffix_line.text().split(',') if s.strip()]

        def _copy():
            from dataset_processor import copy_files_by_suffix
            return copy_files_by_suffix(input_dir, output_dir, suffixes)

        self.run_in_thread(_copy, self.on_copy_complete)

    def on_copy_complete(self, copied):
        msg = CustomMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('完成')
        msg.setText(f'文件复制完成！\n共复制 {copied} 个文件')
        msg.exec_()
        self.parent.progress.setFormat("完成")

    def execute_count_files(self, input_dir):
        suffixes = [s.strip().lower() for s in self.suffix_line.text().split(',') if s.strip()]

        def _count():
            from file_operations import count_files_in_subfolders
            return count_files_in_subfolders(input_dir, suffixes)

        self.run_in_thread(_count, self.on_count_complete)

    def on_count_complete(self, result):
        stats, total = result
        result_lines = [f"{k}: {v} 个文件" for k, v in stats.items()]
        result_lines.append(f"\n总文件数: {total}")
        dialog = StatisticsDialog("\n".join(result_lines), "统计结果", self)
        dialog.exec_()
        self.parent.progress.setFormat("完成")

    def execute_delete_large_files(self, input_dir):
        size_threshold = float(self.size_line.text())

        def _delete():
            from file_operations import delete_large_files
            return delete_large_files(input_dir, size_threshold)

        self.run_in_thread(_delete, self.on_delete_large_complete)

    def on_delete_large_complete(self, result):
        total_files, deleted, errors = result
        result_lines = [f"共扫描文件数: {total_files}", f"共删除文件数: {deleted}"]
        if errors:
            result_lines.append("\n错误信息:")
            result_lines.extend(errors)
        dialog = StatisticsDialog("\n".join(result_lines), "删除结果", self)
        dialog.exec_()
        self.parent.progress.setFormat("完成")

    def execute_delete_folders(self, input_dir):
        threshold = int(self.count_threshold_line.text())

        def _delete():
            from file_operations import delete_folders_by_file_count
            return delete_folders_by_file_count(input_dir, threshold)

        self.run_in_thread(_delete, self.on_delete_folders_complete)

    def on_delete_folders_complete(self, result):
        deleted_count, results = result
        result_lines = results + [f"\n共删除文件夹数量: {deleted_count}"]
        dialog = StatisticsDialog("\n".join(result_lines), "删除文件夹结果", self)
        dialog.exec_()
        self.parent.progress.setFormat("完成")

    def organize_by_txt(self, input_dir, output_dir):
        train_file = self.train_txt_line.text().strip()
        test_file = self.test_txt_line.text().strip()

        def _organize():
            from dataset_processor import organize_files_by_txt
            return organize_files_by_txt(input_dir, train_file, test_file, output_dir)

        self.run_in_thread(_organize, self.on_organize_complete)

    def on_organize_complete(self, result):
        train_count, test_count = result
        msg = CustomMessageBox(self)
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('完成')
        msg.setText(f'文件组织完成！\n训练集: {train_count} 个文件\n测试集: {test_count} 个文件')
        msg.exec_()
        self.parent.progress.setFormat("完成")

    def analyze_dataset_balance(self, input_dir, output_dir):
        def _analyze():
            from dataset_processor import analyze_dataset_balance
            return analyze_dataset_balance(input_dir, output_dir)

        self.run_in_thread(_analyze, self.on_analyze_balance_complete)

    def on_analyze_balance_complete(self, result):
        stats, report = result

        dialog = StatisticsDialog(report, "数据集平衡性分析报告", self)
        dialog.exec_()

        self.parent.progress.setFormat("完成")

    def execute_delete_files_by_suffix(self, input_dir):
        suffixes = [s.strip().lower() for s in self.suffix_line.text().split(',') if s.strip()]

        def _delete():
            from file_operations import delete_files_by_suffix
            return delete_files_by_suffix(input_dir, suffixes)

        self.run_in_thread(_delete, self.on_delete_files_complete)

    def on_delete_files_complete(self, result):
        total_files, deleted_count, errors = result

        result_lines = [
            f"共扫描文件数: {total_files}",
            f"成功删除文件数: {deleted_count}",
            f"失败删除数: {len(errors)}"
        ]

        if errors:
            result_lines.append("\n错误信息:")
            result_lines.extend(errors[:10])  # 只显示前10个错误

        dialog = StatisticsDialog("\n".join(result_lines), "删除结果", self)
        dialog.exec_()
        self.parent.progress.setFormat("完成")

    def execute_compare_paths(self, path1, path2, compare_options):
        """执行路径对比操作"""

        def _compare():
            from file_operations import compare_directories
            return compare_directories(path1, path2, compare_options)

        self.run_in_thread(_compare, self.on_compare_complete)

    def on_compare_complete(self, result):
        """路径对比完成回调"""
        differences = result

        if not differences:
            self.result_text.setPlainText("两个路径内容完全相同")
            self.parent.progress.setFormat("完成")
            return

        report = "路径对比结果:\n"
        report += f"路径1: {self.input1_line.text()}\n"
        report += f"路径2: {self.input2_line.text()}\n\n"
        report += "差异详情:\n"

        for diff_type, files in differences.items():
            if files:  # 只显示有差异的类型
                report += f"\n{diff_type} ({len(files)}个):\n"
                for file in files[:50]:  # 最多显示50个文件
                    report += f"  - {file}\n"
                if len(files) > 50:
                    report += f"  ...(共{len(files)}个文件，只显示前50个)\n"

        self.result_text.setPlainText(report)
        self.parent.progress.setFormat("完成")

    def run_in_thread(self, func, success_callback, error_callback=None):
        """在子线程中运行函数"""
        if self.thread and self.thread.isRunning():
            self.thread.stop()

        self.thread = WorkerThread(func)
        self.thread.finished.connect(success_callback)
        if error_callback:
            self.thread.error.connect(error_callback)
        else:
            self.thread.error.connect(self.on_thread_error)
        self.thread.progress.connect(self.update_progress)
        self.thread.start()

    def update_progress(self, current, total):
        """更新进度条"""
        self.parent.progress.setMaximum(total)
        self.parent.progress.setValue(current)
        self.parent.progress.setFormat(f"处理中: {current}/{total} (%p%)")

    def on_thread_error(self, error_msg):
        msg = CustomMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("错误")
        msg.setText(f"处理过程中发生错误:\n{error_msg}")
        msg.exec_()
        self.parent.progress.setFormat("错误")

    def get_current_settings(self):
        """获取当前数据标签页的设置"""
        return {
            "mode": self.mode_combo.currentText(),
            "input_dir": self.input_line.text(),
            "output_dir": self.output_line.text(),
            "train_txt": self.train_txt_line.text(),
            "test_txt": self.test_txt_line.text(),
            "test_ratio": self.ratio_line.text(),
            "suffix": self.suffix_line.text(),
            "size_threshold": self.size_line.text(),
            "count_threshold": self.count_threshold_line.text(),
            "confirm_delete": self.confirm_delete_check.isChecked(),
            "path1": self.input1_line.text(),
            "path2": self.input2_line.text(),
            "compare_name": self.compare_name_check.isChecked(),
            "compare_size": self.compare_size_check.isChecked(),
            "compare_mtime": self.compare_mtime_check.isChecked(),
            "compare_content": self.compare_content_check.isChecked()
        }

    def apply_settings(self, settings):
        """应用设置到数据标签页"""
        self.mode_combo.setCurrentText(settings.get("mode", ""))
        self.input_line.setText(settings.get("input_dir", ""))
        self.output_line.setText(settings.get("output_dir", ""))
        self.train_txt_line.setText(settings.get("train_txt", ""))
        self.test_txt_line.setText(settings.get("test_txt", ""))
        self.ratio_line.setText(settings.get("test_ratio", "0.2"))
        self.suffix_line.setText(settings.get("suffix", ".jpg"))
        self.size_line.setText(settings.get("size_threshold", "5"))
        self.count_threshold_line.setText(settings.get("count_threshold", "5"))
        self.confirm_delete_check.setChecked(settings.get("confirm_delete", False))
        self.input1_line.setText(settings.get("path1", ""))
        self.input2_line.setText(settings.get("path2", ""))
        self.compare_name_check.setChecked(settings.get("compare_name", True))
        self.compare_size_check.setChecked(settings.get("compare_size", True))
        self.compare_mtime_check.setChecked(settings.get("compare_mtime", False))
        self.compare_content_check.setChecked(settings.get("compare_content", False))
        self.toggle_mode_inputs()



# 添加新的 SystemToolsTab 类：
class SystemToolsTab(QWidget):
    """系统工具标签页"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.monitor = None
        self.monitor_thread = None
        self.log_analyzer_thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 功能选择
        self.tab_widget = QTabWidget()

        # 日志分析标签
        self.log_tab = QWidget()
        self.init_log_ui()
        self.tab_widget.addTab(self.log_tab, "日志分析")

        # 资源监控标签
        self.monitor_tab = QWidget()
        self.init_monitor_ui()
        self.tab_widget.addTab(self.monitor_tab, "资源监控")

        layout.addWidget(self.tab_widget)
        self.setLayout(layout)

    def init_log_ui(self):
        """初始化日志分析UI"""
        layout = QVBoxLayout()

        # 日志文件选择
        file_group = QGroupBox("日志文件选择")
        file_layout = QVBoxLayout()

        self.log_file_radio = QRadioButton("单个日志文件")
        self.log_dir_radio = QRadioButton("日志目录")
        self.log_file_radio.setChecked(True)

        radio_layout = QHBoxLayout()
        radio_layout.addWidget(self.log_file_radio)
        radio_layout.addWidget(self.log_dir_radio)
        file_layout.addLayout(radio_layout)

        self.log_path_layout = QHBoxLayout()
        self.log_path_edit = QLineEdit()
        self.log_browse_btn = QPushButton("浏览...")
        self.log_browse_btn.clicked.connect(self.select_log_path)
        self.log_path_layout.addWidget(self.log_path_edit)
        self.log_path_layout.addWidget(self.log_browse_btn)
        file_layout.addLayout(self.log_path_layout)

        file_group.setLayout(file_layout)
        layout.addWidget(file_group)

        # 时间范围选择
        time_group = QGroupBox("时间范围（可选）")
        time_layout = QHBoxLayout()

        self.start_time_label = QLabel("开始时间:")
        self.start_time_edit = QDateTimeEdit()
        self.start_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.start_time_edit.setCalendarPopup(True)

        self.end_time_label = QLabel("结束时间:")
        self.end_time_edit = QDateTimeEdit()
        self.end_time_edit.setDisplayFormat("yyyy-MM-dd HH:mm:ss")
        self.end_time_edit.setCalendarPopup(True)
        self.end_time_edit.setDateTime(self.end_time_edit.dateTime().currentDateTime())

        time_layout.addWidget(self.start_time_label)
        time_layout.addWidget(self.start_time_edit)
        time_layout.addWidget(self.end_time_label)
        time_layout.addWidget(self.end_time_edit)
        time_group.setLayout(time_layout)
        layout.addWidget(time_group)

        # 输出设置
        output_group = QGroupBox("输出设置")
        output_layout = QHBoxLayout()

        self.output_dir_edit = QLineEdit()
        self.output_browse_btn = QPushButton("浏览...")
        self.output_browse_btn.clicked.connect(self.select_output_dir)
        output_layout.addWidget(self.output_dir_edit)
        output_layout.addWidget(self.output_browse_btn)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 分析按钮
        self.analyze_btn = QPushButton("开始分析")
        self.analyze_btn.clicked.connect(self.analyze_logs)
        self.help_btn = QPushButton("帮助")
        self.help_btn.clicked.connect(self.show_log_help)

        btn_layout = QHBoxLayout()
        btn_layout.addWidget(self.analyze_btn)
        btn_layout.addWidget(self.help_btn)
        layout.addLayout(btn_layout)

        # 结果显示
        self.log_result_text = QTextEdit()
        self.log_result_text.setReadOnly(True)
        layout.addWidget(self.log_result_text)

        self.log_tab.setLayout(layout)

    def init_monitor_ui(self):
        """初始化资源监控UI"""
        layout = QVBoxLayout()

        # 监控控制
        control_group = QGroupBox("监控控制")
        control_layout = QHBoxLayout()

        self.start_monitor_btn = QPushButton("开始监控")
        self.start_monitor_btn.clicked.connect(self.start_monitoring)
        self.stop_monitor_btn = QPushButton("停止监控")
        self.stop_monitor_btn.clicked.connect(self.stop_monitoring)
        self.stop_monitor_btn.setEnabled(False)

        self.refresh_label = QLabel("刷新间隔(秒):")
        self.refresh_spin = QSpinBox()
        self.refresh_spin.setRange(1, 60)
        self.refresh_spin.setValue(2)

        control_layout.addWidget(self.start_monitor_btn)
        control_layout.addWidget(self.stop_monitor_btn)
        control_layout.addWidget(self.refresh_label)
        control_layout.addWidget(self.refresh_spin)
        control_group.setLayout(control_layout)
        layout.addWidget(control_group)

        # 资源显示
        stats_group = QGroupBox("资源状态")
        stats_layout = QGridLayout()

        # CPU
        self.cpu_label = QLabel("CPU使用率:")
        self.cpu_value = QLabel("0%")
        self.cpu_progress = QProgressBar()
        self.cpu_progress.setRange(0, 100)

        # 内存
        self.mem_label = QLabel("内存使用:")
        self.mem_value = QLabel("0 GB / 0 GB (0%)")
        self.mem_progress = QProgressBar()
        self.mem_progress.setRange(0, 100)

        # 磁盘
        self.disk_label = QLabel("磁盘使用:")
        self.disk_value = QLabel("0 GB / 0 GB (0%)")
        self.disk_progress = QProgressBar()
        self.disk_progress.setRange(0, 100)

        # 网络
        self.net_label = QLabel("网络流量:")
        self.net_value = QLabel("上传: 0 KB/s  下载: 0 KB/s")

        stats_layout.addWidget(self.cpu_label, 0, 0)
        stats_layout.addWidget(self.cpu_value, 0, 1)
        stats_layout.addWidget(self.cpu_progress, 0, 2)

        stats_layout.addWidget(self.mem_label, 1, 0)
        stats_layout.addWidget(self.mem_value, 1, 1)
        stats_layout.addWidget(self.mem_progress, 1, 2)

        stats_layout.addWidget(self.disk_label, 2, 0)
        stats_layout.addWidget(self.disk_value, 2, 1)
        stats_layout.addWidget(self.disk_progress, 2, 2)

        stats_layout.addWidget(self.net_label, 3, 0, 1, 3)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # 图表区域
        self.chart_label = QLabel()
        self.chart_label.setAlignment(Qt.AlignCenter)
        self.chart_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.chart_label)

        # 帮助按钮
        self.monitor_help_btn = QPushButton("帮助")
        self.monitor_help_btn.clicked.connect(self.show_monitor_help)
        layout.addWidget(self.monitor_help_btn, alignment=Qt.AlignRight)

        self.monitor_tab.setLayout(layout)

    def select_log_path(self):
        """选择日志文件或目录"""
        if self.log_file_radio.isChecked():
            path, _ = QFileDialog.getOpenFileName(self, "选择日志文件", "", "日志文件 (*.log *.txt)")
        else:
            path = QFileDialog.getExistingDirectory(self, "选择日志目录")

        if path:
            self.log_path_edit.setText(path)

    def select_output_dir(self):
        """选择输出目录"""
        path = QFileDialog.getExistingDirectory(self, "选择输出目录")
        if path:
            self.output_dir_edit.setText(path)

    def analyze_logs(self):
        """分析日志"""
        log_path = self.log_path_edit.text().strip()
        if not log_path:
            QMessageBox.warning(self, "警告", "请选择日志文件或目录")
            return

        output_dir = self.output_dir_edit.text().strip()
        if not output_dir:
            QMessageBox.warning(self, "警告", "请选择输出目录")
            return

        # 获取时间范围
        start_time = self.start_time_edit.dateTime().toPyDateTime()
        end_time = self.end_time_edit.dateTime().toPyDateTime()
        time_range = (start_time, end_time) if start_time < end_time else None

        self.parent.progress.setValue(0)
        self.parent.progress.setFormat("分析中...")
        self.analyze_btn.setEnabled(False)

        def _analyze():
            from system_tools import LogAnalyzer
            try:
                result = LogAnalyzer.analyze_log_file(log_path, time_range)
                report_path = LogAnalyzer.generate_report(result, output_dir)
                return report_path, result
            except Exception as e:
                return str(e)

        self.log_analyzer_thread = WorkerThread(_analyze)
        self.log_analyzer_thread.finished.connect(self.on_log_analysis_complete)
        self.log_analyzer_thread.error.connect(self.on_log_analysis_error)
        self.log_analyzer_thread.start()

    def on_log_analysis_complete(self, result):
        """日志分析完成"""
        self.analyze_btn.setEnabled(True)
        self.parent.progress.setFormat("完成")

        if isinstance(result, tuple):
            report_path, analysis_result = result
            self.log_result_text.clear()

            # 显示简要结果
            text = f"分析完成！报告已保存到:\n{report_path}\n\n"
            text += f"总错误数: {analysis_result['total_errors']}\n"
            text += f"总警告数: {analysis_result['total_warnings']}\n\n"

            text += "=== 错误统计 ===\n"
            for error, count in analysis_result['error_stats'].items():
                text += f"{error}: {count}次\n"

            text += "\n=== 最近错误 ===\n"
            for error in analysis_result['error_details'][-5:]:
                text += f"{error['timestamp']}: {error['message']}\n"

            self.log_result_text.setPlainText(text)

            # 显示图表
            chart_path = os.path.join(os.path.dirname(report_path), "hourly_distribution.png")
            if os.path.exists(chart_path):
                pixmap = QPixmap(chart_path)
                self.log_result_text.document().addResource(
                    QTextDocument.ImageResource,
                    QUrl("hourly_distribution.png"),
                    pixmap
                )
                self.log_result_text.append("\n错误时间分布:")
                self.log_result_text.append('<img src="hourly_distribution.png">')
        else:
            QMessageBox.critical(self, "错误", f"分析失败: {result}")

    def on_log_analysis_error(self, error_msg):
        """日志分析错误"""
        self.analyze_btn.setEnabled(True)
        self.parent.progress.setFormat("错误")
        QMessageBox.critical(self, "错误", f"分析过程中发生错误:\n{error_msg}")

    def start_monitoring(self):
        """开始资源监控"""
        try:
            import psutil
        except ImportError:
            QMessageBox.critical(self, "错误", "需要安装psutil库: pip install psutil")
            return

        self.monitor = SystemMonitor(update_interval=self.refresh_spin.value())
        self.monitor.start_monitoring()

        self.start_monitor_btn.setEnabled(False)
        self.stop_monitor_btn.setEnabled(True)

        # 创建监控线程
        self.monitor_thread = MonitorThread(self.monitor)
        self.monitor_thread.update_signal.connect(self.update_monitor_ui)
        self.monitor_thread.start()

    def stop_monitoring(self):
        """停止资源监控"""
        if self.monitor_thread:
            self.monitor_thread.stop()
            self.monitor_thread.wait()

        if self.monitor:
            self.monitor.stop_monitoring()

        self.start_monitor_btn.setEnabled(True)
        self.stop_monitor_btn.setEnabled(False)

    def update_monitor_ui(self, stats):
        """更新监控UI"""
        # CPU
        cpu_percent = stats['cpu']['total']
        self.cpu_value.setText(f"{cpu_percent}%")
        self.cpu_progress.setValue(cpu_percent)

        # 内存
        mem = stats['memory']
        mem_used_gb = mem['used'] / (1024 ** 3)
        mem_total_gb = mem['total'] / (1024 ** 3)
        self.mem_value.setText(f"{mem_used_gb:.1f} GB / {mem_total_gb:.1f} GB ({mem['percent']}%)")
        self.mem_progress.setValue(mem['percent'])

        # 磁盘
        disk = stats['disk']
        disk_used_gb = disk['used'] / (1024 ** 3)
        disk_total_gb = disk['total'] / (1024 ** 3)
        self.disk_value.setText(f"{disk_used_gb:.1f} GB / {disk_total_gb:.1f} GB ({disk['percent']}%)")
        self.disk_progress.setValue(disk['percent'])

        # 网络
        net = stats['network']
        upload_speed = net['bytes_sent'] / 1024  # KB/s
        download_speed = net['bytes_recv'] / 1024  # KB/s
        self.net_value.setText(f"上传: {upload_speed:.1f} KB/s  下载: {download_speed:.1f} KB/s")

    def show_log_help(self):
        """显示日志分析帮助"""
        from help_functions import get_system_help
        help_text = get_system_help('日志分析工具')
        dialog = HelpDialog('日志分析工具', help_text, self)
        dialog.exec_()

    def show_monitor_help(self):
        """显示资源监控帮助"""
        from help_functions import get_system_help
        help_text = get_system_help('系统资源监控')
        dialog = HelpDialog('系统资源监控', help_text, self)
        dialog.exec_()


class MonitorThread(QThread):
    """资源监控线程"""
    update_signal = pyqtSignal(dict)

    def __init__(self, monitor):
        super().__init__()
        self.monitor = monitor
        self._running = True

    def run(self):
        while self._running:
            stats = self.monitor.get_system_stats()
            self.update_signal.emit(stats)
            time.sleep(self.monitor.update_interval)

    def stop(self):
        self._running = False
        self.quit()
class GraphProcessingTab(QWidget):
    """图数据处理功能标签页"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.thread = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 功能选择
        mode_layout = QHBoxLayout()
        self.mode_label = QLabel("选择功能:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "选择单个文件加载图结构",
            "统计路径下最大点/边数量的文件",
            "统计路径下每个类别的信息"
        ])
        self.mode_combo.currentIndexChanged.connect(self.toggle_mode_inputs)
        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # 路径设置组
        path_group = QGroupBox("路径设置")
        path_layout = QVBoxLayout()

        # 输入路径
        input_layout = QHBoxLayout()
        self.input_label = QLabel('输入路径:')
        self.input_line = QLineEdit()
        self.input_btn = QPushButton('浏览...')
        self.input_btn.clicked.connect(self.select_input_dir)
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(self.input_line)
        input_layout.addWidget(self.input_btn)
        path_layout.addLayout(input_layout)

        # 输出路径
        self.output_layout = QHBoxLayout()
        self.output_label = QLabel('输出目录:')
        self.output_line = QLineEdit()
        self.output_btn = QPushButton('浏览...')
        self.output_btn.clicked.connect(self.select_output_dir)
        self.output_layout.addWidget(self.output_label)
        self.output_layout.addWidget(self.output_line)
        self.output_layout.addWidget(self.output_btn)
        path_layout.addLayout(self.output_layout)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # 输出区域
        output_group = QGroupBox("输出结果")
        output_layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.text_edit)

        output_layout.addWidget(scroll_area)
        output_group.setLayout(output_layout)
        layout.addWidget(output_group)

        # 按钮布局
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton('执行操作')
        self.run_btn.clicked.connect(self.run_tool)
        self.help_btn = QPushButton('帮助')
        self.help_btn.clicked.connect(self.show_help)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.help_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)
        self.toggle_mode_inputs()

    def show_help(self):
        """显示当前功能的帮助信息"""
        from help_functions import get_graph_processing_help
        mode = self.mode_combo.currentText()
        help_text = get_graph_processing_help(mode)
        dialog = HelpDialog(mode, help_text, self)
        dialog.exec_()

    def toggle_mode_inputs(self):
        mode = self.mode_combo.currentText()
        has_output = mode == "统计路径下每个类别的信息"

        self.output_label.setVisible(has_output)
        self.output_line.setVisible(has_output)
        self.output_btn.setVisible(has_output)

    def select_input_dir(self):
        if self.mode_combo.currentText() == "选择单个文件加载图结构":
            file_path, _ = QFileDialog.getOpenFileName(self, "选择 .bin 文件", "", "BIN Files (*.bin)")
            if file_path:
                self.input_line.setText(file_path)
        else:
            dir_path = QFileDialog.getExistingDirectory(self, "选择包含 .bin 文件的目录")
            if dir_path:
                self.input_line.setText(dir_path)

    def select_output_dir(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "选择保存路径和文件名", "统计结果.xlsx", "Excel 文件 (*.xlsx)"
        )
        if file_path:
            if not file_path.lower().endswith('.xlsx'):
                file_path += '.xlsx'
            self.output_line.setText(file_path)

    def run_tool(self):
        mode = self.mode_combo.currentText()
        input_path = self.input_line.text().strip()

        if not input_path:
            QMessageBox.warning(self, '警告', '请输入输入路径！')
            return
        if not os.path.exists(input_path):
            QMessageBox.warning(self, '警告', '输入路径不存在！')
            return

        self.parent.progress.setValue(0)
        self.parent.progress.setFormat("处理中...")

        if mode == "选择单个文件加载图结构":
            self.load_single_file(input_path)
        elif mode == "统计路径下最大点/边数量的文件":
            self.analyze_max(input_path)
        elif mode == "统计路径下每个类别的信息":
            self.analyze_directory_statistics(input_path)

    def load_single_file(self, file_path):
        def _load():
            return init(file_path)

        self.run_in_thread(_load, self.on_load_complete, self.on_load_error)

    def on_load_complete(self, graph):
        file_path = self.input_line.text()
        info = f"📄 文件路径: {file_path}\n📁 文件名: {Path(file_path).name}"
        info += f"\n🟢 节点数量: {graph.number_of_nodes()}"
        info += f"\n➖ 边数量: {graph.number_of_edges()}"
        if "x" in graph.ndata:
            info += f"\n📐 节点特征维度: {tuple(graph.ndata['x'].shape)}"
        if "x" in graph.edata:
            info += f"\n📏 边特征维度: {tuple(graph.edata['x'].shape)}"
        self.text_edit.setText(info)
        self.parent.progress.setFormat("完成")

    def on_load_error(self, error_msg):
        self.text_edit.setText(f"❌ 加载失败: {error_msg}")
        self.parent.progress.setFormat("错误")

    def analyze_max(self, dir_path):
        def _analyze():
            return StatisticsAnalyzer.analyze_max_nodes_edges(Path(dir_path))

        self.run_in_thread(_analyze, self.on_analyze_max_complete, self.on_analyze_error)

    def on_analyze_max_complete(self, result):
        max_nodes_info, max_edges_info = result
        info = f"📌 节点最多的文件:\n{max_nodes_info}\n\n"
        info += f"📌 边最多的文件:\n{max_edges_info}"
        self.text_edit.setText(info)
        self.parent.progress.setFormat("完成")

    def analyze_directory_statistics(self, input_dir):
        output_path = self.output_line.text().strip()
        if not output_path:
            QMessageBox.warning(self, "警告", "请选择保存路径！")
            return

        def _analyze():
            stats = StatisticsAnalyzer.analyze_category_statistics(Path(input_dir))
            if not stats:
                return None
            success = StatisticsAnalyzer.save_statistics_to_excel(stats, Path(output_path))
            return success

        self.run_in_thread(_analyze, self.on_analyze_stats_complete, self.on_analyze_error)

    def on_analyze_stats_complete(self, success):
        if success is None:
            self.text_edit.setText("⚠️ 未找到有效类别或文件")
            self.parent.progress.setFormat("完成")
            return

        if success:
            # 使用CustomMessageBox替代QMessageBox
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("成功")
            msg.setText(f"统计结果已保存到:\n{self.output_line.text()}")
            msg.exec_()
            self.text_edit.setText(f"统计结果成功保存到 {self.output_line.text()}")
        else:
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Critical)
            msg.setWindowTitle("错误")
            msg.setText("保存失败")
            msg.exec_()
            self.text_edit.setText("保存失败")
        self.parent.progress.setFormat("完成")


    def on_analyze_error(self, error_msg):
        self.text_edit.setText(f"❌ 分析失败: {error_msg}")
        self.parent.progress.setFormat("错误")

    def run_in_thread(self, func, success_callback, error_callback=None):
        """在子线程中运行函数"""
        if self.thread and self.thread.isRunning():
            self.thread.stop()

        self.thread = WorkerThread(func)
        self.thread.finished.connect(success_callback)
        if error_callback:
            self.thread.error.connect(error_callback)
        else:
            self.thread.error.connect(self.on_thread_error)
        self.thread.progress.connect(self.update_progress)
        self.thread.start()

    def update_progress(self, current, total):
        """更新进度条"""
        self.parent.progress.setMaximum(total)
        self.parent.progress.setValue(current)
        self.parent.progress.setFormat(f"处理中: {current}/{total} (%p%)")

    def on_thread_error(self, error_msg):
        QMessageBox.critical(self, "错误", f"处理过程中发生错误:\n{error_msg}")
        self.parent.progress.setFormat("错误")

    def get_current_settings(self):
        """获取当前图数据标签页的设置"""
        return {
            "mode": self.mode_combo.currentText(),
            "input_path": self.input_line.text(),
            "output_path": self.output_line.text()
        }

    def apply_settings(self, settings):
        """应用设置到图数据标签页"""
        self.mode_combo.setCurrentText(settings.get("mode", ""))
        self.input_line.setText(settings.get("input_path", ""))
        self.output_line.setText(settings.get("output_path", ""))
        self.toggle_mode_inputs()


class ModelProcessingTab(QWidget):
    """3D模型处理功能标签页"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.thread = None
        self.failed_files = set()
        self.process_pool = None
        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.check_memory_usage)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # 功能选择
        mode_layout = QHBoxLayout()
        self.mode_label = QLabel("选择功能:")
        self.mode_combo = QComboBox()
        self.mode_combo.addItems([
            "STEP转STL",
            "STL转点云",
            "STL转多视图",
            "STEP转DGL图结构"
        ])
        self.mode_combo.currentIndexChanged.connect(self.toggle_mode_inputs)
        mode_layout.addWidget(self.mode_label)
        mode_layout.addWidget(self.mode_combo)
        layout.addLayout(mode_layout)

        # 路径设置组
        path_group = QGroupBox("路径设置")
        path_layout = QVBoxLayout()
        path_layout.setSpacing(10)

        # 输入路径
        self.input_layout = QHBoxLayout()
        self.input_label = QLabel('输入目录:')
        self.input_line = QLineEdit()
        self.input_btn = QPushButton('浏览...')
        self.input_btn.clicked.connect(self.select_input_dir)
        self.input_layout.addWidget(self.input_label)
        self.input_layout.addWidget(self.input_line)
        self.input_layout.addWidget(self.input_btn)
        path_layout.addLayout(self.input_layout)

        # 输出路径
        self.output_layout = QHBoxLayout()
        self.output_label = QLabel('输出目录:')
        self.output_line = QLineEdit()
        self.output_btn = QPushButton('浏览...')
        self.output_btn.clicked.connect(self.select_output_dir)
        self.output_layout.addWidget(self.output_label)
        self.output_layout.addWidget(self.output_line)
        self.output_layout.addWidget(self.output_btn)
        path_layout.addLayout(self.output_layout)

        path_group.setLayout(path_layout)
        layout.addWidget(path_group)

        # 参数设置组
        self.param_group = QGroupBox("参数设置")
        self.param_layout = QVBoxLayout()
        self.param_layout.setSpacing(10)

        # 网格质量
        self.quality_layout = QHBoxLayout()
        self.quality_label = QLabel('网格质量 (1-10):')
        self.quality_spin = QSpinBox()
        self.quality_spin.setRange(1, 10)
        self.quality_spin.setValue(5)
        self.quality_layout.addWidget(self.quality_label)
        self.quality_layout.addWidget(self.quality_spin)
        self.param_layout.addLayout(self.quality_layout)

        # 点云采样
        self.points_layout = QHBoxLayout()
        self.points_label = QLabel('采样点数量:')
        self.points_spin = QSpinBox()
        self.points_spin.setRange(100, 100000)
        self.points_spin.setValue(2048)
        self.points_layout.addWidget(self.points_label)
        self.points_layout.addWidget(self.points_spin)
        self.param_layout.addLayout(self.points_layout)

        self.normals_check = QCheckBox('包含法线数据')
        self.param_layout.addWidget(self.normals_check)

        # 多视图渲染
        self.views_layout = QHBoxLayout()
        self.views_label = QLabel('视图数量:')
        self.views_spin = QSpinBox()
        self.views_spin.setRange(1, 36)
        self.views_spin.setValue(12)
        self.views_layout.addWidget(self.views_label)
        self.views_layout.addWidget(self.views_spin)
        self.param_layout.addLayout(self.views_layout)

        self.size_layout = QHBoxLayout()
        self.size_label = QLabel('图像尺寸:')
        self.size_spin = QSpinBox()
        self.size_spin.setRange(64, 1024)
        self.size_spin.setValue(224)
        self.size_layout.addWidget(self.size_label)
        self.size_layout.addWidget(self.size_spin)
        self.param_layout.addLayout(self.size_layout)

        # STEP转DGL参数
        self.curv_u_layout = QHBoxLayout()
        self.curv_u_label = QLabel('曲线U采样数:')
        self.curv_u_spin = QSpinBox()
        self.curv_u_spin.setRange(1, 100)
        self.curv_u_spin.setValue(10)
        self.curv_u_layout.addWidget(self.curv_u_label)
        self.curv_u_layout.addWidget(self.curv_u_spin)
        self.param_layout.addLayout(self.curv_u_layout)

        self.surf_u_layout = QHBoxLayout()
        self.surf_u_label = QLabel('曲面U采样数:')
        self.surf_u_spin = QSpinBox()
        self.surf_u_spin.setRange(1, 100)
        self.surf_u_spin.setValue(10)
        self.surf_u_layout.addWidget(self.surf_u_label)
        self.surf_u_layout.addWidget(self.surf_u_spin)
        self.param_layout.addLayout(self.surf_u_layout)

        self.surf_v_layout = QHBoxLayout()
        self.surf_v_label = QLabel('曲面V采样数:')
        self.surf_v_spin = QSpinBox()
        self.surf_v_spin.setRange(1, 100)
        self.surf_v_spin.setValue(10)
        self.surf_v_layout.addWidget(self.surf_v_label)
        self.surf_v_layout.addWidget(self.surf_v_spin)
        self.param_layout.addLayout(self.surf_v_layout)

        self.proc_layout = QHBoxLayout()
        self.proc_label = QLabel('并行进程数:')
        self.proc_spin = QSpinBox()
        self.proc_spin.setRange(1, 64)
        self.proc_spin.setValue(8)
        self.proc_layout.addWidget(self.proc_label)
        self.proc_layout.addWidget(self.proc_spin)
        self.param_layout.addLayout(self.proc_layout)

        # 内存限制设置
        self.mem_layout = QHBoxLayout()
        self.mem_label = QLabel('内存限制(GB):')
        self.mem_spin = QSpinBox()
        self.mem_spin.setRange(1, 32)
        self.mem_spin.setValue(8)
        self.mem_layout.addWidget(self.mem_label)
        self.mem_layout.addWidget(self.mem_spin)
        self.param_layout.addLayout(self.mem_layout)

        self.param_group.setLayout(self.param_layout)
        layout.addWidget(self.param_group)

        # 按钮布局
        btn_layout = QHBoxLayout()
        self.run_btn = QPushButton('开始处理')
        self.run_btn.clicked.connect(self.run_processing)
        self.stop_btn = QPushButton('停止处理')
        self.stop_btn.clicked.connect(self.stop_processing)
        self.stop_btn.setEnabled(False)
        self.help_btn = QPushButton('帮助')
        self.help_btn.clicked.connect(self.show_help)
        btn_layout.addWidget(self.run_btn)
        btn_layout.addWidget(self.stop_btn)
        btn_layout.addWidget(self.help_btn)
        layout.addLayout(btn_layout)

        # 状态标签
        self.status_label = QLabel("就绪")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        self.setLayout(layout)
        self.toggle_mode_inputs()

    def check_system_resources(self):
        """检查系统资源是否充足"""
        try:
            import psutil
            # 检查内存
            mem = psutil.virtual_memory()
            if mem.available < 2 * 1024 * 1024 * 1024:  # 小于2GB可用内存
                return False

            # 检查CPU负载
            if psutil.cpu_percent(interval=1) > 90:  # CPU使用率超过90%
                return False

            return True
        except ImportError:
            return True  # 如果没有psutil，假设资源充足

    def select_input_dir(self):
        """选择输入目录"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择输入目录')
        if dir_path:
            self.input_line.setText(dir_path)

    def select_output_dir(self):
        """选择输出目录"""
        dir_path = QFileDialog.getExistingDirectory(self, '选择输出目录')
        if dir_path:
            self.output_line.setText(dir_path)

    def show_help(self):
        """显示帮助信息"""
        from help_functions import get_model_processing_help
        mode = self.mode_combo.currentText()
        help_text = get_model_processing_help(mode)
        dialog = HelpDialog(mode, help_text, self)
        dialog.exec_()

    def toggle_mode_inputs(self):
        """根据选择的模式切换显示不同的参数控件"""
        mode = self.mode_combo.currentText()

        # 显示/隐藏参数控件
        self.quality_label.setVisible(mode == "STEP转STL")
        self.quality_spin.setVisible(mode == "STEP转STL")

        self.points_label.setVisible(mode == "STL转点云")
        self.points_spin.setVisible(mode == "STL转点云")
        self.normals_check.setVisible(mode == "STL转点云")

        self.views_label.setVisible(mode == "STL转多视图")
        self.views_spin.setVisible(mode == "STL转多视图")
        self.size_label.setVisible(mode == "STL转多视图")
        self.size_spin.setVisible(mode == "STL转多视图")

        self.curv_u_label.setVisible(mode == "STEP转DGL图结构")
        self.curv_u_spin.setVisible(mode == "STEP转DGL图结构")
        self.surf_u_label.setVisible(mode == "STEP转DGL图结构")
        self.surf_u_spin.setVisible(mode == "STEP转DGL图结构")
        self.surf_v_label.setVisible(mode == "STEP转DGL图结构")
        self.surf_v_spin.setVisible(mode == "STEP转DGL图结构")
        self.proc_label.setVisible(mode == "STEP转DGL图结构")
        self.proc_spin.setVisible(mode == "STEP转DGL图结构")
        self.mem_label.setVisible(mode == "STEP转DGL图结构")
        self.mem_spin.setVisible(mode == "STEP转DGL图结构")

    def run_processing(self):
        """执行处理操作"""
        mode = self.mode_combo.currentText()
        input_dir = self.input_line.text().strip()
        output_dir = self.output_line.text().strip()

        if mode == "STEP转DGL图结构" and not self.check_system_resources():
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("资源警告")
            msg.setText("系统资源不足，可能无法完成处理。建议关闭其他程序或减少并行进程数。")
            msg.exec_()
            return

        if not input_dir or not output_dir:
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("警告")
            msg.setText("请选择输入和输出目录")
            msg.exec_()
            return

        if not os.path.exists(input_dir):
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("警告")
            msg.setText("输入目录不存在")
            msg.exec_()
            return

        os.makedirs(output_dir, exist_ok=True)
        self.failed_files.clear()
        self.parent.progress.setValue(0)
        self.parent.progress.setFormat("处理中...")
        self.run_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.status_label.setText("处理中...")

        if mode == "STEP转STL":
            self.process_files(input_dir, output_dir, (".stp", ".step"), self.process_step_to_stl)
        elif mode == "STL转点云":
            self.process_files(input_dir, output_dir, ".stl", self.process_stl_to_pointcloud)
        elif mode == "STL转多视图":
            self.process_files(input_dir, output_dir, ".stl", self.process_multiview)
        elif mode == "STEP转DGL图结构":
            # 开始内存监控
            self.memory_timer.start(5000)  # 每5秒检查一次内存
            self.process_step_to_dgl(input_dir, output_dir)

    def stop_processing(self):
        """停止当前处理任务"""
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread.quit()
            self.thread.wait(1000)

        if self.process_pool:
            try:
                self.process_pool.terminate()
                self.process_pool.join()
            except Exception as e:
                print(f"停止进程池时出错: {e}")

        self.memory_timer.stop()
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.status_label.setText("已停止")
        self.parent.progress.setFormat("已停止")

    def check_memory_usage(self):
        """检查内存使用情况"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            mem_usage = process.memory_info().rss / (1024 ** 3)  # GB
            mem_limit = self.mem_spin.value()

            if mem_usage > mem_limit:
                self.status_label.setText(f"内存警告: {mem_usage:.2f}GB/{mem_limit}GB")
                QApplication.processEvents()  # 强制更新UI

                # 释放内存
                if self.process_pool:
                    try:
                        self.process_pool.terminate()
                        self.process_pool.join()
                    except Exception as e:
                        print(f"释放内存时出错: {e}")

                # 重新启动处理
                if self.mode_combo.currentText() == "STEP转DGL图结构":
                    input_dir = self.input_line.text().strip()
                    output_dir = self.output_line.text().strip()
                    self.process_step_to_dgl(input_dir, output_dir)
        except ImportError:
            pass
        except Exception as e:
            print(f"检查内存时出错: {e}")

    def process_step_to_dgl(self, input_dir, output_dir):
        """处理STEP到DGL图结构转换"""
        curv_u = self.curv_u_spin.value()
        surf_u = self.surf_u_spin.value()
        surf_v = self.surf_v_spin.value()
        num_proc = min(self.proc_spin.value(), os.cpu_count())

        # 限制最大进程数，避免资源耗尽
        num_proc = min(num_proc, 4)  # 限制为4个进程

        # 减少内存限制检查频率
        self.memory_timer.setInterval(10000)  # 10秒检查一次

        def _convert(progress_callback=None):  # 添加progress_callback参数
            try:
                from model_processor import ModelProcessor
                self.process_pool = ModelProcessor.create_process_pool(num_proc)

                result = ModelProcessor.convert_step_to_dgl(
                    input_dir, output_dir,
                    curv_u_samples=curv_u,
                    surf_u_samples=surf_u,
                    surf_v_samples=surf_v,
                    num_processes=num_proc,
                    progress_callback=progress_callback  # 传递回调函数
                )
                return result
            except Exception as e:
                raise e
            finally:
                if self.process_pool:
                    self.process_pool.terminate()
                    self.process_pool.join()
                    self.process_pool = None

        self.run_in_thread(_convert, self.on_dgl_conversion_complete, self.on_dgl_conversion_error)

    def on_dgl_conversion_complete(self, result):
        """DGL转换完成回调"""
        self.memory_timer.stop()
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        if result is None:  # 用户取消
            self.status_label.setText("已取消")
            return

        failed_count, failed_files = result

        if failed_count > 0:
            fail_file = os.path.join(self.output_line.text(), "failed_files.log")
            with open(fail_file, "w", encoding="utf-8") as f:
                f.write("失败文件列表:\n")
                for file, error in failed_files:
                    f.write(f"{file}: {error}\n")

            error_dialog = CustomMessageBox(self)
            error_dialog.setWindowTitle("转换结果")
            error_dialog.setIcon(QMessageBox.Information)
            error_dialog.setText(f"{failed_count}个文件转换失败，详细错误已保存到:\n{fail_file}")
            error_dialog.setDetailedText("\n".join([f"{f[0]}: {f[1]}" for f in failed_files]))
            error_dialog.exec_()
            self.status_label.setText(f"完成(部分失败:{failed_count})")
        else:
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("完成")
            msg.setText("所有STEP文件已成功转换为DGL图结构!")
            msg.exec_()
            self.status_label.setText("完成")
        self.parent.progress.setFormat("完成")

    def on_dgl_conversion_error(self, error_msg):
        """DGL转换错误回调"""
        self.memory_timer.stop()
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        error_dialog = CustomMessageBox(self)
        error_dialog.setWindowTitle("严重错误")
        error_dialog.setIcon(QMessageBox.Critical)
        error_dialog.setText("转换过程中发生严重错误")

        if "Can't pickle" in error_msg:
            error_msg += "\n\n建议：尝试减少并行进程数或重启程序"

        error_dialog.setDetailedText(
            f"错误详情:\n{error_msg}\n\n"
            f"{traceback.format_exc()}"
        )
        error_dialog.exec_()
        self.parent.progress.setFormat("错误")
        self.status_label.setText("错误")

    def process_files(self, input_dir, output_dir, extensions, process_func):
        """处理文件并更新进度"""
        from pathlib import Path

        # 收集所有匹配文件
        files = []
        for root, _, filenames in os.walk(input_dir):
            for filename in filenames:
                if isinstance(extensions, tuple):
                    if filename.lower().endswith(extensions):
                        files.append(Path(root) / filename)
                else:
                    if filename.lower().endswith(extensions):
                        files.append(Path(root) / filename)

        total = len(files)
        if total == 0:
            ext_str = ",".join(extensions) if isinstance(extensions, tuple) else extensions
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Warning)
            msg.setWindowTitle("警告")
            msg.setText(f"未找到{ext_str}文件")
            msg.exec_()
            self.run_btn.setEnabled(True)
            self.stop_btn.setEnabled(False)
            return

        def _process():
            processed = 0
            for i, file in enumerate(files):
                if not getattr(self.thread, '_is_running', True):
                    return None

                relative_path = file.relative_to(input_dir).parent
                output_path = Path(output_dir) / relative_path
                output_path.mkdir(parents=True, exist_ok=True)

                try:
                    if process_func(str(file), str(output_path)):
                        processed += 1
                    else:
                        self.failed_files.add(file.name)
                except Exception as e:
                    self.failed_files.add(file.name)
                    print(f"处理失败 {file}: {str(e)}")

                self.thread.progress.emit(i + 1, total)
            return processed, total

        if self.thread and self.thread.isRunning():
            self.thread.stop()

        self.thread = WorkerThread(_process)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.on_files_processed)
        self.thread.error.connect(self.on_files_process_error)
        self.thread.start()

    def on_files_processed(self, result):
        """文件处理完成回调"""
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        if result is None:  # 用户取消
            self.status_label.setText("已取消")
            return

        processed, total = result
        self.show_results(processed, total)
        self.parent.progress.setFormat("完成")
        self.status_label.setText("完成")

    def on_files_process_error(self, error_msg):
        """文件处理错误回调"""
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        msg = CustomMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("错误")
        msg.setText(f"处理过程中发生错误:\n{error_msg}")
        msg.exec_()
        self.parent.progress.setFormat("错误")
        self.status_label.setText("错误")

    def run_in_thread(self, func, success_callback, error_callback=None):
        """在子线程中运行函数"""
        if self.thread and self.thread.isRunning():
            self.thread.stop()

        self.thread = WorkerThread(func)
        self.thread.finished.connect(success_callback)
        if error_callback:
            self.thread.error.connect(error_callback)
        else:
            self.thread.error.connect(self.on_thread_error)
        self.thread.progress.connect(self.update_progress)
        self.thread.start()

    def update_progress(self, current, total):
        """更新进度条"""
        self.parent.progress.setMaximum(total)
        self.parent.progress.setValue(current)
        self.parent.progress.setFormat(f"处理中: {current}/{total} (%p%)")

    def on_thread_error(self, error_msg):
        """线程错误处理"""
        self.run_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)

        msg = CustomMessageBox(self)
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("错误")
        msg.setText(f"处理过程中发生错误:\n{error_msg}")
        msg.exec_()
        self.parent.progress.setFormat("错误")
        self.status_label.setText("错误")

    def process_step_to_stl(self, input_file, output_dir):
        """处理STEP到STL转换"""
        from model_processor import ModelProcessor
        quality = self.quality_spin.value()
        return ModelProcessor.convert_step_to_stl(input_file, output_dir, quality)

    def process_stl_to_pointcloud(self, input_file, output_dir):
        """处理STL到点云转换"""
        from model_processor import ModelProcessor
        num_points = self.points_spin.value()
        include_normals = self.normals_check.isChecked()
        return ModelProcessor.sample_point_cloud(input_file, output_dir, num_points, include_normals)

    def process_multiview(self, input_file, output_dir):
        """处理多视图渲染"""
        from model_processor import ModelProcessor
        num_views = self.views_spin.value()
        image_size = self.size_spin.value()
        return ModelProcessor.render_multiview(input_file, output_dir, num_views, image_size)

    def show_results(self, processed, total):
        """显示处理结果"""
        if self.failed_files:
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("处理完成")
            msg.setText(f"处理完成! 成功: {processed}/{total}")
            msg.setDetailedText("\n".join(self.failed_files))
            msg.exec_()
        else:
            msg = CustomMessageBox(self)
            msg.setIcon(QMessageBox.Information)
            msg.setWindowTitle("完成")
            msg.setText(f"所有{total}个文件处理成功!")
            msg.exec_()

    def closeEvent(self, event):
        """关闭时清理资源"""
        self.stop_processing()
        super().closeEvent(event)

    def get_current_settings(self):
        """获取当前模型标签页的设置"""
        return {
            "mode": self.mode_combo.currentText(),
            "input_dir": self.input_line.text(),
            "output_dir": self.output_line.text(),
            "quality": self.quality_spin.value(),
            "points": self.points_spin.value(),
            "normals": self.normals_check.isChecked(),
            "views": self.views_spin.value(),
            "size": self.size_spin.value(),
            "curv_u": self.curv_u_spin.value(),
            "surf_u": self.surf_u_spin.value(),
            "surf_v": self.surf_v_spin.value(),
            "processes": self.proc_spin.value(),
            "memory": self.mem_spin.value()
        }

    def apply_settings(self, settings):
        """应用设置到模型标签页"""
        self.mode_combo.setCurrentText(settings.get("mode", ""))
        self.input_line.setText(settings.get("input_dir", ""))
        self.output_line.setText(settings.get("output_dir", ""))
        self.quality_spin.setValue(settings.get("quality", 5))
        self.points_spin.setValue(settings.get("points", 2048))
        self.normals_check.setChecked(settings.get("normals", False))
        self.views_spin.setValue(settings.get("views", 12))
        self.size_spin.setValue(settings.get("size", 224))
        self.curv_u_spin.setValue(settings.get("curv_u", 10))
        self.surf_u_spin.setValue(settings.get("surf_u", 10))
        self.surf_v_spin.setValue(settings.get("surf_v", 10))
        self.proc_spin.setValue(settings.get("processes", 8))
        self.mem_spin.setValue(settings.get("memory", 8))
        self.toggle_mode_inputs()

class HelpDialog(QDialog):
    """帮助信息对话框"""

    def __init__(self, title: str, content: str, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"帮助 - {title}")
        self.setMinimumSize(800, 600)

        layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setHtml(content)
        self.text_edit.setReadOnly(True)

        btn_close = QPushButton("关闭")
        btn_close.clicked.connect(self.close)

        layout.addWidget(self.text_edit)
        layout.addWidget(btn_close, alignment=Qt.AlignRight)

        self.setLayout(layout)

class StatisticsDialog(QDialog):
    """显示统计结果的对话框"""

    def __init__(self, text: str, title: str = '统计结果', parent=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumSize(620, 520)
        self.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QTextEdit {
                background-color: white;
                border: 1px solid #ccc;
                font-family: "Courier New";
                font-size: 12px;
            }
        """)

        layout = QVBoxLayout(self)

        group_box = QGroupBox("统计详情")
        group_layout = QVBoxLayout()

        self.text_edit = QTextEdit()
        self.text_edit.setPlainText(text)
        self.text_edit.setReadOnly(True)
        self.text_edit.setLineWrapMode(QTextEdit.NoWrap)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.text_edit)

        group_layout.addWidget(scroll_area)
        group_box.setLayout(group_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Ok)
        buttons.accepted.connect(self.accept)
        buttons.button(QDialogButtonBox.Save).clicked.connect(self.save_results)

        layout.addWidget(group_box)
        layout.addWidget(buttons)

    def save_results(self):
        save_path, _ = QFileDialog.getSaveFileName(
            self, "保存统计结果", "统计结果.txt", "Text Files (*.txt)"
        )
        if save_path:
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(self.text_edit.toPlainText())
            QMessageBox.information(self, '成功', f'统计结果已保存到:\n{save_path}')