import streamlit as st

from rag import RagService
import config_data as config


st.set_page_config(
    page_title="企业智能客服",
    page_icon="💼",
    layout="wide",
)

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "您好，我是企业智能客服助手，很高兴为您服务。请描述您的问题或业务场景。",
        }
    ]

if "rag" not in st.session_state:
    st.session_state.rag = RagService()

st.markdown(
    """
    <style>
    .app-header {
        padding: 0.5rem 0 1.25rem 0;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 0.75rem;
    }
    .app-title {
        font-size: 1.6rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    .app-subtitle {
        font-size: 0.9rem;
        color: #6B7280;
    }
    .app-card {
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
    <div class="app-header">
        <div class="app-title">企业智能客服助手</div>
        <div class="app-subtitle">
            基于企业知识库的问答系统，支持多轮对话，适用于内部支持、客服工单辅助等场景。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

col_main, col_side = st.columns([2.2, 1])

with col_side:
    with st.sidebar:
        st.header("运行配置")
        st.caption(f"当前模型：{config.chat_model_name}")
        st.caption(f"向量库：{config.collection_name}")
        if st.button("清除当前会话", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "会话已重置，请重新输入您的问题。",
                }
            ]
            st.rerun()
        st.divider()
        st.caption("系统状态")
        st.caption("✅ 知识库已加载")

with col_main:
    st.markdown('<div class="app-card">', unsafe_allow_html=True)

    for msg in st.session_state.messages:
        avatar = "🧑‍💼" if msg["role"] == "user" else "🤖"
        with st.chat_message(msg["role"], avatar=avatar):
            st.markdown(msg["content"])

    st.markdown("</div>", unsafe_allow_html=True)

# 用户输入框固定在页面最底部
prompt = st.chat_input("请输入您的问题，例如“根据售后政策，这种情况怎么处理？”")

if prompt:
    with st.chat_message("user", avatar="🧑‍💼"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar="🤖"):
        status = st.status("正在基于知识库生成回答...", expanded=True)

        try:
            response_stream = st.session_state.rag.chain.stream(
                {"input": prompt},
                config=config.session_config,
            )

            full_response = ""
            response_placeholder = status.empty()

            for chunk in response_stream:
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)
            status.update(label="回答完成", state="complete", expanded=True)

        except Exception as e:
            st.error(f"请求失败：{str(e)}")
            full_response = "抱歉，服务暂时不可用，请稍后再试。"
            status.update(label="请求失败", state="error", expanded=True)

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": full_response,
        }
    )
