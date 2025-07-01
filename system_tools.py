"""
系统工具模块
包含日志分析和资源监控功能
"""
import os
import re
import time
import psutil
from datetime import datetime
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import logging
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from io import BytesIO
import numpy as np

logger = logging.getLogger(__name__)


class LogAnalyzer:
    @staticmethod
    def analyze_log_file(log_file: str, time_range: Optional[Tuple[datetime, datetime]] = None) -> Dict:
        """
        分析单个日志文件

        参数:
            log_file: 日志文件路径
            time_range: 可选的时间范围元组(start_time, end_time)

        返回:
            包含分析结果的字典
        """
        if not os.path.isfile(log_file):
            raise FileNotFoundError(f"日志文件不存在: {log_file}")

        error_stats = defaultdict(int)
        warning_stats = defaultdict(int)
        time_series = []
        error_details = []

        # 常见日志模式匹配
        log_pattern = re.compile(
            r'(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3}) '
            r'\[?(?P<level>\w+)\]?.*? - (?P<message>.+)'
        )

        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    match = log_pattern.match(line.strip())
                    if not match:
                        continue

                    log_time = datetime.strptime(match.group('timestamp'), '%Y-%m-%d %H:%M:%S,%f')
                    if time_range and not (time_range[0] <= log_time <= time_range[1]):
                        continue

                    level = match.group('level').upper()
                    message = match.group('message')

                    time_series.append((log_time, level))

                    if level == 'ERROR':
                        error_key = re.sub(r'\d+', '<num>', message.split(':')[0])
                        error_stats[error_key] += 1
                        error_details.append({
                            'timestamp': log_time,
                            'message': message
                        })
                    elif level == 'WARNING':
                        warning_key = re.sub(r'\d+', '<num>', message.split(':')[0])
                        warning_stats[warning_key] += 1

        except Exception as e:
            logger.error(f"分析日志文件失败: {str(e)}")
            raise

        # 生成时间分布数据
        hourly_dist = defaultdict(int)
        for log_time, level in time_series:
            if level == 'ERROR':
                hourly_dist[log_time.hour] += 1

        return {
            'error_stats': dict(sorted(error_stats.items(), key=lambda x: x[1], reverse=True)),
            'warning_stats': dict(sorted(warning_stats.items(), key=lambda x: x[1], reverse=True)),
            'hourly_distribution': dict(sorted(hourly_dist.items())),
            'error_details': sorted(error_details, key=lambda x: x['timestamp']),
            'total_errors': sum(error_stats.values()),
            'total_warnings': sum(warning_stats.values())
        }

    @staticmethod
    def generate_report(analysis_result: Dict, output_dir: str) -> str:
        """
        生成日志分析报告

        参数:
            analysis_result: 分析结果字典
            output_dir: 输出目录

        返回:
            生成的报告文件路径
        """
        os.makedirs(output_dir, exist_ok=True)
        report_file = os.path.join(output_dir, f"log_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")

        # 生成时间分布图表
        fig = plt.figure(figsize=(10, 6))
        hours = list(analysis_result['hourly_distribution'].keys())
        counts = list(analysis_result['hourly_distribution'].values())

        plt.bar(hours, counts)
        plt.xlabel('Hour of Day')
        plt.ylabel('Error Count')
        plt.title('Hourly Error Distribution')

        # 保存图表为图片
        chart_buffer = BytesIO()
        canvas = FigureCanvasAgg(fig)
        canvas.print_png(chart_buffer)
        chart_path = os.path.join(output_dir, 'hourly_distribution.png')
        with open(chart_path, 'wb') as f:
            f.write(chart_buffer.getvalue())
        plt.close(fig)

        # 生成文本报告
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("=== 日志分析报告 ===\n\n")
            f.write(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"总错误数: {analysis_result['total_errors']}\n")
            f.write(f"总警告数: {analysis_result['total_warnings']}\n\n")

            f.write("=== 错误统计 ===\n")
            for error, count in analysis_result['error_stats'].items():
                f.write(f"{error}: {count}次\n")

            f.write("\n=== 警告统计 ===\n")
            for warning, count in analysis_result['warning_stats'].items():
                f.write(f"{warning}: {count}次\n")

            f.write("\n=== 最近错误详情 ===\n")
            for error in analysis_result['error_details'][-10:]:
                f.write(f"{error['timestamp']} - {error['message']}\n")

            f.write(f"\n错误时间分布图表已保存到: {chart_path}\n")

        return report_file


class SystemMonitor:
    def __init__(self, update_interval: float = 1.0):
        self.update_interval = update_interval
        self.running = False
        self.history = {
            'cpu': [],
            'memory': [],
            'disk': [],
            'network': []
        }
        self.max_history = 300  # 保留300个数据点

    def start_monitoring(self):
        """开始监控系统资源"""
        self.running = True
        logger.info("系统资源监控已启动")

    def stop_monitoring(self):
        """停止监控"""
        self.running = False
        logger.info("系统资源监控已停止")

    def get_system_stats(self) -> Dict:
        """获取当前系统状态"""
        # CPU使用率
        cpu_percent = psutil.cpu_percent(interval=None)
        cpu_percent_per_core = psutil.cpu_percent(interval=None, percpu=True)

        # 内存使用
        mem = psutil.virtual_memory()

        # 磁盘使用
        disk_usage = psutil.disk_usage('/')
        disk_io = psutil.disk_io_counters()

        # 网络
        net_io = psutil.net_io_counters()

        # 进程数
        process_count = len(psutil.pids())

        stats = {
            'timestamp': datetime.now(),
            'cpu': {
                'total': cpu_percent,
                'cores': cpu_percent_per_core,
                'count': psutil.cpu_count()
            },
            'memory': {
                'total': mem.total,
                'available': mem.available,
                'used': mem.used,
                'percent': mem.percent
            },
            'disk': {
                'total': disk_usage.total,
                'used': disk_usage.used,
                'free': disk_usage.free,
                'percent': disk_usage.percent,
                'read_bytes': disk_io.read_bytes,
                'write_bytes': disk_io.write_bytes
            },
            'network': {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            },
            'process': {
                'count': process_count
            }
        }

        # 添加到历史记录
        self._add_to_history(stats)
        return stats

    def _add_to_history(self, stats: Dict):
        """添加统计数据到历史记录"""
        # CPU
        self.history['cpu'].append((stats['timestamp'], stats['cpu']['total']))
        if len(self.history['cpu']) > self.max_history:
            self.history['cpu'].pop(0)

        # 内存
        self.history['memory'].append((stats['timestamp'], stats['memory']['percent']))
        if len(self.history['memory']) > self.max_history:
            self.history['memory'].pop(0)

        # 磁盘
        self.history['disk'].append((stats['timestamp'], stats['disk']['percent']))
        if len(self.history['disk']) > self.max_history:
            self.history['disk'].pop(0)

        # 网络
        if len(self.history['network']) > 0:
            last = self.history['network'][-1]
            time_diff = (stats['timestamp'] - last[0]).total_seconds()
            if time_diff > 0:
                sent_speed = (stats['network']['bytes_sent'] - last[1]) / time_diff
                recv_speed = (stats['network']['bytes_recv'] - last[2]) / time_diff
            else:
                sent_speed = 0
                recv_speed = 0
        else:
            sent_speed = 0
            recv_speed = 0

        self.history['network'].append((
            stats['timestamp'],
            stats['network']['bytes_sent'],
            stats['network']['bytes_recv'],
            sent_speed,
            recv_speed
        ))
        if len(self.history['network']) > self.max_history:
            self.history['network'].pop(0)

    def generate_resource_charts(self, output_dir: str) -> Dict:
        """生成资源使用图表"""
        os.makedirs(output_dir, exist_ok=True)
        chart_paths = {}

        # CPU使用率图表
        if self.history['cpu']:
            timestamps, values = zip(*self.history['cpu'])
            fig = plt.figure(figsize=(10, 4))
            plt.plot(timestamps, values, label='CPU Usage')
            plt.xlabel('Time')
            plt.ylabel('Percentage')
            plt.title('CPU Usage History')
            plt.ylim(0, 100)
            plt.grid(True)

            cpu_chart_path = os.path.join(output_dir, 'cpu_usage.png')
            fig.savefig(cpu_chart_path)
            plt.close(fig)
            chart_paths['cpu'] = cpu_chart_path

        # 内存使用图表
        if self.history['memory']:
            timestamps, values = zip(*self.history['memory'])
            fig = plt.figure(figsize=(10, 4))
            plt.plot(timestamps, values, label='Memory Usage')
            plt.xlabel('Time')
            plt.ylabel('Percentage')
            plt.title('Memory Usage History')
            plt.ylim(0, 100)
            plt.grid(True)

            mem_chart_path = os.path.join(output_dir, 'memory_usage.png')
            fig.savefig(mem_chart_path)
            plt.close(fig)
            chart_paths['memory'] = mem_chart_path

        # 磁盘使用图表
        if self.history['disk']:
            timestamps, values = zip(*self.history['disk'])
            fig = plt.figure(figsize=(10, 4))
            plt.plot(timestamps, values, label='Disk Usage')
            plt.xlabel('Time')
            plt.ylabel('Percentage')
            plt.title('Disk Usage History')
            plt.ylim(0, 100)
            plt.grid(True)

            disk_chart_path = os.path.join(output_dir, 'disk_usage.png')
            fig.savefig(disk_chart_path)
            plt.close(fig)
            chart_paths['disk'] = disk_chart_path

        # 网络流量图表
        if len(self.history['network']) > 1:
            timestamps = [x[0] for x in self.history['network']]
            sent_speeds = [x[3] / 1024 for x in self.history['network'][1:]]  # KB/s
            recv_speeds = [x[4] / 1024 for x in self.history['network'][1:]]  # KB/s

            fig = plt.figure(figsize=(10, 4))
            plt.plot(timestamps[1:], sent_speeds, label='Upload Speed')
            plt.plot(timestamps[1:], recv_speeds, label='Download Speed')
            plt.xlabel('Time')
            plt.ylabel('Speed (KB/s)')
            plt.title('Network Traffic')
            plt.grid(True)
            plt.legend()

            net_chart_path = os.path.join(output_dir, 'network_traffic.png')
            fig.savefig(net_chart_path)
            plt.close(fig)
            chart_paths['network'] = net_chart_path

        return chart_paths