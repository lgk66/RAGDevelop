import streamlit as st


from rag import RagService
import config_data as config


# 页面配置
st.set_page_config(page_title="智能客服", page_icon="💬")
st.title("💬 智能客服助手")
st.divider()

# 初始化会话状态
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "你好呀，我是你的智能客服小助手！有什么可以帮助你的吗？"
    }]

if "rag" not in st.session_state:
    st.session_state.rag = RagService()

# 侧边栏
with st.sidebar:
    st.caption(f"当前对话模型：{config.chat_model_name}")
    if st.button("🧹 清除聊天记录", use_container_width=True):
        st.session_state.messages = [{
            "role": "assistant",
            "content": "聊天记录已清空，有什么新问题吗？"
        }]
        st.rerun()
    st.divider()

# 显示历史消息
for msg in st.session_state.messages:
    avatar = "🧑‍💻" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# 用户输入
if prompt := st.chat_input("请输入您的问题..."):
    # 显示用户消息
    with st.chat_message("user", avatar="🧑‍💻"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # ---------- 获取AI响应 ----------
    with st.chat_message("assistant", avatar="🤖"):
        status = st.status("AI正在思考...", expanded=True)
        # 删除: retrieval_callback = RetrievalCallback()  # 创建回调实例

        try:
            # 调用流式接口，使用默认配置
            response_stream = st.session_state.rag.chain.stream(
                {"input": prompt},
                config=config.session_config
            )

            # 收集完整回答
            full_response = ""
            response_placeholder = status.empty()

            # 流式输出
            for chunk in response_stream:
                full_response += chunk
                response_placeholder.markdown(full_response + "▌")

            # 最终显示（去掉光标）
            response_placeholder.markdown(full_response)

            # 更新状态为完成
            status.update(label="✅ 回答完成", state="complete", expanded=True)

        except Exception as e:
            st.error(f"请求失败：{str(e)}")
            full_response = "抱歉，服务暂时不可用，请稍后再试。"
            status.update(label="❌ 回答失败", state="error", expanded=True)

    # 保存AI回答
    st.session_state.messages.append({
        "role": "assistant",
        "content": full_response
    })
