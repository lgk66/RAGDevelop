import time

import  streamlit as st

from Knowledge_base import KnowledgeBaseService

st.title("知识库更新服务")

uploader_file=st.file_uploader(
    "请上传markdown文件"
    ,type=["md"]
    ,accept_multiple_files=False   #仅允许一个文件的上传
)


#session_state是一个字典
if  "counter" not in st.session_state:
    st.session_state["service"]=KnowledgeBaseService()


if uploader_file  is not None:
    file_name=uploader_file.name
    file_type=uploader_file.type
    file_size=uploader_file.size/1024

    st.subheader(f"文件名：{file_name}")
    st.write(f"格式：{file_type}|大小:{file_size:2f} KB")

    text=uploader_file.getvalue().decode("utf-8")
    with st.spinner("正在载入数据库..."):
        time.sleep(1)

    result=st.session_state["service"].upload_by_str(text,file_name)
    st.write(result)
    # st.write(f"文件内容：\n{text}")
#
#     st.session_state["counter"]+=1
# print(f'上传了{st.session_state["counter"]}个文件')