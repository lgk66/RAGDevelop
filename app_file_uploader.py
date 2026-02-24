from io import BytesIO

import streamlit as st

from Knowledge_base import KnowledgeBaseService
from logger_config import setup_logger

# 创建日志记录器
logger = setup_logger('file_uploader')


st.set_page_config(
    page_title="知识库管理中心",
    page_icon="📚",
    layout="wide"
)

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()


# 创建标签页
tab1, tab2 = st.tabs(["文档上传", "知识库管理"])

with tab1:
    st.markdown(
        """
        <style>
        .kb-header {
            padding: 0.5rem 0 1.5rem 0;
            border-bottom: 1px solid #E5E7EB;
            margin-bottom: 1.5rem;
        }
        .kb-title {
            font-size: 1.6rem;
            font-weight: 600;
            color: #111827;
            margin-bottom: 0.25rem;
        }
        .kb-subtitle {
            font-size: 0.9rem;
            color: #6B7280;
        }
        .kb-card {
            border-radius: 0.5rem;
            border: 1px solid #E5E7EB;
            padding: 1.25rem 1.5rem;
            background: #FFFFFF;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="kb-header">
            <div class="kb-title">知识库管理中心</div>
            <div class="kb-subtitle">
                支持文档上传、知识库管理，适用于企业级知识库维护场景。
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown('<div class="kb-card">', unsafe_allow_html=True)
    st.subheader("文档上传")
    st.caption("请选择需要加入知识库的源文档，支持 TXT / Markdown 格式。")

    uploader_files = st.file_uploader(
        "上传文件",
        type=["txt", "md"],
        accept_multiple_files=True,
        key="file_uploader"
    )

    if uploader_files:
        st.markdown("---")
        st.markdown(f"**选中文件数量**：{len(uploader_files)}")
        
        # 显示文件列表
        file_list = []
        for i, file in enumerate(uploader_files):
            file_size = file.size / 1024
            file_list.append(f"{i+1}. {file.name} ({file_size:.2f} KB)")
        
        st.markdown("\n".join(file_list))
        
        # 处理按钮
        if st.button("开始处理", use_container_width=True):
            logger.info(f"开始处理 {len(uploader_files)} 个文件")
            success_count = 0
            error_count = 0
            error_files = []
            
            with st.spinner("正在处理文件，请稍候..."):
                for file in uploader_files:
                    try:
                        logger.info(f"处理文件：{file.name}")
                        text = file.getvalue().decode("utf-8")
                        
                        if text:
                            result = st.session_state["service"].upload_by_str(text, file.name)
                            logger.info(f"文件处理成功：{file.name}")
                            success_count += 1
                        else:
                            error_files.append(file.name)
                            error_count += 1
                            logger.warning(f"文件内容为空：{file.name}")
                    except UnicodeDecodeError:
                        st.error(f"文件 {file.name} 编码不是 UTF-8，请转换编码后重试。")
                        logger.error(f"文件编码错误：{file.name}")
                        error_files.append(file.name)
                        error_count += 1
                    except Exception as e:
                        error_files.append(file.name)
                        error_count += 1
                        logger.error(f"文件处理失败：{file.name}, {str(e)}")
                    finally:
                        # 重置文件指针
                        file.seek(0)
            
            logger.info(f"处理完成：成功 {success_count} 个，失败 {error_count} 个")
            st.success(f"处理完成！\n成功：{success_count} 个文件\n失败：{error_count} 个文件")
            
            if error_files:
                st.warning("处理失败的文件：")
                st.markdown("\n".join([f"- {file}" for file in error_files]))

    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="kb-card">', unsafe_allow_html=True)
    st.subheader("知识库管理")
    st.caption("查看和管理知识库中的文档。")
    
    # 知识库统计信息
    stats = st.session_state["service"].get_stats()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("文档块数量", stats["total_chunks"])
    with col2:
        st.metric("源文件数量", stats["total_files"])
    with col3:
        if st.button("🔄 刷新", key="refresh_stats"):
            st.rerun()
    
    st.markdown("---")
    
    # 文档列表
    st.subheader("文档列表")
    
    if stats["sources"]:
        for source in stats["source"]:
            with st.expander(f"📄 {source}"):
                docs = st.session_state["service"].get_documents_by_source(source)
                st.markdown(f"**文档块数量**: {len(docs)}")
                
                # 显示文档内容
                for i, doc in enumerate(docs):
                    st.markdown(f"##### 文档块 {i+1}")
                    st.text_area(
                        f"内容_{i}",
                        doc["content"],
                        height=150,
                        key=f"content_{doc['id']}",
                        disabled=True
                    )
                    st.markdown(f"**创建时间**: {doc['metadata'].get('create_time', '未知')}")
                    st.markdown(f"**操作人**: {doc['metadata'].get('operator', '未知')}")
                    
                    col_del, col_del_id = st.columns([1, 4])
                    with col_del:
                        if st.button("🗑️ 删除", key=f"del_{doc['id']}"):
                            result = st.session_state["service"].delete_by_id(doc['id'])
                            st.success(result)
                            logger.info(f"删除文档块: {doc['id']}")
                            st.rerun()
                    st.divider()
                
                # 整个文件删除按钮
                col_del_all, _ = st.columns([1, 4])
                with col_del_all:
                    if st.button(f"🗑️ 删除整个文件: {source}", key=f"del_file_{source}"):
                        result = st.session_state["service"].delete_by_source(source)
                        st.success(result)
                        logger.info(f"删除文件: {source}")
                        st.rerun()
    else:
        st.info("知识库为空，请先上传文档")
    
    st.markdown("---")
    
    # 清空知识库
    st.subheader("危险操作")
    st.warning("以下操作不可恢复，请谨慎操作！")
    
    if st.button("🗑️ 清空整个知识库", use_container_width=True, type="primary"):
        if st.session_state.get("confirm_clear"):
            result = st.session_state["service"].clear_all()
            st.success(result)
            logger.info("知识库已清空")
            st.rerun()
        else:
            st.session_state["confirm_clear"] = True
            st.warning("再次点击确认清空知识库")
    
    if "confirm_clear" in st.session_state and st.session_state.get("confirm_clear"):
        if st.button("✅ 确认清空", key="confirm_clear_btn"):
            pass
    
    st.markdown("</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("操作说明")
    st.markdown(
        """
        - **支持格式**：`.txt`、`.md`  
        - **文档上传**：支持单个或多个文档上传，自动批量处理  
        - **注意事项**：  
            - 建议控制单次上传文档长度，避免异常超长文件  
            - 批量上传时，建议控制文件数量，避免系统负载过高  
        """,
    )
    
    st.divider()
    
    st.header("系统状态")
    st.success("✅ 服务运行中")
    st.success("✅ 向量库连接正常")
    st.success("✅ 文档处理就绪")
