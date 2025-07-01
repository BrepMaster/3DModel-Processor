"""
统计分析模块
包含对图数据和数据集进行统计分析的功能
"""

import logging
import openpyxl
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from openpyxl.workbook import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from graph_processor import init

# 配置日志记录
logger = logging.getLogger(__name__)

class StatisticsAnalyzer:
    @staticmethod
    def analyze_max_nodes_edges(dir_path: Path) -> Tuple[str, str]:
        """
        分析目录中节点和边数量最多的图文件

        参数:
            dir_path: 包含.bin文件的目录路径，必须是Path对象

        返回:
            包含最多节点和最多边的文件信息的元组

        异常:
            NotADirectoryError: 如果目录不存在
            Exception: 如果分析过程中出现错误
        """
        # 验证输入参数
        if not isinstance(dir_path, Path):
            raise TypeError("dir_path必须是Path对象")
        if not dir_path.is_dir():
            raise NotADirectoryError(f"目录不存在: {dir_path}")

        max_nodes = -1
        max_edges = -1
        file_nodes = ""
        file_edges = ""

        try:
            # 遍历目录中的所有.bin文件
            for file in dir_path.glob("*.bin"):
                try:
                    # 初始化图数据
                    graph = init(str(file))

                    # 获取节点和边数量
                    node_count = graph.number_of_nodes()
                    edge_count = graph.number_of_edges()

                    # 更新最大值
                    if node_count > max_nodes:
                        max_nodes = node_count
                        file_nodes = str(file)

                    if edge_count > max_edges:
                        max_edges = edge_count
                        file_edges = str(file)

                except Exception as file_error:
                    logger.warning(f"分析文件 {file} 失败: {str(file_error)}")
                    continue

            # 返回格式化结果
            nodes_result = f"{file_nodes}\n节点数: {max_nodes}"
            edges_result = f"{file_edges}\n边数: {max_edges}"

            return (nodes_result, edges_result)

        except Exception as analysis_error:
            logger.error(f"分析最大节点/边失败: {str(analysis_error)}")
            raise Exception(f"分析最大节点/边失败: {str(analysis_error)}")

    @staticmethod
    def analyze_category_statistics(input_dir: Path) -> Dict[str, Dict[str, Any]]:
        """
        按类别统计图数据信息

        参数:
            input_dir: 包含按类别组织的.bin文件的目录路径，必须是Path对象

        返回:
            字典，键是类别名称，值是包含统计信息的字典:
            {
                "model_count": 模型数量,
                "nodes": 节点数量列表,
                "edges": 边数量列表
            }

        异常:
            NotADirectoryError: 如果目录不存在
            Exception: 如果分析过程中出现错误
        """
        # 验证输入参数
        if not isinstance(input_dir, Path):
            raise TypeError("input_dir必须是Path对象")
        if not input_dir.is_dir():
            raise NotADirectoryError(f"目录不存在: {input_dir}")

        category_stats = {}

        try:
            # 遍历目录中的每个子文件夹（代表一个类别）
            for subfolder in input_dir.iterdir():
                if not subfolder.is_dir():
                    continue

                category_name = subfolder.name
                nodes_list = []
                edges_list = []
                model_count = 0

                try:
                    # 遍历类别文件夹中的所有.bin文件
                    for file in subfolder.glob("*.bin"):
                        try:
                            # 初始化图数据
                            graph = init(str(file))

                            # 收集统计信息
                            nodes_list.append(graph.number_of_nodes())
                            edges_list.append(graph.number_of_edges())
                            model_count += 1

                        except Exception as file_error:
                            logger.warning(f"分析文件 {file} 失败: {str(file_error)}")
                            continue

                    # 如果有有效模型，添加到统计结果
                    if model_count > 0:
                        category_stats[category_name] = {
                            "model_count": model_count,
                            "nodes": nodes_list,
                            "edges": edges_list
                        }

                except Exception as category_error:
                    logger.warning(f"分析类别 {category_name} 失败: {str(category_error)}")
                    continue

            return category_stats

        except Exception as analysis_error:
            logger.error(f"分析类别统计失败: {str(analysis_error)}")
            raise Exception(f"分析类别统计失败: {str(analysis_error)}")

    @staticmethod
    def save_statistics_to_excel(stats: Dict[str, Dict[str, Any]], save_path: Path) -> bool:
        """
        将统计结果保存到Excel文件

        参数:
            stats: 统计信息字典，格式与analyze_category_statistics返回的一致
            save_path: Excel文件保存路径，必须是Path对象

        返回:
            bool: 是否成功保存

        异常:
            ValueError: 如果统计信息为空
            TypeError: 如果参数类型不正确
            Exception: 如果保存过程中出现错误
        """
        # 验证输入参数
        if not stats:
            raise ValueError("统计信息为空")
        if not isinstance(save_path, Path):
            raise TypeError("save_path必须是Path对象")

        try:
            # 创建新的Excel工作簿
            workbook = Workbook()
            worksheet = workbook.active
            worksheet.title = "类别统计"

            # 设置表头
            headers = [
                "类别", "模型数量",
                "节点平均", "节点标准差", "节点最小", "节点最大",
                "边平均", "边标准差", "边最小", "边最大"
            ]
            worksheet.append(headers)

            # 遍历每个类别的统计信息
            for category_name, category_data in sorted(stats.items()):
                try:
                    nodes = category_data["nodes"]
                    edges = category_data["edges"]

                    # 计算节点统计量
                    node_avg = sum(nodes) / len(nodes)
                    node_std = (sum((x - node_avg) ** 2 for x in nodes) / len(nodes)) ** 0.5
                    node_min = min(nodes)
                    node_max = max(nodes)

                    # 计算边统计量
                    edge_avg = sum(edges) / len(edges)
                    edge_std = (sum((x - edge_avg) ** 2 for x in edges) / len(edges)) ** 0.5
                    edge_min = min(edges)
                    edge_max = max(edges)

                    # 添加一行数据
                    worksheet.append([
                        category_name,
                        category_data["model_count"],
                        round(node_avg, 2),
                        round(node_std, 2),
                        node_min,
                        node_max,
                        round(edge_avg, 2),
                        round(edge_std, 2),
                        edge_min,
                        edge_max
                    ])

                except Exception as calculation_error:
                    logger.warning(f"计算类别 {category_name} 统计量失败: {str(calculation_error)}")
                    continue

            # 确保保存目录存在
            save_path.parent.mkdir(parents=True, exist_ok=True)

            # 保存Excel文件
            workbook.save(str(save_path))
            return True

        except Exception as save_error:
            logger.error(f"保存Excel失败: {str(save_error)}")
            return False