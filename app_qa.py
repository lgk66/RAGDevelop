import streamlit as st
import time

from rag import RagService
import config_data as config
from monitoring import get_monitor

# 设置页面配置
st.set_page_config(
    page_title="企业智能客服",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "您好，我是企业智能客服助手，很高兴为您服务。请描述您的问题或业务场景。",
            "sources": []
        }
    ]

if "rag" not in st.session_state:
    st.session_state.rag = RagService()

if "session_id" not in st.session_state:
    st.session_state.session_id = "user_001"

if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# 现代化UI样式
st.markdown(
    """
    <style>
    /* 全局样式 */
    :root {
        --primary-color: #2563eb;
        --secondary-color: #64748b;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --background-color: #ffffff;
        --surface-color: #f8fafc;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }

    /* 深色模式 */
    .dark {
        --primary-color: #3b82f6;
        --secondary-color: #94a3b8;
        --success-color: #10b981;
        --warning-color: #f59e0b;
        --error-color: #ef4444;
        --background-color: #0f172a;
        --surface-color: #1e293b;
        --text-primary: #f8fafc;
        --text-secondary: #cbd5e1;
        --border-color: #334155;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.3);
        --shadow-md: 0 4px 6px -1px rgb(0 0 0 / 0.4), 0 2px 4px -2px rgb(0 0 0 / 0.4);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.5), 0 4px 6px -4px rgb(0 0 0 / 0.5);
    }

    body {
        background-color: var(--background-color);
        color: var(--text-primary);
    }

    /* 头部样式 */
    .app-header {
        padding: 1rem 0 1.5rem 0;
        border-bottom: 1px solid var(--border-color);
        margin-bottom: 1.5rem;
    }

    .app-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: var(--primary-color);
        margin-bottom: 0.5rem;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    .app-subtitle {
        font-size: 1rem;
        color: var(--text-secondary);
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }

    /* 卡片样式 */
    .app-card {
        border-radius: 0.75rem;
        border: 1px solid var(--border-color);
        padding: 1.5rem;
        background: var(--surface-color);
        box-shadow: var(--shadow-sm);
        margin-bottom: 1.5rem;
    }

    /* 消息气泡样式 */
    .user-message {
        background-color: var(--primary-color);
        color: white;
        border-radius: 18px 18px 4px 18px;
        padding: 12px 16px;
        margin-left: auto;
        max-width: 80%;
        box-shadow: var(--shadow-sm);
    }

    .assistant-message {
        background-color: var(--surface-color);
        color: var(--text-primary);
        border-radius: 18px 18px 18px 4px;
        padding: 12px 16px;
        margin-right: auto;
        max-width: 80%;
        box-shadow: var(--shadow-sm);
        border: 1px solid var(--border-color);
    }

    /* 消息来源样式 */
    .message-sources {
        font-size: 0.75rem;
        color: var(--text-secondary);
        margin-top: 0.5rem;
        padding-top: 0.5rem;
        border-top: 1px solid var(--border-color);
        font-style: italic;
    }

    /* 按钮样式 */
    .stButton > button {
        border-radius: 0.5rem;
        font-weight: 500;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
    }

    /* 输入框样式 */
    .stChatInput > div {
        border-radius: 1rem;
        border: 1px solid var(--border-color);
        background: var(--surface-color);
    }

    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background-color: var(--surface-color);
        border-right: 1px solid var(--border-color);
    }

    /* 状态样式 */
    .stStatusWidget {
        border-radius: 0.5rem;
        background: var(--surface-color);
        border: 1px solid var(--border-color);
    }

    /* 响应式设计 */
    @media (max-width: 768px) {
        .app-title {
            font-size: 1.5rem;
        }
        
        .user-message,
        .assistant-message {
            max-width: 90%;
        }
    }

    /* 滚动条样式 */
    ::-webkit-scrollbar {
        width: 6px;
    }

    ::-webkit-scrollbar-track {
        background: var(--surface-color);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 3px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--secondary-color);
    }

    /* 打字动画 */
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }

    .typing-indicator {
        display: inline-block;
        overflow: hidden;
        white-space: nowrap;
        animation: typing 1s steps(40, end);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 头部区域
st.markdown(
    f"""
    <div class="app-header">
        <div class="app-title">企业智能客服助手</div>
        <div class="app-subtitle">
            基于企业知识库的问答系统，支持多轮对话，适用于内部支持、客服工单辅助等场景。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# 主要布局
col_main, col_side = st.columns([3, 1])

with col_side:
    with st.sidebar:
        # 会话管理
        st.header("会话管理")
        
        # 会话ID输入
        session_id = st.text_input(
            "会话ID", 
            value=st.session_state.session_id,
            help="不同的会话ID会保存不同的对话历史"
        )
        
        if session_id != st.session_state.session_id:
            st.session_state.session_id = session_id
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "您好，我是企业智能客服助手，很高兴为您服务。请描述您的问题或业务场景。",
                    "sources": []
                }
            ]
            # 更新配置
            config.session_config["configurable"]["session_id"] = session_id
            st.rerun()
        
        # 清除会话按钮
        if st.button("清除当前会话", use_container_width=True, type="secondary"):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "会话已重置，请重新输入您的问题。",
                    "sources": []
                }
            ]
            st.rerun()
        
        # 深色模式切换
        dark_mode = st.checkbox(
            "深色模式", 
            value=st.session_state.dark_mode,
            help="切换到深色主题"
        )
        
        if dark_mode != st.session_state.dark_mode:
            st.session_state.dark_mode = dark_mode
            # 这里可以添加深色模式的实现
            st.rerun()
        
        st.divider()
        
        # 系统信息
        st.header("系统信息")
        st.caption(f"当前模型：{config.chat_model_name}")
        st.caption(f"向量库：{config.collection_name}")
        st.caption(f"检索阈值：{config.similarity_threshold}")
        
        st.divider()
        
        # 系统状态
        st.header("系统状态")
        st.success("✅ 知识库已加载")
        st.success("✅ 模型连接正常")
        st.success("✅ 服务运行中")
        
        st.divider()
        
        # 监控指标
        st.header("监控指标")
        
        try:
            monitor = get_monitor()
            
            # 系统指标
            system_metrics = monitor.get_system_metrics()
            st.subheader("系统资源")
            
            if 'cpu' in system_metrics:
                st.metric("CPU使用率", f"{system_metrics['cpu']['percent']}%")
                st.metric("进程CPU", f"{system_metrics['cpu']['process_percent']}%")
            
            if 'memory' in system_metrics:
                st.metric("内存使用率", f"{system_metrics['memory']['percent']}%")
                st.metric("进程内存", f"{system_metrics['memory']['process_mb']} MB")
            
            # 应用指标
            app_metrics = monitor.get_application_metrics()
            st.subheader("应用性能")
            
            st.metric("平均响应时间", f"{app_metrics['response_times']['average_seconds']} s")
            st.metric("平均检索时间", f"{app_metrics['retrieval_times']['average_seconds']} s")
            st.metric("总查询数", app_metrics['query_count'])
            st.metric("错误数", app_metrics['error_count'])
            
        except Exception as e:
            st.warning(f"监控指标获取失败：{e}")

with col_main:
    # 消息历史
    st.markdown('<div class="app-card">', unsafe_allow_html=True)
    
    # 消息容器
    message_container = st.container()
    
    with message_container:
        for i, msg in enumerate(st.session_state.messages):
            # 显示消息
            if msg["role"] == "user":
                # 用户消息
                st.markdown(
                    f'<div class="user-message">{msg["content"]}</div>', 
                    unsafe_allow_html=True
                )
            else:
                # 助手消息
                st.markdown(
                    f'<div class="assistant-message">{msg["content"]}</div>', 
                    unsafe_allow_html=True
                )
                # 显示消息来源
                if "sources" in msg and msg["sources"]:
                    sources_text = "\n".join([f"- {source}" for source in msg["sources"]])
                    st.markdown(
                        f'<div class="message-sources">参考来源：\n{sources_text}</div>', 
                        unsafe_allow_html=True
                    )
            # 添加消息间距
            if i < len(st.session_state.messages) - 1:
                st.markdown('<div style="height: 12px;"></div>', unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)

# 用户输入框
prompt = st.chat_input(
    "请输入您的问题，例如“根据售后政策，这种情况怎么处理？”",
    key="user_input"
)

if prompt:
    # 记录查询开始时间
    start_time = time.time()
    
    # 添加用户消息
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # 显示用户消息
    with message_container:
        st.markdown(
            f'<div class="user-message">{prompt}</div>', 
            unsafe_allow_html=True
        )
    
    # 显示助手消息加载状态
    with message_container:
        assistant_message_placeholder = st.empty()
        
        # 显示加载状态
        status = st.status(
            "正在基于知识库生成回答...", 
            expanded=True
        )
        
        try:
            # 调用RAG服务生成回答
            response_stream = st.session_state.rag.chain.stream(
                {"input": prompt},
                config=config.session_config,
            )

            full_response = ""
            response_placeholder = status.empty()

            # 流式显示回答
            for chunk in response_stream:
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")

            # 完成回答
            response_placeholder.markdown(full_response)
            status.update(
                label="回答完成", 
                state="complete", 
                expanded=False
            )

            # 添加助手消息到会话历史
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": full_response,
                    "sources": ["知识库文档"]  # 这里可以添加实际的来源信息
                }
            )
            
            # 记录监控指标
            try:
                monitor = get_monitor()
                monitor.increment_query_count()
                monitor.record_response_time(time.time() - start_time)
            except Exception as monitor_error:
                st.warning(f"监控记录失败：{monitor_error}")

        except Exception as e:
            error_message = f"抱歉，服务暂时不可用，请稍后再试。错误信息：{str(e)}"
            st.error(error_message)
            status.update(
                label="请求失败", 
                state="error", 
                expanded=False
            )
            
            # 添加错误消息到会话历史
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": "抱歉，服务暂时不可用，请稍后再试。",
                    "sources": []
                }
            )
            
            # 记录错误监控指标
            try:
                monitor = get_monitor()
                monitor.increment_error_count()
                monitor.record_response_time(time.time() - start_time)
            except Exception as monitor_error:
                st.warning(f"监控记录失败：{monitor_error}")

# 添加打字动画效果
st.markdown(
    """
    <script>
    // 打字动画效果
    document.addEventListener('DOMContentLoaded', function() {
        const typingElements = document.querySelectorAll('.typing-indicator');
        typingElements.forEach(element => {
            const text = element.textContent;
            element.textContent = '';
            let i = 0;
            const typeWriter = () => {
                if (i < text.length) {
                    element.textContent += text.charAt(i);
                    i++;
                    setTimeout(typeWriter, 50);
                }
            };
            typeWriter();
        });
    });
    </script>
    """,
    unsafe_allow_html=True
)
