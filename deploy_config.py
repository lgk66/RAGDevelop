import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 部署配置类
class DeployConfig:
    """部署配置类，用于管理环境变量和部署参数"""
    
    def __init__(self):
        # API密钥
        self.BAI_LIAN_API_KEY = os.getenv('BAI_LIAN_API_KEY', 'sk-cff8fd7e3eb7463a9a4ed47d0a8c4957')
        
        # 模型配置
        self.EMBEDDING_MODEL_NAME = os.getenv('EMBEDDING_MODEL_NAME', 'text-embedding-v4')
        self.CHAT_MODEL_NAME = os.getenv('CHAT_MODEL_NAME', 'qwen3-max')
        
        # 向量存储配置
        self.COLLECTION_NAME = os.getenv('COLLECTION_NAME', 'rag')
        self.PERSIST_DIRECTORY = os.getenv('PERSIST_DIRECTORY', './chroma_db')
        
        # 文档处理配置
        self.CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', '1500'))
        self.CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', '150'))
        self.MAX_SPLIT_CHAR_NUMBER = int(os.getenv('MAX_SPLIT_CHAR_NUMBER', '5000'))
        
        # 检索配置
        self.SIMILARITY_THRESHOLD = int(os.getenv('SIMILARITY_THRESHOLD', '5'))
        
        # 服务配置
        self.HOST = os.getenv('HOST', '0.0.0.0')
        self.PORT = int(os.getenv('PORT', '8501'))
        self.DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
        
        # 安全配置
        self.ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', '*').split(',')
        self.API_KEY_REQUIRED = os.getenv('API_KEY_REQUIRED', 'False').lower() == 'true'
        self.SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
        
        # 日志配置
        self.LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
        self.LOG_DIR = os.getenv('LOG_DIR', './logs')
        
        # 监控配置
        self.ENABLE_MONITORING = os.getenv('ENABLE_MONITORING', 'True').lower() == 'true'
        self.MONITORING_INTERVAL = int(os.getenv('MONITORING_INTERVAL', '60'))  # 秒
    
    def get_config_dict(self):
        """获取配置字典"""
        return {
            'api_keys': {
                'bai_lian_api_key': self.BAI_LIAN_API_KEY
            },
            'models': {
                'embedding_model_name': self.EMBEDDING_MODEL_NAME,
                'chat_model_name': self.CHAT_MODEL_NAME
            },
            'vector_store': {
                'collection_name': self.COLLECTION_NAME,
                'persist_directory': self.PERSIST_DIRECTORY
            },
            'document_processing': {
                'chunk_size': self.CHUNK_SIZE,
                'chunk_overlap': self.CHUNK_OVERLAP,
                'max_split_char_number': self.MAX_SPLIT_CHAR_NUMBER
            },
            'retrieval': {
                'similarity_threshold': self.SIMILARITY_THRESHOLD
            },
            'server': {
                'host': self.HOST,
                'port': self.PORT,
                'debug': self.DEBUG
            },
            'security': {
                'allowed_origins': self.ALLOWED_ORIGINS,
                'api_key_required': self.API_KEY_REQUIRED,
                'secret_key': self.SECRET_KEY
            },
            'logging': {
                'log_level': self.LOG_LEVEL,
                'log_dir': self.LOG_DIR
            },
            'monitoring': {
                'enable_monitoring': self.ENABLE_MONITORING,
                'monitoring_interval': self.MONITORING_INTERVAL
            }
        }

# 创建全局配置实例
config = DeployConfig()

# 导出配置
def get_config():
    """获取配置实例"""
    return config

# 示例用法
if __name__ == '__main__':
    print("部署配置:")
    print(config.get_config_dict())
