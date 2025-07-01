"""
3D模型处理模块
包含STEP/STL转换、点云采样、多视图渲染和STEP到DGL图转换的核心逻辑
"""

import os
import time
import signal
import logging
import traceback
import numpy as np
import open3d as o3d
from vtkmodules.util.numpy_support import vtk_to_numpy
import vtkmodules.all as vtk
from typing import List, Tuple, Set, Dict, Optional, Any, Callable
from pathlib import Path
import dgl
import torch
from itertools import repeat
from multiprocessing import Pool, Manager, Queue
from types import SimpleNamespace
from functools import partial
from occwl.graph import face_adjacency
from occwl.io import load_step
from occwl.uvgrid import ugrid, uvgrid
import sys
# 配置日志记录
logger = logging.getLogger(__name__)

def _initializer():
    """多进程初始化函数（必须定义在模块级别）"""
    signal.signal(signal.SIGINT, signal.SIG_IGN)

class ModelProcessor:
    @staticmethod
    def create_process_pool(num_processes: int) -> Pool:
        """
        创建进程池

        参数:
            num_processes: 进程数量

        返回:
            multiprocessing.Pool: 创建的进程池

        异常:
            ValueError: 如果进程数小于等于0
            Exception: 如果创建进程池失败
        """
        if num_processes <= 0:
            raise ValueError("进程数必须大于0")

        try:
            logger.info(f"创建包含 {num_processes} 个进程的进程池")
            return Pool(processes=num_processes, initializer=_initializer)
        except Exception as e:
            logger.error(f"创建进程池失败: {str(e)}")
            raise Exception(f"创建进程池失败: {str(e)}")

    @staticmethod
    def convert_step_to_stl(step_file: str, output_dir: str, mesh_quality: int = 5) -> bool:
        """
        将STEP文件转换为STL格式

        参数:
            step_file: 输入的STEP文件路径
            output_dir: 输出目录
            mesh_quality: 网格质量(1-10)

        返回:
            bool: 转换是否成功

        异常:
            FileNotFoundError: 如果STEP文件不存在
            ValueError: 如果网格质量不在1-10范围内
            ImportError: 如果缺少OpenCASCADE依赖
            Exception: 如果转换过程中出现其他错误
        """
        # 验证输入参数
        if not os.path.isfile(step_file):
            raise FileNotFoundError(f"STEP文件不存在: {step_file}")
        if not 1 <= mesh_quality <= 10:
            raise ValueError("网格质量必须在1-10之间")

        try:
            # 导入OpenCASCADE相关模块
            from OCC.Core.STEPControl import STEPControl_Reader
            from OCC.Core.IFSelect import IFSelect_RetDone
            from OCC.Core.BRepMesh import BRepMesh_IncrementalMesh
            from OCC.Core.StlAPI import StlAPI_Writer

            # 网格质量映射
            quality_map = {
                1: 0.5, 2: 0.4, 3: 0.3, 4: 0.2, 5: 0.15,
                6: 0.1, 7: 0.07, 8: 0.05, 9: 0.03, 10: 0.01
            }
            deflection = quality_map.get(mesh_quality, 0.15)

            logger.info(f"开始转换STEP文件: {step_file} (质量: {mesh_quality})")

            # 读取STEP文件
            step_reader = STEPControl_Reader()
            status = step_reader.ReadFile(step_file)
            if status != IFSelect_RetDone:
                logger.error(f"读取STEP文件失败: {step_file}")
                return False

            # 转换模型
            step_reader.TransferRoots()
            shape = step_reader.OneShape()

            # 生成网格
            mesh = BRepMesh_IncrementalMesh(shape, deflection)
            mesh.Perform()
            if not mesh.IsDone():
                logger.error(f"网格生成失败: {step_file}")
                return False

            # 准备输出路径
            stl_filename = Path(step_file).stem + ".stl"
            stl_file = str(Path(output_dir) / stl_filename)
            os.makedirs(output_dir, exist_ok=True)

            # 写入STL文件
            stl_writer = StlAPI_Writer()
            stl_writer.SetASCIIMode(False)
            success = stl_writer.Write(shape, stl_file)

            if success:
                logger.info(f"成功转换STEP到STL: {stl_file}")
            else:
                logger.error(f"写入STL文件失败: {stl_file}")

            return success

        except ImportError as e:
            logger.error("OpenCASCADE库不可用，无法执行STEP转换")
            raise ImportError("OpenCASCADE库不可用，无法执行STEP转换") from e
        except Exception as e:
            logger.error(f"STEP转STL失败: {str(e)}")
            return False

    @staticmethod
    def sample_point_cloud(stl_file: str, output_dir: str, num_points: int = 2048,
                          include_normals: bool = False) -> bool:
        """
        从STL文件生成点云

        参数:
            stl_file: 输入的STL文件路径
            output_dir: 输出目录
            num_points: 采样点数量
            include_normals: 是否包含法线信息

        返回:
            bool: 采样是否成功

        异常:
            FileNotFoundError: 如果STL文件不存在
            ValueError: 如果采样点数小于等于0
            Exception: 如果采样过程中出现其他错误
        """
        # 验证输入参数
        if not os.path.isfile(stl_file):
            raise FileNotFoundError(f"STL文件不存在: {stl_file}")
        if num_points <= 0:
            raise ValueError("采样点数必须大于0")

        try:
            logger.info(f"开始从STL文件生成点云: {stl_file} (点数: {num_points})")

            # 读取STL文件
            mesh = o3d.io.read_triangle_mesh(stl_file)
            if not mesh.has_vertices():
                logger.error(f"STL文件没有顶点数据: {stl_file}")
                return False

            # 采样点云
            pcd = mesh.sample_points_poisson_disk(number_of_points=num_points)
            points = np.asarray(pcd.points)

            # 准备输出数据
            if include_normals:
                normals = np.asarray(pcd.normals)
                combined_data = np.hstack((points, normals))
            else:
                combined_data = points

            # 准备输出路径
            txt_filename = Path(stl_file).stem + ".txt"
            txt_file = str(Path(output_dir) / txt_filename)
            os.makedirs(output_dir, exist_ok=True)

            # 保存点云数据
            np.savetxt(txt_file, combined_data, fmt='%.6f')
            logger.info(f"成功生成点云文件: {txt_file}")
            return True

        except Exception as e:
            logger.error(f"STL转点云失败: {str(e)}")
            return False

    @staticmethod
    def render_multiview(stl_file: str, output_dir: str, num_views: int = 12,
                        image_size: int = 224) -> bool:
        """
        为STL模型渲染多视图

        参数:
            stl_file: 输入的STL文件路径
            output_dir: 输出目录
            num_views: 视图数量
            image_size: 图像尺寸

        返回:
            bool: 渲染是否成功

        异常:
            FileNotFoundError: 如果STL文件不存在
            ValueError: 如果视图数或图像尺寸无效
            Exception: 如果渲染过程中出现其他错误
        """
        # 验证输入参数
        if not os.path.isfile(stl_file):
            raise FileNotFoundError(f"STL文件不存在: {stl_file}")
        if num_views <= 0:
            raise ValueError("视图数量必须大于0")
        if image_size <= 0:
            raise ValueError("图像尺寸必须大于0")

        try:
            logger.info(f"开始渲染多视图: {stl_file} (视图数: {num_views}, 尺寸: {image_size})")

            # 读取STL文件
            reader = vtk.vtkSTLReader()
            reader.SetFileName(stl_file)
            reader.Update()

            if reader.GetOutput().GetNumberOfPoints() == 0:
                logger.error(f"STL文件没有点数据: {stl_file}")
                return False

            # 设置映射器和演员
            mapper = vtk.vtkPolyDataMapper()
            mapper.SetInputConnection(reader.GetOutputPort())

            actor = vtk.vtkActor()
            actor.SetMapper(mapper)

            # 设置渲染器
            renderer = vtk.vtkRenderer()
            renderer.AddActor(actor)
            renderer.SetBackground(1, 1, 1)  # 白色背景

            # 设置渲染窗口
            render_window = vtk.vtkRenderWindow()
            render_window.SetOffScreenRendering(1)
            render_window.SetSize(image_size, image_size)
            render_window.AddRenderer(renderer)

            # 计算角度步长
            angle_step = 360 / num_views
            model_name = Path(stl_file).stem

            # 渲染每个视图
            for view_index in range(num_views):
                try:
                    # 设置相机位置
                    camera = renderer.GetActiveCamera()
                    camera.SetPosition(0, 0, 1)
                    camera.SetFocalPoint(0, 0, 0)
                    camera.Azimuth(view_index * angle_step)
                    camera.Elevation(30)  # 固定30度俯仰角
                    renderer.ResetCamera()

                    # 渲染当前视图
                    render_window.Render()

                    # 捕获图像
                    window_to_image_filter = vtk.vtkWindowToImageFilter()
                    window_to_image_filter.SetInput(render_window)
                    window_to_image_filter.Update()

                    # 准备输出路径
                    output_file = str(Path(output_dir) / f"{model_name}_{view_index:02d}.png")
                    os.makedirs(output_dir, exist_ok=True)

                    # 保存PNG图像
                    writer = vtk.vtkPNGWriter()
                    writer.SetFileName(output_file)
                    writer.SetInputConnection(window_to_image_filter.GetOutputPort())
                    writer.Write()

                    logger.debug(f"成功渲染视图 {view_index}: {output_file}")

                except Exception as view_error:
                    logger.error(f"渲染视图 {view_index} 失败: {str(view_error)}")
                    continue

            logger.info(f"成功完成多视图渲染: {stl_file}")
            return True

        except Exception as e:
            logger.error(f"多视图渲染失败: {str(e)}")
            return False

    @staticmethod
    def build_graph(solid, curv_num_u_samples: int = 10,
                   surf_num_u_samples: int = 10, surf_num_v_samples: int = 10) -> dgl.DGLGraph:
        """
        构建DGL图结构

        参数:
            solid: OCCWL实体对象
            curv_num_u_samples: 曲线U方向采样数
            surf_num_u_samples: 曲面U方向采样数
            surf_num_v_samples: 曲面V方向采样数

        返回:
            dgl.DGLGraph: 构建的图结构

        异常:
            Exception: 如果构建过程中出现错误
        """
        try:
            logger.debug("开始构建DGL图结构")

            # 创建面邻接图
            graph = face_adjacency(solid)

            # 处理面特征
            graph_face_feat = []
            for face_idx in graph.nodes:
                face = graph.nodes[face_idx]["face"]

                # 采样曲面上的点
                points = uvgrid(face, method="point",
                              num_u=surf_num_u_samples,
                              num_v=surf_num_v_samples)

                # 采样曲面法线
                normals = uvgrid(face, method="normal",
                               num_u=surf_num_u_samples,
                               num_v=surf_num_v_samples)

                # 采样可见性状态
                visibility_status = uvgrid(face, method="visibility_status",
                                         num_u=surf_num_u_samples,
                                         num_v=surf_num_v_samples)

                # 创建面特征
                mask = np.logical_or(visibility_status == 0, visibility_status == 2)
                face_feat = np.concatenate((points, normals, mask), axis=-1)
                graph_face_feat.append(face_feat)

            graph_face_feat = np.asarray(graph_face_feat)

            # 处理边特征
            graph_edge_feat = []
            for edge_idx in graph.edges:
                edge = graph.edges[edge_idx]["edge"]
                if not edge.has_curve():
                    continue

                # 采样曲线上的点和切线
                points = ugrid(edge, method="point", num_u=curv_num_u_samples)
                tangents = ugrid(edge, method="tangent", num_u=curv_num_u_samples)

                # 创建边特征
                edge_feat = np.concatenate((points, tangents), axis=-1)
                graph_edge_feat.append(edge_feat)

            graph_edge_feat = np.asarray(graph_edge_feat)

            # 创建DGL图
            edges = list(graph.edges)
            src = [e[0] for e in edges]
            dst = [e[1] for e in edges]
            dgl_graph = dgl.graph((src, dst), num_nodes=len(graph.nodes))

            # 添加节点和边特征
            dgl_graph.ndata["x"] = torch.from_numpy(graph_face_feat)
            dgl_graph.edata["x"] = torch.from_numpy(graph_edge_feat)

            logger.debug("成功构建DGL图结构")
            return dgl_graph

        except Exception as e:
            logger.error(f"构建图结构失败: {str(e)}")
            raise Exception(f"构建图结构失败: {str(e)}")

    @staticmethod
    def _process_single_step_file(args: Tuple[Path, SimpleNamespace, List, Optional[Queue]]) -> Optional[Tuple[str, str]]:
        """
        处理单个STEP文件（内部方法，用于多进程）

        参数:
            args: 包含以下内容的元组:
                - file_path: STEP文件路径
                - args: 包含处理参数的SimpleNamespace对象
                - failed_files: 失败文件列表
                - progress_queue: 进度队列

        返回:
            如果成功返回None，如果失败返回(相对路径, 错误信息)
        """
        try:
            file_path, args, failed_files, progress_queue = args
            relative_path = file_path.relative_to(args.input)
            output_file = Path(args.output) / relative_path.with_suffix('.bin')
            output_file.parent.mkdir(parents=True, exist_ok=True)

            logger.debug(f"处理STEP文件: {file_path}")

            # 加载STEP文件
            solid = load_step(file_path)
            if not solid or len(solid) == 0:
                raise ValueError("无法加载STEP文件或文件为空")

            # 构建图结构
            graph = ModelProcessor.build_graph(
                solid[0],
                args.curv_u_samples,
                args.surf_u_samples,
                args.surf_v_samples
            )

            # 保存图结构
            dgl.data.utils.save_graphs(str(output_file), [graph])

            # 更新进度
            if progress_queue is not None:
                progress_queue.put(1)

            logger.debug(f"成功处理STEP文件: {file_path}")
            return None

        except Exception as e:
            error_msg = str(e)
            logger.warning(f"处理STEP文件 {file_path} 失败: {error_msg}")

            # 更新进度
            if progress_queue is not None:
                progress_queue.put(0)

            return (str(file_path.relative_to(args.input)), error_msg)

    @staticmethod
    def convert_step_to_dgl(input_dir: str, output_dir: str,
                            curv_u_samples: int = 10, surf_u_samples: int = 10,
                            surf_v_samples: int = 10, num_processes: int = 8,
                            progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[
        int, List[Tuple[str, str]]]:
        """
        批量转换STEP文件到DGL图结构（修改版，解决打包问题）
        """
        # 验证输入参数
        input_path = Path(input_dir)
        if not input_path.is_dir():
            raise NotADirectoryError(f"输入目录不存在: {input_dir}")

        # 在打包环境中强制使用单进程
        if getattr(sys, 'frozen', False):
            num_processes = 1
            logger.warning("检测到打包环境，强制使用单进程模式")

        # 查找所有STEP文件
        step_files = list(input_path.rglob("*.stp")) + list(input_path.rglob("*.step"))
        total_files = len(step_files)

        if not step_files:
            raise ValueError("没有找到任何STEP文件")

        args = SimpleNamespace(
            input=input_path,
            output=output_dir,
            curv_u_samples=curv_u_samples,
            surf_u_samples=surf_u_samples,
            surf_v_samples=surf_v_samples
        )

        failed_files = []
        processed_count = 0

        try:
            # 使用单进程模式处理（适用于打包环境）
            if getattr(sys, 'frozen', False):
                logger.info("使用单进程模式处理STEP文件")
                for file in step_files:
                    try:
                        result = ModelProcessor._process_single_step_file(
                            (file, args, failed_files, None)
                        )
                        processed_count += 1

                        if progress_callback:
                            progress_callback(processed_count, total_files)

                        if result is not None:
                            failed_files.append(result)

                    except Exception as e:
                        failed_files.append((str(file.relative_to(args.input)), str(e)))
                        logger.error(f"处理文件 {file} 失败: {str(e)}")

            # 多进程模式（仅用于开发环境）
            else:
                with Pool(processes=num_processes, initializer=_initializer) as pool:
                    tasks = ((file, args, failed_files, None) for file in step_files)

                    for result in pool.imap_unordered(
                            ModelProcessor._process_single_step_file,
                            tasks,
                            chunksize=max(1, min(10, len(step_files) // (num_processes * 10)))
                    ):
                        processed_count += 1

                        if progress_callback:
                            progress_callback(processed_count, total_files)

                        if result is not None:
                            failed_files.append(result)

        except Exception as e:
            logger.error(f"处理STEP文件失败: {str(e)}")
            raise Exception(f"处理STEP文件失败: {str(e)}")

        return len(failed_files), failed_files

    @staticmethod
    def batch_process_files(process_func: Callable[[str, str], bool], input_dir: str, output_dir: str,
                          extensions: Tuple[str, ...], progress_callback: Optional[Callable[[int, int], None]] = None) -> Tuple[int, List[str]]:
        """
        通用批量文件处理方法

        参数:
            process_func: 处理单个文件的函数
            input_dir: 输入目录
            output_dir: 输出目录
            extensions: 文件扩展名元组
            progress_callback: 进度回调函数

        返回:
            元组(成功处理数, 失败文件列表)
        """
        # 验证输入参数
        if not callable(process_func):
            raise TypeError("process_func必须是可调用对象")
        if not os.path.isdir(input_dir):
            raise NotADirectoryError(f"输入目录不存在: {input_dir}")
        if not extensions:
            raise ValueError("必须提供至少一个文件扩展名")

        logger.info(f"开始批量处理文件: {input_dir} -> {output_dir}")

        input_path = Path(input_dir)
        output_path = Path(output_dir)
        failed_files = []
        success_count = 0

        # 查找所有匹配的文件
        files = []
        for ext in extensions:
            files.extend(input_path.rglob(f"*{ext}"))
        total_files = len(files)

        if total_files == 0:
            logger.warning(f"没有找到匹配 {extensions} 的文件")
            return 0, []

        # 处理每个文件
        for file_index, file in enumerate(files, 1):
            try:
                # 准备输出路径
                relative_path = file.relative_to(input_path).parent
                current_output_dir = output_path / relative_path
                current_output_dir.mkdir(parents=True, exist_ok=True)

                # 处理文件
                if process_func(str(file), str(current_output_dir)):
                    success_count += 1
                else:
                    failed_files.append(str(file))

                # 更新进度
                if progress_callback:
                    progress_callback(file_index, total_files)

            except Exception as e:
                failed_files.append(str(file))
                logger.error(f"处理文件 {file} 失败: {str(e)}")

        logger.info(f"文件处理完成: 共 {total_files} 个文件, 成功 {success_count} 个")
        return success_count, failed_files