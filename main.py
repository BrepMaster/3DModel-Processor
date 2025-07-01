"""
程序入口模块
"""

import sys
import logging
import json  # 新增导入
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui_window import MainWindow
# 在文件顶部添加：
from system_tools import SystemMonitor, LogAnalyzer
import os
import sys
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ui_window import MainWindow
from system_tools import SystemMonitor, LogAnalyzer
from PyQt5.QtWidgets import (
    QTabWidget, QHBoxLayout, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QWidget, QFileDialog, QMessageBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
# 确保导入必要的可视化库
try:
    import matplotlib
    matplotlib.use('Qt5Agg')  # 设置matplotlib使用Qt5后端
    import vtk
    import open3d
except ImportError as e:
    print(f"可视化依赖库未安装: {str(e)}")
    print("请安装以下库:")
    print("pip install matplotlib vtk open3d")

def setup_logging():
    """
    配置日志记录

    配置日志记录系统，设置日志级别、格式和输出目标。
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),  # 输出到控制台
            logging.FileHandler('application.log', encoding='utf-8')  # 输出到文件
        ]
    )

def main():
    """
    主函数

    初始化应用程序并启动主窗口。
    """
    # 配置日志
    setup_logging()
    logger = logging.getLogger(__name__)

    try:
        # 创建QApplication实例
        app = QApplication(sys.argv)
        logger.info("应用程序启动")

        # 设置全局字体和样式
        app.setStyle('Fusion')
        font = app.font()
        font.setPointSize(10)
        app.setFont(font)
        logger.debug("应用程序样式设置完成")

        # 创建并显示主窗口
        window = MainWindow()
        window.show()
        logger.info("主窗口显示完成")

        # 运行应用程序
        ret = app.exec_()
        logger.info(f"应用程序退出，返回码: {ret}")
        sys.exit(ret)

    except Exception as e:
        # 捕获并记录未处理的异常
        logger.critical(f"应用程序崩溃: {str(e)}", exc_info=True)
        sys.exit(1)

if __name__ == '__main__':
    # 启动应用程序
    main()