from langchain_chroma import Chroma
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
import config_data as config
import os
from logger_config import setup_logger

# 创建日志记录器
logger = setup_logger('vector_store')

class VectorStoreService(object):
    def __init__(self, embedding):
        try:
            logger.info("初始化VectorStoreService...")
            self.embedding = embedding
            logger.info(f"使用模型: {config.embedding_model_name}")
            logger.info(f"向量库: {config.collection_name}")
            logger.info(f"存储路径: {config.persist_directory}")
            
            # 确保存储目录存在
            os.makedirs(config.persist_directory, exist_ok=True)
            logger.info("存储目录已准备就绪")
            
            # 初始化向量存储
            logger.info("初始化Chroma向量存储...")
            self.vector_store = Chroma(
                collection_name=config.collection_name,
                embedding_function=self.embedding,
                persist_directory=config.persist_directory
            )
            logger.info("Chroma向量存储初始化成功")
            
            # 初始化BM25检索器
            logger.info("初始化BM25检索器...")
            self.bm25_retriever = self._init_bm25_retriever()
            if self.bm25_retriever:
                logger.info("BM25检索器初始化成功")
            else:
                logger.warning("BM25检索器初始化失败，将仅使用向量检索")
            
            logger.info("VectorStoreService初始化完成")
        except Exception as e:
            logger.error(f"VectorStoreService初始化失败: {str(e)}")
            raise

    def _init_bm25_retriever(self):
        """初始化BM25检索器，用于关键词检索"""
        try:
            # 从向量库中获取所有文档
            logger.debug("从向量库中获取文档...")
            docs = self.vector_store.get()
            texts = docs.get('documents', [])
            
            logger.info(f"获取到 {len(texts)} 个文档")
            
            if not texts:
                logger.warning("向量库中无文档，无法初始化BM25检索器")
                return None
            
            # 为BM25创建文档列表
            logger.debug("创建文档对象列表...")
            from langchain_core.documents import Document
            doc_objects = []
            for i, text in enumerate(texts):
                metadata = docs.get('metadatas', [{}])[i] if i < len(docs.get('metadatas', [])) else {}
                doc_objects.append(Document(page_content=text, metadata=metadata))
            
            logger.info(f"创建了 {len(doc_objects)} 个文档对象")
            
            # 创建BM25检索器
            logger.debug("创建BM25检索器...")
            bm25_retriever = BM25Retriever.from_documents(doc_objects)
            logger.info("BM25检索器创建成功")
            
            return bm25_retriever
        except Exception as e:
            logger.error(f"初始化BM25检索器失败: {str(e)}")
            return None

    def get_retriever(self):
        """获取混合检索器，结合向量检索和BM25检索"""
        try:
            logger.info("获取检索器...")
            # 计算检索数量
            k_value = config.similarity_threshold * 2
            logger.info(f"设置检索数量: {k_value}")
            
            # 初始化向量检索器
            logger.debug("初始化向量检索器...")
            vector_retriever = self.vector_store.as_retriever(
                search_kwargs={"k": k_value}  # 获取更多结果用于重排序
            )
            logger.debug("向量检索器初始化成功")
            
            if self.bm25_retriever:
                # 创建集成检索器
                logger.info("创建混合检索器...")
                ensemble_retriever = EnsembleRetriever(
                    retrievers=[vector_retriever, self.bm25_retriever],
                    weights=[0.7, 0.3]  # 向量检索权重更高
                )
                logger.info("混合检索器创建成功")
                return ensemble_retriever
            else:
                logger.warning("BM25检索器不可用，返回向量检索器")
                return vector_retriever
        except Exception as e:
            logger.error(f"获取检索器失败: {str(e)}")
            # 降级为仅使用向量检索
            try:
                logger.info("降级为仅使用向量检索...")
                return self.vector_store.as_retriever(
                    search_kwargs={"k": config.similarity_threshold}
                )
            except Exception as fallback_error:
                logger.error(f"降级失败: {str(fallback_error)}")
                raise

    def get_hybrid_retriever(self, k=5):
        """获取混合检索器，支持更灵活的参数配置"""
        try:
            logger.info(f"获取混合检索器，k={k}...")
            
            # 初始化向量检索器
            logger.debug("初始化向量检索器...")
            vector_retriever = self.vector_store.as_retriever(
                search_kwargs={"k": k}
            )
            logger.debug("向量检索器初始化成功")
            
            if self.bm25_retriever:
                logger.info("创建混合检索器...")
                ensemble_retriever = EnsembleRetriever(
                    retrievers=[vector_retriever, self.bm25_retriever],
                    weights=[0.7, 0.3]
                )
                logger.info("混合检索器创建成功")
                return ensemble_retriever
            else:
                logger.warning("BM25检索器不可用，返回向量检索器")
                return vector_retriever
        except Exception as e:
            logger.error(f"获取混合检索器失败: {str(e)}")
            # 降级为仅使用向量检索
            try:
                logger.info("降级为仅使用向量检索...")
                return self.vector_store.as_retriever(
                    search_kwargs={"k": k}
                )
            except Exception as fallback_error:
                logger.error(f"降级失败: {str(fallback_error)}")
                raise




if __name__ == '__main__':
    from langchain_community.embeddings   import  DashScopeEmbeddings
    retriever=VectorStoreService(DashScopeEmbeddings(model=config.embedding_model_name,dashscope_api_key=config.BAI_LIAN_API_KEY)).get_retriever()
    res=retriever.invoke("我的体重180斤，尺码推荐？")
    print(res)





