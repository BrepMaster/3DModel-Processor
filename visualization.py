"""
可视化模块
包含数据集、图数据和3D模型的可视化功能
"""

import os
import logging
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from mpl_toolkits.mplot3d import Axes3D
from PyQt5.QtWidgets import (QVBoxLayout, QWidget, QHBoxLayout, QTabWidget,
                            QLabel, QLineEdit, QPushButton, QFileDialog,
                            QMessageBox, QVBoxLayout, QSizePolicy)
from PyQt5.QtCore import Qt
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
import vtk
import open3d as o3d
import traceback
from help_functions import get_visualization_help
from PyQt5.QtWidgets import QDialog  # 确保 QDialog 被正确导入

# 设置中文字体
try:
    rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei']  # 指定默认字体
    rcParams['axes.unicode_minus'] = False  # 解决保存图像时负号'-'显示为方块的问题
except:
    print("无法设置中文字体，中文显示可能不正常")

logger = logging.getLogger(__name__)


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

class MatplotlibWidget(QWidget):
    """Matplotlib图形显示部件"""

    def __init__(self, parent=None, width=8, height=6, dpi=100):
        super().__init__(parent)

        # 确保使用支持中文的字体
        plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'WenQuanYi Zen Hei']
        plt.rcParams['axes.unicode_minus'] = False

        # 创建图形和画布
        self.figure = plt.figure(figsize=(width, height), dpi=dpi)
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def clear(self):
        """清除图形"""
        self.figure.clear()
        self.canvas.draw()

    def plot_bar_chart(self, data: dict, title: str = "", xlabel: str = "", ylabel: str = ""):
        """绘制柱状图"""
        self.clear()
        ax = self.figure.add_subplot(111)

        # 准备数据
        labels = list(data.keys())
        values = list(data.values())

        # 绘制柱状图
        bars = ax.bar(labels, values)

        # 添加数值标签
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width() / 2., height,
                    f'{height}',
                    ha='center', va='bottom')

        # 设置标题和标签
        ax.set_title(title, fontproperties='SimHei')
        ax.set_xlabel(xlabel, fontproperties='SimHei')
        ax.set_ylabel(ylabel, fontproperties='SimHei')

        # 旋转x轴标签
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right")

        self.canvas.draw()

    def plot_pie_chart(self, data: dict, title: str = ""):
        """绘制饼图"""
        self.clear()
        ax = self.figure.add_subplot(111)

        # 准备数据
        labels = list(data.keys())
        values = list(data.values())

        # 绘制饼图
        ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
        ax.axis('equal')  # 保持圆形
        ax.set_title(title, fontproperties='SimHei')

        self.canvas.draw()

class VTKWidget(QWidget):
    """VTK 3D模型显示部件"""

    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建VTK渲染窗口和交互器
        self.vtkWidget = QVTKRenderWindowInteractor(self)
        self.renderer = vtk.vtkRenderer()
        self.vtkWidget.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor = self.vtkWidget.GetRenderWindow().GetInteractor()

        # 设置布局
        layout = QVBoxLayout()
        layout.addWidget(self.vtkWidget)
        self.setLayout(layout)

        # 设置大小策略
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def clear(self):
        """清除场景"""
        self.renderer.RemoveAllViewProps()
        self.vtkWidget.GetRenderWindow().Render()

    def load_stl(self, file_path: str):
        """加载并显示STL文件"""
        self.clear()

        # 读取STL文件
        reader = vtk.vtkSTLReader()
        reader.SetFileName(file_path)
        reader.Update()

        # 创建映射器和演员
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputConnection(reader.GetOutputPort())

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)

        # 添加到渲染器
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()

        # 设置背景色为白色
        self.renderer.SetBackground(1, 1, 1)

        # 渲染
        self.vtkWidget.GetRenderWindow().Render()

    def load_point_cloud(self, points: np.ndarray):
        """加载并显示点云"""
        self.clear()

        # 创建点数据
        points_vtk = vtk.vtkPoints()
        vertices = vtk.vtkCellArray()

        for i, point in enumerate(points):
            pid = points_vtk.InsertNextPoint(point)
            vertices.InsertNextCell(1)
            vertices.InsertCellPoint(pid)

        # 创建多边形数据
        point_cloud = vtk.vtkPolyData()
        point_cloud.SetPoints(points_vtk)
        point_cloud.SetVerts(vertices)

        # 创建映射器和演员
        mapper = vtk.vtkPolyDataMapper()
        mapper.SetInputData(point_cloud)

        actor = vtk.vtkActor()
        actor.SetMapper(mapper)
        actor.GetProperty().SetPointSize(2)
        actor.GetProperty().SetColor(0, 0, 1)  # 蓝色

        # 添加到渲染器
        self.renderer.AddActor(actor)
        self.renderer.ResetCamera()
        self.renderer.SetBackground(1, 1, 1)  # 白色背景
        self.vtkWidget.GetRenderWindow().Render()

class VisualizationTab(QWidget):
    """可视化功能标签页"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # 创建标签页
        self.tabs = QTabWidget()

        # 数据集可视化标签
        self.data_viz_tab = QWidget()
        self.init_data_viz_ui()
        self.tabs.addTab(self.data_viz_tab, "数据集可视化")

        # 图数据可视化标签
        self.graph_viz_tab = QWidget()
        self.init_graph_viz_ui()
        self.tabs.addTab(self.graph_viz_tab, "图数据可视化")

        # 3D模型可视化标签
        self.model_viz_tab = QWidget()
        self.init_model_viz_ui()
        self.tabs.addTab(self.model_viz_tab, "3D模型可视化")

        layout.addWidget(self.tabs)
        self.setLayout(layout)

    def init_data_viz_ui(self):
        """初始化数据集可视化UI"""
        layout = QVBoxLayout()

        # 选择数据集目录
        dir_layout = QHBoxLayout()
        self.data_dir_label = QLabel("数据集目录:")
        self.data_dir_edit = QLineEdit()
        self.data_dir_btn = QPushButton("浏览...")
        self.data_dir_btn.clicked.connect(self.select_data_dir)
        dir_layout.addWidget(self.data_dir_label)
        dir_layout.addWidget(self.data_dir_edit)
        dir_layout.addWidget(self.data_dir_btn)

        # 可视化按钮和帮助按钮
        btn_layout = QHBoxLayout()
        self.viz_btn = QPushButton("可视化数据集")
        self.viz_btn.clicked.connect(self.visualize_dataset)
        self.help_btn = QPushButton("帮助")
        self.help_btn.clicked.connect(lambda: self.show_help("数据集可视化"))
        btn_layout.addWidget(self.viz_btn)
        btn_layout.addWidget(self.help_btn)

        # 图表显示区域
        self.matplotlib_widget = MatplotlibWidget()

        # 添加到布局
        layout.addLayout(dir_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.matplotlib_widget)

        self.data_viz_tab.setLayout(layout)

    def init_graph_viz_ui(self):
        """初始化图数据可视化UI"""
        layout = QVBoxLayout()

        # 选择图文件
        file_layout = QHBoxLayout()
        self.graph_file_label = QLabel("图文件:")
        self.graph_file_edit = QLineEdit()
        self.graph_file_btn = QPushButton("浏览...")
        self.graph_file_btn.clicked.connect(self.select_graph_file)
        file_layout.addWidget(self.graph_file_label)
        file_layout.addWidget(self.graph_file_edit)
        file_layout.addWidget(self.graph_file_btn)

        # 可视化按钮和帮助按钮
        btn_layout = QHBoxLayout()
        self.viz_graph_btn = QPushButton("可视化图结构")
        self.viz_graph_btn.clicked.connect(self.visualize_graph)
        self.help_graph_btn = QPushButton("帮助")
        self.help_graph_btn.clicked.connect(lambda: self.show_help("图数据可视化"))
        btn_layout.addWidget(self.viz_graph_btn)
        btn_layout.addWidget(self.help_graph_btn)

        # 图表显示区域
        self.graph_matplotlib_widget = MatplotlibWidget()

        # 添加到布局
        layout.addLayout(file_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.graph_matplotlib_widget)

        self.graph_viz_tab.setLayout(layout)

    def init_model_viz_ui(self):
        """初始化3D模型可视化UI"""
        layout = QVBoxLayout()

        # 选择模型文件
        file_layout = QHBoxLayout()
        self.model_file_label = QLabel("模型文件:")
        self.model_file_edit = QLineEdit()
        self.model_file_btn = QPushButton("浏览...")
        self.model_file_btn.clicked.connect(self.select_model_file)
        file_layout.addWidget(self.model_file_label)
        file_layout.addWidget(self.model_file_edit)
        file_layout.addWidget(self.model_file_btn)

        # 可视化按钮和帮助按钮
        btn_layout = QHBoxLayout()
        self.viz_model_btn = QPushButton("可视化模型")
        self.viz_model_btn.clicked.connect(self.visualize_model)
        self.help_model_btn = QPushButton("帮助")
        self.help_model_btn.clicked.connect(lambda: self.show_help("3D模型可视化"))
        btn_layout.addWidget(self.viz_model_btn)
        btn_layout.addWidget(self.help_model_btn)

        # 3D显示区域
        self.vtk_widget = VTKWidget()

        # 添加到布局
        layout.addLayout(file_layout)
        layout.addLayout(btn_layout)
        layout.addWidget(self.vtk_widget)

        self.model_viz_tab.setLayout(layout)

    def show_help(self, mode: str):
        """显示帮助对话框"""
        help_text = get_visualization_help(mode)
        dialog = HelpDialog(mode, help_text, self)
        dialog.exec_()

    def select_data_dir(self):
        """选择数据集目录"""
        dir_path = QFileDialog.getExistingDirectory(self, "选择数据集目录")
        if dir_path:
            self.data_dir_edit.setText(dir_path)

    def select_graph_file(self):
        """选择图文件"""
        file_path, _ = QFileDialog.getOpenFileName(self, "选择图文件", "", "BIN Files (*.bin)")
        if file_path:
            self.graph_file_edit.setText(file_path)

    def select_model_file(self):
        """选择模型文件"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择模型文件", "",
            "STL文件 (*.stl);;点云文件 (*.txt)"
        )
        if file_path:
            self.model_file_edit.setText(file_path)

    def visualize_dataset(self):
        """可视化数据集"""
        from dataset_processor import analyze_dataset_balance

        dir_path = self.data_dir_edit.text().strip()
        if not dir_path:
            QMessageBox.warning(self, "警告", "请选择数据集目录")
            return

        try:
            # 分析数据集
            stats, _ = analyze_dataset_balance(dir_path)

            # 按样本数量排序
            sorted_stats = dict(sorted(stats.items(), key=lambda item: item[1], reverse=True))

            # 只显示前20个类别，避免图表过于拥挤
            if len(sorted_stats) > 20:
                top_stats = dict(list(sorted_stats.items())[:20])
                other_count = sum(list(sorted_stats.values())[20:])
                top_stats["其他"] = other_count
            else:
                top_stats = sorted_stats

            # 绘制类别分布柱状图
            self.matplotlib_widget.plot_bar_chart(
                top_stats,
                title="数据集类别分布",
                xlabel="类别",
                ylabel="样本数量"
            )

        except Exception as e:
            QMessageBox.critical(self, "错误", f"可视化失败: {str(e)}")

    def visualize_graph(self):
        """可视化图结构"""
        from graph_processor import init

        file_path = self.graph_file_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "警告", "请选择图文件")
            return

        try:
            # 加载图
            graph = init(file_path)

            # 提取节点和边数量
            node_count = graph.number_of_nodes()
            edge_count = graph.number_of_edges()

            # 创建信息文本
            info_text = (
                f"图结构基本信息:\n"
                f"• 节点数量: {node_count}\n"
                f"• 边数量: {edge_count}"
            )

            # 清除旧的信息标签（如果有）
            if hasattr(self, 'graph_info_label'):
                self.graph_viz_tab.layout().removeWidget(self.graph_info_label)
                self.graph_info_label.deleteLater()

            # 创建并添加新信息标签
            self.graph_info_label = QLabel(info_text)
            self.graph_info_label.setStyleSheet("""
                font-size: 12px;
                padding: 8px;
                background-color: #f0f0f0;
                border-radius: 5px;
            """)
            self.graph_info_label.setAlignment(Qt.AlignCenter)

            # 将信息标签插入到布局中（按钮和图表之间）
            layout = self.graph_viz_tab.layout()
            layout.insertWidget(2, self.graph_info_label)

            # 准备饼图数据
            stats = {
                "节点": node_count,
                "边": edge_count
            }

            # 绘制饼图
            self.graph_matplotlib_widget.plot_pie_chart(
                stats,
                title="节点与边数量比例"
            )

        except Exception as e:
            QMessageBox.critical(self, "错误", f"可视化失败: {str(e)}\n{traceback.format_exc()}")

    def visualize_model(self):
        """可视化3D模型"""
        file_path = self.model_file_edit.text().strip()
        if not file_path:
            QMessageBox.warning(self, "警告", "请选择模型文件")
            return

        try:
            if file_path.lower().endswith('.stl'):
                # 显示STL模型
                self.vtk_widget.load_stl(file_path)

            elif file_path.lower().endswith('.txt'):
                # 加载点云
                points = np.loadtxt(file_path)
                if points.shape[1] >= 3:
                    self.vtk_widget.load_point_cloud(points[:, :3])
                else:
                    QMessageBox.warning(self, "警告", "点云文件格式不正确")
            else:
                QMessageBox.warning(self, "警告", "不支持的文件格式")

        except Exception as e:
            QMessageBox.critical(self, "错误", f"可视化失败: {str(e)}")

    def get_current_settings(self):
        """获取当前可视化标签页的设置"""
        return {
            "data_dir": self.data_dir_edit.text(),
            "graph_file": self.graph_file_edit.text(),
            "model_file": self.model_file_edit.text()
        }

    def apply_settings(self, settings):
        """应用设置到可视化标签页"""
        self.data_dir_edit.setText(settings.get("data_dir", ""))
        self.graph_file_edit.setText(settings.get("graph_file", ""))
        self.model_file_edit.setText(settings.get("model_file", ""))