import time
from io import BytesIO

import streamlit as st
from PyPDF2 import PdfReader

from Knowledge_base import KnowledgeBaseService


st.set_page_config(
    page_title="知识库管理中心",
    page_icon="📚",
    layout="wide"
)

if "service" not in st.session_state:
    st.session_state["service"] = KnowledgeBaseService()


def extract_text_from_pdf(uploaded_file: BytesIO) -> str:
    reader = PdfReader(uploaded_file)
    pages_text = []
    for page in reader.pages:
        text = page.extract_text() or ""
        pages_text.append(text)
    return "\n".join(pages_text)


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
    .kb-metric {
        font-size: 0.85rem;
        color: #6B7280;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="kb-header">
        <div class="kb-title">知识库更新服务</div>
        <div class="kb-subtitle">
            支持 TXT / MD / PDF 文档上传，自动向量化入库，适用于企业知识库维护场景。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown('<div class="kb-card">', unsafe_allow_html=True)
    st.subheader("上传文档")
    st.caption("请选择需要加入知识库的源文档，目前支持 TXT / Markdown / PDF 格式。")

    uploader_file = st.file_uploader(
        "上传文件",
        type=["txt", "md", "pdf"],
        accept_multiple_files=False,
    )

    if uploader_file is not None:
        file_name = uploader_file.name
        file_type = uploader_file.type
        file_size = uploader_file.size / 1024

        st.markdown("---")
        st.markdown(f"**文件名**：{file_name}")
        st.markdown(f"**MIME 类型**：`{file_type}`")
        st.markdown(f"**文件大小**：{file_size:.2f} KB")

        try:
            if file_name.lower().endswith(".pdf"):
                text = extract_text_from_pdf(uploader_file)
            else:
                text = uploader_file.getvalue().decode("utf-8")
        except UnicodeDecodeError:
            st.error("文本文件编码不是 UTF-8，请转换编码后重试。")
            text = ""
        except Exception as e:
            st.error(f"文件解析失败：{e}")
            text = ""

        if text:
            with st.spinner("正在载入向量数据库，请稍候..."):
                time.sleep(1)
                result = st.session_state["service"].upload_by_str(text, file_name)

            st.success("入库完成")
            st.markdown(f"**处理结果**：{result}")

    st.markdown("</div>", unsafe_allow_html=True)

with col_right:
    st.markdown('<div class="kb-card">', unsafe_allow_html=True)
    st.subheader("操作说明")
    st.markdown(
        """
        - **支持格式**：`.txt`、`.md`、`.pdf`  
        - **适用场景**：产品手册、内部规章、FAQ 文档等  
        - **注意事项**：  
            - PDF 需为可复制文本的版本，扫描件效果依赖 OCR  
            - 建议控制单次上传文档长度，避免异常超长文件  
        """,
    )
    st.markdown("</div>", unsafe_allow_html=True)
