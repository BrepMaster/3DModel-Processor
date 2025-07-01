"""
数据集处理模块
包含数据集划分和分类的核心逻辑
"""

import os
import random
import logging
import shutil
from typing import List, Tuple, Optional, Set, Dict
from pathlib import Path
from file_operations import get_files_by_suffix

# 配置日志记录
logger = logging.getLogger(__name__)

def organize_files_by_txt(base_path: str, train_txt: str, test_txt: str, output_base_path: str) -> Tuple[int, int]:
    """
    根据train.txt和test.txt文件组织文件到train和test文件夹

    参数:
        base_path: 原始文件所在的基础路径
        train_txt: train.txt文件路径
        test_txt: test.txt文件路径
        output_base_path: 输出基础路径

    返回:
        元组(训练集文件数, 测试集文件数)

    异常:
        NotADirectoryError: 如果基础路径不存在
        FileNotFoundError: 如果train.txt或test.txt不存在
        Exception: 如果处理过程中出现其他错误
    """
    # 验证输入参数
    if not os.path.isdir(base_path):
        raise NotADirectoryError(f"基础路径不存在: {base_path}")
    if not os.path.isfile(train_txt):
        raise FileNotFoundError(f"train.txt文件不存在: {train_txt}")
    if not os.path.isfile(test_txt):
        raise FileNotFoundError(f"test.txt文件不存在: {test_txt}")

    logger.info(f"开始组织文件: {base_path} -> {output_base_path}")

    try:
        # 读取train.txt和test.txt文件
        with open(train_txt, 'r', encoding='utf-8') as f:
            train_files = {line.strip() for line in f}
        with open(test_txt, 'r', encoding='utf-8') as f:
            test_files = {line.strip() for line in f}

        train_count = 0
        test_count = 0

        # 遍历基础路径下的所有文件夹
        for folder_name in os.listdir(base_path):
            folder_path = os.path.join(base_path, folder_name)
            if not os.path.isdir(folder_path):
                continue

            # 创建输出文件夹
            train_folder = os.path.join(output_base_path, folder_name, 'train')
            test_folder = os.path.join(output_base_path, folder_name, 'test')
            os.makedirs(train_folder, exist_ok=True)
            os.makedirs(test_folder, exist_ok=True)

            # 处理文件夹中的文件
            for file_name in os.listdir(folder_path):
                file_base_name = os.path.splitext(file_name)[0]
                parts = file_base_name.split('_')

                # 提取文件关键标识(前两部分)
                file_key = '_'.join(parts[:2]) if len(parts) >= 2 else file_base_name

                source_path = os.path.join(folder_path, file_name)

                if file_key in train_files:
                    shutil.copy2(source_path, train_folder)
                    train_count += 1
                elif file_key in test_files:
                    shutil.copy2(source_path, test_folder)
                    test_count += 1

        logger.info(f"文件组织完成: 训练集 {train_count} 个, 测试集 {test_count} 个")
        return train_count, test_count

    except Exception as e:
        logger.error(f"文件组织失败: {str(e)}")
        raise Exception(f"文件组织失败: {str(e)}")

def split_dataset(input_dir: str, output_dir: str, test_ratio: float) -> Tuple[List[str], List[str]]:
    """
    划分数据集为训练集和测试集

    参数:
        input_dir: 输入目录路径
        output_dir: 输出目录路径
        test_ratio: 测试集比例(0-1之间)

    返回:
        元组(训练集文件名列表, 测试集文件名列表)

    异常:
        NotADirectoryError: 如果输入目录不存在
        ValueError: 如果测试集比例不在0-1之间
        Exception: 如果划分过程中出现其他错误
    """
    # 验证输入参数
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"输入目录不存在: {input_dir}")
    if not 0 < test_ratio < 1:
        raise ValueError("测试集比例必须在0和1之间")

    logger.info(f"开始划分数据集: {input_dir} (测试比例: {test_ratio})")

    try:
        # 获取所有类别目录
        class_dirs = [d for d in os.listdir(input_dir)
                     if os.path.isdir(os.path.join(input_dir, d))]
        train_list = []
        test_list = []

        # 处理每个类别
        for class_dir in class_dirs:
            class_path = os.path.join(input_dir, class_dir)
            try:
                # 获取类别下的所有文件
                files = [f for f in os.listdir(class_path)
                         if os.path.isfile(os.path.join(class_path, f))]

                # 跳过文件数不足的类别
                if len(files) < 2:
                    logger.warning(f"类别 {class_dir} 文件数不足2个，跳过")
                    continue

                # 计算测试集大小
                test_size = max(1, int(test_ratio * len(files))) if len(files) > 10 else 1

                # 随机选择测试集文件
                test_files = random.sample(files, test_size)

                # 分配训练集和测试集
                for file in files:
                    name = os.path.splitext(file)[0]
                    if file in test_files:
                        test_list.append(name)
                    else:
                        train_list.append(name)

            except Exception as class_error:
                logger.error(f"处理类别 {class_dir} 时出错: {str(class_error)}")
                continue

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 写入训练集和测试集文件
        train_file = os.path.join(output_dir, 'train.txt')
        test_file = os.path.join(output_dir, 'test.txt')

        try:
            with open(train_file, 'w', encoding='utf-8') as train_f:
                train_f.write('\n'.join(train_list))

            with open(test_file, 'w', encoding='utf-8') as test_f:
                test_f.write('\n'.join(test_list))

        except IOError as io_error:
            logger.error(f"写入训练/测试文件失败: {str(io_error)}")
            raise Exception(f"写入训练/测试文件失败: {str(io_error)}")

        logger.info(f"数据集划分完成: 训练集 {len(train_list)} 个, 测试集 {len(test_list)} 个")
        return train_list, test_list

    except Exception as e:
        logger.error(f"数据集划分失败: {str(e)}")
        raise Exception(f"数据集划分失败: {str(e)}")

def classify_files_by_name(input_dir: str, output_dir: str) -> int:
    """
    根据文件名将文件分类到子文件夹

    参数:
        input_dir: 输入目录路径
        output_dir: 输出目录路径

    返回:
        int: 成功处理的文件数量

    异常:
        NotADirectoryError: 如果输入目录不存在
        Exception: 如果分类过程中出现其他错误
    """
    # 验证输入参数
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"输入目录不存在: {input_dir}")

    logger.info(f"开始按文件名分类文件: {input_dir}")

    processed = 0
    try:
        # 获取所有文件
        files = [f for f in os.listdir(input_dir)
                 if os.path.isfile(os.path.join(input_dir, f))]

        # 处理每个文件
        for filename in files:
            try:
                # 检查文件名是否包含下划线
                if '_' in filename:
                    # 提取类别名(文件名中最后一个下划线前的部分)
                    category = '_'.join(filename.split('_')[:-1])

                    # 创建目标文件夹
                    dst_folder = os.path.join(output_dir, category)
                    os.makedirs(dst_folder, exist_ok=True)

                    # 复制文件
                    src_path = os.path.join(input_dir, filename)
                    dst_path = os.path.join(dst_folder, filename)
                    shutil.copy2(src_path, dst_path)

                    processed += 1
                    logger.debug(f"分类文件: {filename} -> {category}")

            except Exception as file_error:
                logger.error(f"处理文件 {filename} 失败: {str(file_error)}")
                continue

        logger.info(f"文件分类完成: 共处理 {processed} 个文件")
        return processed

    except Exception as e:
        logger.error(f"文件分类失败: {str(e)}")
        raise Exception(f"文件分类失败: {str(e)}")

def copy_files_by_suffix(input_dir: str, output_dir: str, suffixes: List[str]) -> int:
    """
    按后缀复制文件到目标目录

    参数:
        input_dir: 输入目录路径
        output_dir: 输出目录路径
        suffixes: 文件后缀列表

    返回:
        int: 复制的文件数量

    异常:
        NotADirectoryError: 如果输入目录不存在
        ValueError: 如果没有提供后缀
        Exception: 如果复制过程中出现其他错误
    """
    # 验证输入参数
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"输入目录不存在: {input_dir}")
    if not suffixes:
        raise ValueError("必须提供至少一个后缀")

    logger.info(f"开始按后缀复制文件: {input_dir} (后缀: {suffixes})")

    try:
        # 获取匹配的文件
        matched_files = get_files_by_suffix(input_dir, suffixes)

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        # 复制每个文件
        for src in matched_files:
            try:
                shutil.copy2(src, os.path.join(output_dir, os.path.basename(src)))
                logger.debug(f"复制文件: {src}")
            except Exception as copy_error:
                logger.error(f"复制文件 {src} 失败: {str(copy_error)}")
                continue

        logger.info(f"文件复制完成: 共复制 {len(matched_files)} 个文件")
        return len(matched_files)

    except Exception as e:
        logger.error(f"按后缀复制文件失败: {str(e)}")
        raise Exception(f"按后缀复制文件失败: {str(e)}")


def analyze_dataset_balance(input_dir: str, output_dir: str = None) -> Tuple[Dict[str, int], str]:
    """
    分析数据集类别平衡情况

    参数:
        input_dir: 输入目录路径(应包含按类别组织的子文件夹)
        output_dir: 可选输出目录路径(用于保存分析报告)

    返回:
        元组(类别统计字典, 分析报告文本)

    异常:
        NotADirectoryError: 如果输入目录不存在
        Exception: 如果分析过程中出现错误
    """
    # 验证输入参数
    if not os.path.isdir(input_dir):
        raise NotADirectoryError(f"输入目录不存在: {input_dir}")

    logger.info(f"开始分析数据集平衡性: {input_dir}")

    try:
        # 获取所有类别目录
        class_dirs = [d for d in os.listdir(input_dir)
                      if os.path.isdir(os.path.join(input_dir, d))]

        if not class_dirs:
            raise ValueError("输入目录中没有找到任何类别子文件夹")

        # 统计每个类别的文件数量
        class_stats = {}
        for class_dir in class_dirs:
            class_path = os.path.join(input_dir, class_dir)
            files = [f for f in os.listdir(class_path)
                     if os.path.isfile(os.path.join(class_path, f))]
            class_stats[class_dir] = len(files)

        # 生成分析报告
        total_samples = sum(class_stats.values())
        avg_samples = total_samples / len(class_stats) if class_stats else 0

        report_lines = [
            "数据集平衡性分析报告",
            "=" * 40,
            f"总类别数: {len(class_stats)}",
            f"总样本数: {total_samples}",
            f"平均每类样本数: {avg_samples:.1f}",
            "\n类别分布详情:",
            "-" * 40
        ]

        # 添加每个类别的统计信息
        for class_name, count in sorted(class_stats.items(), key=lambda x: x[1], reverse=True):
            percentage = (count / total_samples) * 100 if total_samples > 0 else 0
            report_lines.append(f"{class_name}: {count} 个样本 ({percentage:.1f}%)")

        # 计算不平衡度指标
        if class_stats:
            max_count = max(class_stats.values())
            min_count = min(class_stats.values())
            imbalance_ratio = max_count / min_count if min_count > 0 else float('inf')

            report_lines.extend([
                "\n不平衡度分析:",
                "-" * 40,
                f"最多样本的类别: {max_count} 个样本",
                f"最少样本的类别: {min_count} 个样本",
                f"不平衡比例: {imbalance_ratio:.1f}:1",
                "\n评估建议:"
            ])

            if imbalance_ratio < 2:
                report_lines.append("✅ 数据集较为平衡 (不平衡比例 < 2:1)")
            elif imbalance_ratio < 10:
                report_lines.append("⚠️ 数据集存在中等不平衡 (2:1 ≤ 不平衡比例 < 10:1)")
            else:
                report_lines.append("❌ 数据集严重不平衡 (不平衡比例 ≥ 10:1)")
                report_lines.append("建议: 考虑使用过采样、欠采样或类别权重等技术处理不平衡问题")

        report_text = "\n".join(report_lines)

        # 如果需要保存报告
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
            report_file = os.path.join(output_dir, "dataset_balance_report.txt")
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            logger.info(f"分析报告已保存到: {report_file}")

        logger.info(f"数据集平衡性分析完成")
        return class_stats, report_text

    except Exception as e:
        logger.error(f"数据集平衡性分析失败: {str(e)}")
        raise Exception(f"数据集平衡性分析失败: {str(e)}")