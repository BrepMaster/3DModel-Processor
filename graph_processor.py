"""
图数据处理模块
包含加载和处理图数据的相关函数
"""

import logging
import torch
from pathlib import Path
from dgl.data.utils import load_graphs
from torch import FloatTensor
from typing import Dict, Any, Union, Tuple

logger = logging.getLogger(__name__)

def bounding_box_uvgrid(inp: torch.Tensor) -> torch.Tensor:
    """
    计算UV网格的边界框

    参数:
        inp: 输入张量，形状为(..., 7)，其中前3个是坐标，最后1个是可见性状态

    返回:
        torch.Tensor: 边界框张量，形状为(2, 3)，表示最小和最大点

    异常:
        TypeError: 如果输入不是torch.Tensor
        ValueError: 如果输入张量形状不正确
        Exception: 如果计算过程中出现错误
    """
    # 验证输入参数
    if not isinstance(inp, torch.Tensor):
        raise TypeError("输入必须是torch.Tensor")
    if inp.dim() < 2 or inp.size(-1) != 7:
        raise ValueError("输入张量形状不正确，最后一个维度必须是7")

    try:
        # 提取坐标和可见性状态
        points = inp[..., :3].reshape((-1, 3))
        visibility_mask = inp[..., 6].reshape(-1)

        # 只保留可见点
        visible_points = points[visibility_mask == 1, :]

        # 计算边界框
        return bounding_box_pointcloud(visible_points)

    except Exception as e:
        logger.error(f"计算UV网格边界框失败: {str(e)}")
        raise Exception(f"计算UV网格边界框失败: {str(e)}")

def bounding_box_pointcloud(pts: torch.Tensor) -> torch.Tensor:
    """
    计算点云的边界框

    参数:
        pts: 点云张量，形状为(N, 3)

    返回:
        torch.Tensor: 边界框张量，形状为(2, 3)，表示最小和最大点

    异常:
        TypeError: 如果输入不是torch.Tensor
        ValueError: 如果输入张量形状不正确
        Exception: 如果计算过程中出现错误
    """
    # 验证输入参数
    if not isinstance(pts, torch.Tensor):
        raise TypeError("输入必须是torch.Tensor")
    if pts.dim() != 2 or pts.size(1) != 3:
        raise ValueError("点云张量形状必须是(N, 3)")
    if pts.size(0) == 0:
        raise ValueError("点云不能为空")

    try:
        # 计算每个维度的最小值和最大值
        x_coords = pts[:, 0]
        y_coords = pts[:, 1]
        z_coords = pts[:, 2]

        min_point = torch.tensor([x_coords.min(), y_coords.min(), z_coords.min()])
        max_point = torch.tensor([x_coords.max(), y_coords.max(), z_coords.max()])

        return torch.stack([min_point, max_point])

    except Exception as e:
        logger.error(f"计算点云边界框失败: {str(e)}")
        raise Exception(f"计算点云边界框失败: {str(e)}")

def center_and_scale_uvgrid(
    inp: torch.Tensor,
    return_center_scale: bool = False
) -> Union[torch.Tensor, Tuple[torch.Tensor, torch.Tensor, float]]:
    """
    对UV网格进行中心化和缩放

    参数:
        inp: 输入张量，形状为(..., 7)
        return_center_scale: 是否返回中心和缩放因子

    返回:
        如果return_center_scale为False，返回处理后的张量
        如果return_center_scale为True，返回元组(处理后的张量, 中心点, 缩放因子)

    异常:
        TypeError: 如果输入不是torch.Tensor
        ValueError: 如果输入张量形状不正确
        Exception: 如果计算过程中出现错误
    """
    # 验证输入参数
    if not isinstance(inp, torch.Tensor):
        raise TypeError("输入必须是torch.Tensor")
    if inp.dim() < 2 or inp.size(-1) != 7:
        raise ValueError("输入张量形状不正确，最后一个维度必须是7")

    try:
        # 计算边界框
        bbox = bounding_box_uvgrid(inp)

        # 计算对角线和缩放因子
        diagonal = bbox[1] - bbox[0]
        scale_factor = 2.0 / max(diagonal[0], diagonal[1], diagonal[2])

        # 计算中心点
        center_point = 0.5 * (bbox[0] + bbox[1])

        # 中心化和缩放
        inp_centered_scaled = inp.clone()
        inp_centered_scaled[..., :3] -= center_point
        inp_centered_scaled[..., :3] *= scale_factor

        if return_center_scale:
            return inp_centered_scaled, center_point, scale_factor
        else:
            return inp_centered_scaled

    except Exception as e:
        logger.error(f"中心化和缩放UV网格失败: {str(e)}")
        raise Exception(f"中心化和缩放UV网格失败: {str(e)}")

def load_one_graph(file_path: str) -> Dict[str, Any]:
    """
    加载单个图文件

    参数:
        file_path: 图文件路径(.bin文件)

    返回:
        字典，包含以下键:
        - "graph": 加载的图数据
        - "filename": 文件名(不含扩展名)

    异常:
        FileNotFoundError: 如果文件不存在
        Exception: 如果加载过程中出现错误
    """
    # 验证输入参数
    file_path_obj = Path(file_path)
    if not file_path_obj.is_file():
        raise FileNotFoundError(f"图文件不存在: {file_path}")

    try:
        # 加载图数据
        graphs = load_graphs(str(file_path_obj))
        if not graphs or len(graphs[0]) == 0:
            raise ValueError("加载的图为空")

        graph = graphs[0][0]

        # 中心化和缩放
        graph.ndata["x"], center_point, scale_factor = center_and_scale_uvgrid(
            graph.ndata["x"],
            return_center_scale=True
        )

        # 对边数据进行相同的变换
        graph.edata["x"][..., :3] -= center_point
        graph.edata["x"][..., :3] *= scale_factor

        # 转换为FloatTensor
        graph.ndata["x"] = graph.ndata["x"].type(FloatTensor)
        graph.edata["x"] = graph.edata["x"].type(FloatTensor)

        return {
            "graph": graph,
            "filename": file_path_obj.stem
        }

    except Exception as e:
        logger.error(f"加载图文件 {file_path} 失败: {str(e)}")
        raise Exception(f"加载图文件 {file_path} 失败: {str(e)}")

def init(file_path: str) -> Any:
    """
    初始化图数据

    参数:
        file_path: 图文件路径(.bin文件)

    返回:
        处理后的图数据，节点和边特征已重新排列

    异常:
        FileNotFoundError: 如果文件不存在
        Exception: 如果初始化过程中出现错误
    """
    try:
        # 加载图数据
        sample = load_one_graph(file_path)
        graph = sample["graph"]

        # 重新排列节点和边特征的维度
        graph.ndata["x"] = graph.ndata["x"].permute(0, 3, 1, 2)
        graph.edata["x"] = graph.edata["x"].permute(0, 2, 1)

        return graph

    except Exception as e:
        logger.error(f"初始化图数据失败: {str(e)}")
        raise Exception(f"初始化图数据失败: {str(e)}")