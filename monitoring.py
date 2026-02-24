import time
import psutil
import os
from datetime import datetime
from typing import Dict, List, Optional

from logger_config import setup_logger

# 创建日志记录器
logger = setup_logger('monitoring')


class SystemMonitor:
    """系统监控类，用于收集系统性能指标"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics = {
            'response_times': [],
            'token_usage': [],
            'retrieval_times': [],
            'document_count': 0,
            'query_count': 0,
            'error_count': 0
        }
        self.process = psutil.Process(os.getpid())
    
    def get_system_metrics(self) -> Dict[str, any]:
        """获取系统级别的性能指标"""
        try:
            # CPU 使用率
            cpu_percent = psutil.cpu_percent(interval=0.1)
            
            # 内存使用情况
            memory = psutil.virtual_memory()
            memory_used = memory.used / (1024 * 1024 * 1024)  # 转换为GB
            memory_total = memory.total / (1024 * 1024 * 1024)  # 转换为GB
            memory_percent = memory.percent
            
            # 磁盘使用情况
            disk = psutil.disk_usage('.')
            disk_used = disk.used / (1024 * 1024 * 1024)  # 转换为GB
            disk_total = disk.total / (1024 * 1024 * 1024)  # 转换为GB
            disk_percent = disk.percent
            
            # 进程使用情况
            process_memory = self.process.memory_info().rss / (1024 * 1024)  # 转换为MB
            process_cpu = self.process.cpu_percent(interval=0.1)
            
            # 系统启动时间
            uptime = (datetime.now() - self.start_time).total_seconds() / 3600  # 转换为小时
            
            return {
                'cpu': {
                    'percent': cpu_percent,
                    'process_percent': process_cpu
                },
                'memory': {
                    'used_gb': round(memory_used, 2),
                    'total_gb': round(memory_total, 2),
                    'percent': memory_percent,
                    'process_mb': round(process_memory, 2)
                },
                'disk': {
                    'used_gb': round(disk_used, 2),
                    'total_gb': round(disk_total, 2),
                    'percent': disk_percent
                },
                'uptime_hours': round(uptime, 2),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"获取系统指标失败: {str(e)}")
            return {
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def record_response_time(self, seconds: float):
        """记录API响应时间"""
        self.metrics['response_times'].append({
            'time': seconds,
            'timestamp': datetime.now().isoformat()
        })
        # 保持列表大小合理
        if len(self.metrics['response_times']) > 1000:
            self.metrics['response_times'] = self.metrics['response_times'][-1000:]
    
    def record_token_usage(self, prompt_tokens: int, completion_tokens: int):
        """记录token使用情况"""
        self.metrics['token_usage'].append({
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': prompt_tokens + completion_tokens,
            'timestamp': datetime.now().isoformat()
        })
        # 保持列表大小合理
        if len(self.metrics['token_usage']) > 1000:
            self.metrics['token_usage'] = self.metrics['token_usage'][-1000:]
    
    def record_retrieval_time(self, seconds: float):
        """记录检索时间"""
        self.metrics['retrieval_times'].append({
            'time': seconds,
            'timestamp': datetime.now().isoformat()
        })
        # 保持列表大小合理
        if len(self.metrics['retrieval_times']) > 1000:
            self.metrics['retrieval_times'] = self.metrics['retrieval_times'][-1000:]
    
    def increment_document_count(self, count: int = 1):
        """增加文档计数"""
        self.metrics['document_count'] += count
    
    def increment_query_count(self, count: int = 1):
        """增加查询计数"""
        self.metrics['query_count'] += count
    
    def increment_error_count(self, count: int = 1):
        """增加错误计数"""
        self.metrics['error_count'] += count
    
    def get_application_metrics(self) -> Dict[str, any]:
        """获取应用级别的性能指标"""
        # 计算平均响应时间
        avg_response_time = 0
        if self.metrics['response_times']:
            avg_response_time = sum(item['time'] for item in self.metrics['response_times']) / len(self.metrics['response_times'])
        
        # 计算平均检索时间
        avg_retrieval_time = 0
        if self.metrics['retrieval_times']:
            avg_retrieval_time = sum(item['time'] for item in self.metrics['retrieval_times']) / len(self.metrics['retrieval_times'])
        
        # 计算总token使用量
        total_tokens = 0
        if self.metrics['token_usage']:
            total_tokens = sum(item['total_tokens'] for item in self.metrics['token_usage'])
        
        return {
            'response_times': {
                'count': len(self.metrics['response_times']),
                'average_seconds': round(avg_response_time, 3),
                'last_10': [item['time'] for item in self.metrics['response_times'][-10:]]
            },
            'retrieval_times': {
                'count': len(self.metrics['retrieval_times']),
                'average_seconds': round(avg_retrieval_time, 3),
                'last_10': [item['time'] for item in self.metrics['retrieval_times'][-10:]]
            },
            'token_usage': {
                'count': len(self.metrics['token_usage']),
                'total': total_tokens,
                'last_10': [item['total_tokens'] for item in self.metrics['token_usage'][-10:]]
            },
            'document_count': self.metrics['document_count'],
            'query_count': self.metrics['query_count'],
            'error_count': self.metrics['error_count'],
            'timestamp': datetime.now().isoformat()
        }
    
    def get_all_metrics(self) -> Dict[str, any]:
        """获取所有性能指标"""
        return {
            'system': self.get_system_metrics(),
            'application': self.get_application_metrics()
        }


# 创建全局监控实例
global_monitor = SystemMonitor()


def get_monitor() -> SystemMonitor:
    """获取全局监控实例"""
    return global_monitor


def monitor_function(func):
    """监控函数执行时间的装饰器"""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            execution_time = time.time() - start_time
            # 这里可以根据函数名决定记录哪种类型的指标
            if 'retrieve' in func.__name__.lower():
                global_monitor.record_retrieval_time(execution_time)
            else:
                global_monitor.record_response_time(execution_time)
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            global_monitor.record_response_time(execution_time)
            global_monitor.increment_error_count()
            raise
    return wrapper
