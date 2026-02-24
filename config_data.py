
md5_path="./md5.text"
collection_name="rag"
persist_directory="./chroma_db"




#spliter
chunk_size=150
chunk_overlap=10
separators=["\n\n","\n","。","？","！","；","，","、",":",";"]
max_split_char_number=5000


BAI_LIAN_API_KEY="sk-cff8fd7e3eb7463a9a4ed47d0a8c4957"
embedding_model_name="text-embedding-v4"
chat_model_name="qwen3.5-plus"

session_config = {
    "configurable": {
        "session_id": "user_001",
    }
}

#相识度检索阈值
similarity_threshold=3    #检索匹配返回的文档数量