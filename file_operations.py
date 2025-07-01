"""
文件操作模块
包含与文件系统交互的实用函数
"""

import os
import logging
from typing import List, Tuple, Dict, Optional
from pathlib import Path
import shutil

# 配置日志记录
logger = logging.getLogger(__name__)

def get_files_by_suffix(directory: str, suffixes: List[str]) -> List[str]:
    """
    获取目录中指定后缀的文件

    参数:
        directory: 目录路径
        suffixes: 后缀列表

    返回:
        匹配的文件路径列表

    异常:
        NotADirectoryError: 如果目录不存在
        ValueError: 如果没有提供后缀
        Exception: 如果获取过程中出现其他错误
    """
    # 验证输入参数
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"目录不存在: {directory}")
    if not suffixes:
        raise ValueError("必须提供至少一个后缀")

    logger.debug(f"获取文件: {directory} (后缀: {suffixes})")

    matched = []
    try:
        # 遍历目录树
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)

                # 检查文件后缀
                if any(file.lower().endswith(s.lower()) for s in suffixes):
                    matched.append(file_path)
                    logger.debug(f"找到匹配文件: {file_path}")

        logger.info(f"找到 {len(matched)} 个匹配文件")
        return matched

    except Exception as e:
        logger.error(f"获取文件失败: {str(e)}")
        raise Exception(f"获取文件失败: {str(e)}")

def count_files_in_subfolders(directory: str,
                            suffixes: Optional[List[str]] = None) -> Tuple[Dict[str, int], int]:
    """
    统计子文件夹中的文件数量

    参数:
        directory: 目录路径
        suffixes: 可选的后缀列表，如果为None则统计所有文件

    返回:
        元组(子文件夹文件数统计字典, 总文件数)

    异常:
        NotADirectoryError: 如果目录不存在
        Exception: 如果统计过程中出现其他错误
    """
    # 验证输入参数
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"目录不存在: {directory}")

    logger.info(f"统计子文件夹文件数: {directory}")

    stats = {}
    total = 0
    try:
        # 获取所有子文件夹
        subfolders = [d for d in os.listdir(directory)
                     if os.path.isdir(os.path.join(directory, d))]

        # 统计每个子文件夹
        for sub in subfolders:
            folder_path = os.path.join(directory, sub)
            try:
                # 获取文件夹中的文件
                files = os.listdir(folder_path)

                # 根据后缀过滤
                if suffixes:
                    files = [f for f in files
                            if os.path.isfile(os.path.join(folder_path, f))
                            and any(f.lower().endswith(s.lower()) for s in suffixes)]
                else:
                    files = [f for f in files
                            if os.path.isfile(os.path.join(folder_path, f))]

                # 更新统计
                count = len(files)
                stats[sub] = count
                total += count

                logger.debug(f"子文件夹 {sub}: {count} 个文件")

            except Exception as sub_error:
                logger.error(f"统计子文件夹 {sub} 失败: {str(sub_error)}")
                continue

        logger.info(f"统计完成: 共 {total} 个文件")
        return stats, total

    except Exception as e:
        logger.error(f"统计子文件夹文件数失败: {str(e)}")
        raise Exception(f"统计子文件夹文件数失败: {str(e)}")

def delete_large_files(directory: str, size_threshold_mb: float) -> Tuple[int, int, List[str]]:
    """
    删除大文件（按大小）

    参数:
        directory: 目录路径
        size_threshold_mb: 大小阈值(MB)

    返回:
        元组(总文件数, 删除文件数, 错误信息列表)

    异常:
        NotADirectoryError: 如果目录不存在
        ValueError: 如果大小阈值小于等于0
        Exception: 如果删除过程中出现其他错误
    """
    # 验证输入参数
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"目录不存在: {directory}")
    if size_threshold_mb <= 0:
        raise ValueError("大小阈值必须大于0")

    logger.info(f"删除大文件: {directory} (阈值: {size_threshold_mb}MB)")

    size_threshold_bytes = size_threshold_mb * 1024 * 1024
    total_files = 0
    total_deleted = 0
    errors = []

    try:
        # 获取所有子文件夹
        subfolders = [d for d in os.listdir(directory)
                     if os.path.isdir(os.path.join(directory, d))]

        # 处理每个子文件夹
        for sub in subfolders:
            folder_path = os.path.join(directory, sub)
            try:
                # 获取文件夹中的文件
                files = [f for f in os.listdir(folder_path)
                         if os.path.isfile(os.path.join(folder_path, f))]

                # 处理每个文件
                for file in files:
                    total_files += 1
                    file_path = os.path.join(folder_path, file)
                    try:
                        # 检查文件大小
                        if os.path.getsize(file_path) > size_threshold_bytes:
                            os.remove(file_path)
                            total_deleted += 1
                            logger.debug(f"删除大文件: {file_path}")

                    except Exception as file_error:
                        error_msg = f"删除失败: {file_path} 错误: {str(file_error)}"
                        errors.append(error_msg)
                        logger.error(error_msg)

            except Exception as sub_error:
                error_msg = f"处理子文件夹 {sub} 失败: {str(sub_error)}"
                errors.append(error_msg)
                logger.error(error_msg)
                continue

        logger.info(f"删除完成: 共扫描 {total_files} 个文件, 删除 {total_deleted} 个")
        return total_files, total_deleted, errors

    except Exception as e:
        logger.error(f"删除大文件失败: {str(e)}")
        raise Exception(f"删除大文件失败: {str(e)}")

def delete_folders_by_file_count(directory: str, threshold: int) -> Tuple[int, List[str]]:
    """
    删除文件夹（文件数小于阈值）

    参数:
        directory: 目录路径
        threshold: 文件数量阈值

    返回:
        元组(删除文件夹数, 结果信息列表)

    异常:
        NotADirectoryError: 如果目录不存在
        ValueError: 如果阈值小于0
        Exception: 如果删除过程中出现其他错误
    """
    # 验证输入参数
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"目录不存在: {directory}")
    if threshold < 0:
        raise ValueError("阈值不能为负数")

    logger.info(f"删除空文件夹: {directory} (阈值: {threshold})")

    deleted_count = 0
    results = []

    try:
        # 获取所有子文件夹
        subfolders = [d for d in os.listdir(directory)
                     if os.path.isdir(os.path.join(directory, d))]

        # 处理每个子文件夹
        for sub in subfolders:
            folder_path = os.path.join(directory, sub)
            try:
                # 获取文件夹中的文件
                files = [f for f in os.listdir(folder_path)
                         if os.path.isfile(os.path.join(folder_path, f))]

                # 检查文件数量
                if len(files) < threshold:
                    try:
                        # 删除文件夹
                        shutil.rmtree(folder_path)
                        deleted_count += 1
                        result_msg = f"已删除：{sub}（文件数: {len(files)}）"
                        results.append(result_msg)
                        logger.info(result_msg)

                    except Exception as delete_error:
                        error_msg = f"删除失败：{sub} 错误: {str(delete_error)}"
                        results.append(error_msg)
                        logger.error(error_msg)
                else:
                    result_msg = f"保留：{sub}（文件数: {len(files)}）"
                    results.append(result_msg)
                    logger.debug(result_msg)

            except Exception as sub_error:
                error_msg = f"处理子文件夹 {sub} 失败: {str(sub_error)}"
                results.append(error_msg)
                logger.error(error_msg)
                continue

        logger.info(f"删除完成: 共删除 {deleted_count} 个文件夹")
        return deleted_count, results

    except Exception as e:
        logger.error(f"删除文件夹失败: {str(e)}")
        raise Exception(f"删除文件夹失败: {str(e)}")

def delete_files_by_suffix(directory: str, suffixes: List[str]) -> Tuple[int, int, List[str]]:
    """
    删除指定路径下指定后缀的所有文件

    参数:
        directory: 目录路径
        suffixes: 要删除的文件后缀列表

    返回:
        元组(总文件数, 删除文件数, 错误信息列表)

    异常:
        NotADirectoryError: 如果目录不存在
        ValueError: 如果没有提供后缀
        Exception: 如果删除过程中出现其他错误
    """
    # 验证输入参数
    if not os.path.isdir(directory):
        raise NotADirectoryError(f"目录不存在: {directory}")
    if not suffixes:
        raise ValueError("必须提供至少一个后缀")

    logger.info(f"开始删除指定后缀文件: {directory} (后缀: {suffixes})")

    total_files = 0
    deleted_count = 0
    errors = []

    try:
        # 获取所有匹配的文件
        matched_files = get_files_by_suffix(directory, suffixes)
        total_files = len(matched_files)

        # 删除每个匹配的文件
        for file_path in matched_files:
            try:
                os.remove(file_path)
                deleted_count += 1
                logger.debug(f"删除文件: {file_path}")
            except Exception as e:
                error_msg = f"删除文件 {file_path} 失败: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)

        logger.info(f"删除完成: 共扫描 {total_files} 个匹配文件, 成功删除 {deleted_count} 个")
        return total_files, deleted_count, errors

    except Exception as e:
        logger.error(f"删除指定后缀文件失败: {str(e)}")
        raise Exception(f"删除指定后缀文件失败: {str(e)}")


def compare_directories(path1, path2, compare_options):
    """
    对比两个目录的差异

    参数:
        path1: 第一个目录路径
        path2: 第二个目录路径
        compare_options: 对比选项字典，包含:
            - name: 是否比较文件名
            - size: 是否比较文件大小
            - mtime: 是否比较修改时间
            - content: 是否比较文件内容

    返回:
        包含差异的字典，结构为:
        {
            '仅在路径1存在的文件': [...],
            '仅在路径2存在的文件': [...],
            '文件名相同但内容不同': [...],
            '文件名相同但大小不同': [...],
            '文件名相同但修改时间不同': [...]
        }
    """
    differences = {
        '仅在路径1存在的文件': set(),
        '仅在路径2存在的文件': set(),
        '文件名相同但内容不同': set(),
        '文件名相同但大小不同': set(),
        '文件名相同但修改时间不同': set()
    }

    # 获取两个路径下的所有文件相对路径
    path1_files = set()
    for root, _, files in os.walk(path1):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), path1)
            path1_files.add(rel_path)

    path2_files = set()
    for root, _, files in os.walk(path2):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), path2)
            path2_files.add(rel_path)

    # 找出仅在某一方存在的文件
    differences['仅在路径1存在的文件'] = path1_files - path2_files
    differences['仅在路径2存在的文件'] = path2_files - path1_files

    # 找出共同文件中的差异
    common_files = path1_files & path2_files
    for rel_path in common_files:
        file1 = os.path.join(path1, rel_path)
        file2 = os.path.join(path2, rel_path)

        # 比较文件大小
        if compare_options.get('size', False):
            size1 = os.path.getsize(file1)
            size2 = os.path.getsize(file2)
            if size1 != size2:
                differences['文件名相同但大小不同'].add(rel_path)
                continue

        # 比较修改时间
        if compare_options.get('mtime', False):
            mtime1 = os.path.getmtime(file1)
            mtime2 = os.path.getmtime(file2)
            if mtime1 != mtime2:
                differences['文件名相同但修改时间不同'].add(rel_path)
                continue

        # 比较文件内容
        if compare_options.get('content', False):
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                content1 = f1.read()
                content2 = f2.read()
                if content1 != content2:
                    differences['文件名相同但内容不同'].add(rel_path)

    # 转换集合为列表并排序
    for key in differences:
        differences[key] = sorted(differences[key])

    return differences