import hashlib
import os
import config_data as config
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import DashScopeEmbeddings
from datetime import datetime
import logging

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_md5(md5_str:str):
    if not os.path.exists(config.md5_path):
        open(config.md5_path,"w",encoding="utf-8").close()
        return False
    else:
        with open(config.md5_path, "r", encoding="utf-8") as f:
            for line in  f.readlines():
                line=line.strip()     #处理字符串前后的空格和回车
                if line==md5_str:
                    return True    #已经处理过了
    return False

def save_md5(md5_str:str):
    with open(config.md5_path,"a",encoding="utf-8") as f:
        f.write(md5_str+"\n")

def get_string_md5(input_str:str,encoding="utf-8"):
    #将字符串转换为md5字符串

    #将字符串转换为bytes字节数组
    str_bytes=input_str.encode(encoding= encoding)

    #创建md5对象
    md5_obj=hashlib.md5()
    md5_obj.update(str_bytes)     #更新md5对象
    md5_hex=md5_obj.hexdigest()     #获取md5字符串

    return  md5_hex
class KnowledgeBaseService(object):
    def __init__(self):
        #如果文件不存在创建否则跳过
        os.makedirs(config.persist_directory,exist_ok=True)

        embedding_function = DashScopeEmbeddings(
            model="text-embedding-v4",
            dashscope_api_key=config.BAI_LIAN_API_KEY
        )
        
        self.chroma=Chroma(
            collection_name=config.collection_name,     #数据库表名
            embedding_function=embedding_function,
            persist_directory=config.persist_directory,
            #向量维度
        )
        self.spliter=RecursiveCharacterTextSplitter(
            chunk_size=config.chunk_size,
            chunk_overlap=config.chunk_overlap,
            separators=config.separators,
            length_function=len      #使用Python自带的len函数做长度统计的依据
        )

    """将传入的字符串进行向量化  存入向量数据库中"""
    def upload_by_str(self,data:str,filename):
        md5_hex = get_string_md5(data)
        if check_md5(md5_hex):
            return "[跳过]内容已经存在知识库中"
        if len(data)>config.max_split_char_number:
            knowledge_chunks=self.spliter.split_text(data)
        else:
            knowledge_chunks=[data]
        metadata={
            "source":filename,
            "create_time":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "operator": "小刘"
        }
        #将数据加入向量库中
        self.chroma.add_texts(
            knowledge_chunks,
            metadatas=[metadata for _ in knowledge_chunks]
        )

        save_md5(md5_hex)

        return "[成功]内容已经载入向量库"

if __name__ == '__main__':
    # r1=get_string_md5("周杰伦")
    # r2=get_string_md5("周杰伦")
    # r3=get_string_md5("蔡依林")
    # print(r1,r2,r3)
    # save_md5("060545170130c81c5505fda49b58d018")
    # print(check_md5("060545170130c81c5505fda49b58d018"))
    service=KnowledgeBaseService()
    service.upload_by_str("周杰伦","周杰伦.txt")
