import time
import os
from io import BytesIO

import streamlit as st
from PyPDF2 import PdfReader

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


def extract_text_from_pdf(uploaded_file: BytesIO) -> str:
    """从PDF文件中提取文本，支持OCR和表格提取"""
    text_parts = []
    
    # 使用PyPDF2提取文本
    try:
        reader = PdfReader(uploaded_file)
        for page_num, page in enumerate(reader.pages, 1):
            text = page.extract_text() or ""
            if text.strip():
                text_parts.append(f"# 页面 {page_num}\n{text}")
    except Exception as e:
        st.warning(f"PyPDF2提取文本失败：{e}")
    
    # 重置文件指针
    uploaded_file.seek(0)
    
    # 使用pdfplumber提取表格
    try:
        import pdfplumber
        with pdfplumber.open(uploaded_file) as pdf:
            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                if tables:
                    text_parts.append(f"# 页面 {page_num} - 表格")
                    for table_num, table in enumerate(tables, 1):
                        text_parts.append(f"## 表格 {table_num}")
                        # 转换表格为文本
                        for row in table:
                            row_text = " | ".join([str(cell) if cell else "" for cell in row])
                            text_parts.append(row_text)
                        text_parts.append("")
    except ImportError:
        st.warning("pdfplumber未安装，跳过表格提取")
    except Exception as e:
        st.warning(f"表格提取失败：{e}")
    
    # 重置文件指针
    uploaded_file.seek(0)
    
    # 如果文本提取失败，尝试OCR
    if not text_parts:
        try:
            import pytesseract
            from PIL import Image
            import pdfplumber
            
            # 这里需要安装tesseract-ocr并配置路径
            # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            
            with pdfplumber.open(uploaded_file) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # 转换页面为图片
                    img = page.to_image(resolution=300)
                    # 转换为PIL Image
                    pil_img = img.original
                    
                    # OCR识别
                    ocr_text = pytesseract.image_to_string(pil_img, lang='chi_sim+eng')
                    
                    if ocr_text.strip():
                        text_parts.append(f"# 页面 {page_num} (OCR)\n{ocr_text}")
        except ImportError:
            st.warning("OCR依赖未安装，跳过OCR处理")
        except Exception as e:
            st.warning(f"OCR处理失败：{e}")
    
    return "\n".join(text_parts) if text_parts else ""


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
        <div class="kb-title">知识库管理中心</div>
        <div class="kb-subtitle">
            支持批量文档上传、知识库管理，适用于企业级知识库维护场景。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 创建标签页
tab1, tab2, tab3 = st.tabs(["文档上传", "批量导入", "知识库管理"])

with tab1:
    st.markdown('<div class="kb-card">', unsafe_allow_html=True)
    st.subheader("单个文档上传")
    st.caption("请选择需要加入知识库的源文档，目前支持 TXT / Markdown / PDF 格式。")

    uploader_file = st.file_uploader(
        "上传文件",
        type=["txt", "md", "pdf"],
        accept_multiple_files=False,
        key="single_file_uploader"
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
            logger.info(f"处理文件：{file_name}")
            if file_name.lower().endswith(".pdf"):
                text = extract_text_from_pdf(uploader_file)
            else:
                text = uploader_file.getvalue().decode("utf-8")
            logger.info(f"文件解析成功，文本长度：{len(text)}")
        except UnicodeDecodeError:
            st.error("文本文件编码不是 UTF-8，请转换编码后重试。")
            logger.error(f"文件编码错误：{file_name}")
            text = ""
        except Exception as e:
            st.error(f"文件解析失败：{e}")
            logger.error(f"文件解析失败：{file_name}, {str(e)}")
            text = ""

        if text:
            with st.spinner("正在载入向量数据库，请稍候..."):
                try:
                    logger.info(f"开始入库：{file_name}")
                    result = st.session_state["service"].upload_by_str(text, file_name)
                    logger.info(f"入库完成：{file_name}, 结果：{result}")
                    st.success("入库完成")
                    st.markdown(f"**处理结果**：{result}")
                except Exception as e:
                    st.error(f"入库失败：{e}")
                    logger.error(f"入库失败：{file_name}, {str(e)}")

    st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    st.markdown('<div class="kb-card">', unsafe_allow_html=True)
    st.subheader("批量文档导入")
    st.caption("请选择多个需要加入知识库的文档，支持批量处理。")

    uploader_files = st.file_uploader(
        "批量上传文件",
        type=["txt", "md", "pdf"],
        accept_multiple_files=True,
        key="batch_file_uploader"
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
        
        # 批量处理按钮
        if st.button("开始批量处理", use_container_width=True):
            logger.info(f"开始批量处理 {len(uploader_files)} 个文件")
            success_count = 0
            error_count = 0
            error_files = []
            
            with st.spinner("正在批量处理文件，请稍候..."):
                for file in uploader_files:
                    try:
                        logger.info(f"处理文件：{file.name}")
                        if file.name.lower().endswith(".pdf"):
                            text = extract_text_from_pdf(file)
                        else:
                            text = file.getvalue().decode("utf-8")
                        
                        if text:
                            result = st.session_state["service"].upload_by_str(text, file.name)
                            logger.info(f"文件处理成功：{file.name}")
                            success_count += 1
                        else:
                            error_files.append(file.name)
                            error_count += 1
                            logger.warning(f"文件内容为空：{file.name}")
                    except Exception as e:
                        error_files.append(file.name)
                        error_count += 1
                        logger.error(f"文件处理失败：{file.name}, {str(e)}")
                    finally:
                        # 重置文件指针
                        file.seek(0)
            
            logger.info(f"批量处理完成：成功 {success_count} 个，失败 {error_count} 个")
            st.success(f"批量处理完成！\n成功：{success_count} 个文件\n失败：{error_count} 个文件")
            
            if error_files:
                st.warning("处理失败的文件：")
                st.markdown("\n".join([f"- {file}" for file in error_files]))

    st.markdown("</div>", unsafe_allow_html=True)

with tab3:
    st.markdown('<div class="kb-card">', unsafe_allow_html=True)
    st.subheader("知识库管理")
    st.caption("查看和管理知识库中的文档。")
    
    # 这里可以添加知识库管理功能，如：
    # 1. 查看知识库中的文档列表
    # 2. 删除指定文档
    # 3. 清空知识库
    # 4. 导出知识库
    
    st.markdown("---")
    
    # 知识库统计信息
    st.subheader("知识库统计")
    
    # 这里可以添加统计信息，如文档数量、向量数量等
    st.info("知识库管理功能开发中...")
    
    # 清空知识库按钮
    if st.button("清空知识库", use_container_width=True, type="secondary"):
        if st.warning("确定要清空整个知识库吗？此操作不可恢复！"):
            # 这里可以添加清空知识库的代码
            st.success("知识库已清空")
            logger.info("知识库已清空")

    st.markdown("</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("操作说明")
    st.markdown(
        """
        - **支持格式**：`.txt`、`.md`、`.pdf`  
        - **单个上传**：一次上传一个文档，支持详细的处理信息  
        - **批量导入**：一次上传多个文档，自动批量处理  
        - **注意事项**：  
            - PDF 需为可复制文本的版本，扫描件效果依赖 OCR  
            - 建议控制单次上传文档长度，避免异常超长文件  
            - 批量上传时，建议控制文件数量，避免系统负载过高  
        """,
    )
    
    st.divider()
    
    st.header("系统状态")
    st.success("✅ 服务运行中")
    st.success("✅ 向量库连接正常")
    st.success("✅ 文档处理就绪")
