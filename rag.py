from langchain_community.chat_models import ChatTongyi
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnablePassthrough, RunnableLambda, RunnableWithMessageHistory, RunnableParallel
from file_history_store import  get_history
from vector_stores import  VectorStoreService
from langchain_community.embeddings import DashScopeEmbeddings
import config_data as config



"""这个函数可以帮助我们看到我们提问的问题"""
def print_prompt(prompt):
    print("="*20)
    print(prompt.to_string())
    print("=" * 20)
    return prompt
class RagService(object):

    def __init__(self):
        self.vector_service=VectorStoreService(DashScopeEmbeddings(model=config.embedding_model_name,dashscope_api_key=config.BAI_LIAN_API_KEY))

        '''三个地方的注入 1.参考资料2.历史信息3.用户的提问'''
        self.prompt_template=ChatPromptTemplate.from_messages([
            ("system","你是一个严格基于知识库内容回答问题的AI助手。你必须遵守以下规则：\n"
             "1. 严格基于我提供的参考资料回答问题，不要编造任何内容\n"
             "2. 如果参考资料中没有相关信息，请明确说明'根据现有资料无法回答此问题'\n"
             "3. 不要添加参考资料以外的推测或假设\n"
             "4. 回答应简洁专业，直接引用相关资料内容\n"
             "参考资料:{context}"),
            ("system","用户的对话历史记录如下："),
            MessagesPlaceholder("history"),
            ("user","请严格基于上述参考资料回答我的问题:{input}")
        ])

        self.chat_model=ChatTongyi(model=config.chat_model_name,api_key=config.BAI_LIAN_API_KEY)

        self.chain=self.__get_chain()


    def __get_chain(self):
        retriever = self.vector_service.get_retriever()

        def format_for_retriever(value: dict) -> str:
            """
            从输入字典中提取用户问题，用于检索器查询

            Args:
                value: 包含用户输入的字典，格式如 {"input": "用户问题"}

            Returns:
                str: 提取出的用户问题字符串
            """
            print("输入到检索器中的数据:",value)
            return value["input"]

        def format_for_prompt_template(value):
            print("输入到prompt_template中的数据:",value)
            """
            将检索结果和输入信息重组为提示模板所需的格式

            Args:
                value: 包含检索结果和原始输入的字典，格式如：
                    {
                        "input": {"input": "用户问题", "history": [...]},
                        "context": "检索到的文档内容"
                    }

            Returns:
                dict: 重组后的字典，包含提示模板所需的三个键：
                    - "input": 用户问题
                    - "context": 检索到的文档上下文
                    - "history": 对话历史
            """
            new_value = {}
            new_value["input"] = value["input"]["input"]  # 提取用户问题
            new_value["context"] = value["context"]  # 直接使用检索结果
            new_value["history"] = value["input"]["history"]  # 提取历史对话
            return new_value
        def format_document(docs: list[Document]) -> str:
            if not docs:
                return "未找到相关参考资料。请明确告知用户：根据现有知识库内容无法回答此问题，建议提供更多相关信息或询问其他问题。"
            return "\n".join(
                f"文档片段: {doc.page_content}\n文档元数据: {doc.metadata}"
                for doc in docs
            )

        # 构建检索链：输入问题 -> 检索 -> 格式化
        retrieval_chain = retriever | format_document

        # 主链：并行处理输入（透传）和检索结果
        chain = (
                {
                    "input": RunnablePassthrough(),
                    "context": RunnableLambda(format_for_retriever) | retriever | format_document
                }
                | RunnableLambda(format_for_prompt_template)
                | self.prompt_template
                | self.chat_model
                | StrOutputParser()
        )

        # 添加历史管理
        conversation_chain=RunnableWithMessageHistory(
            chain,
            get_history,
            input_messages_key="input",
            history_messages_key="history",  # 明确指定历史消息键（与模板中的MessagesPlaceholder对应）
        )
        return conversation_chain
""""input" 键：

RunnablePassthrough() 的作用是“透传”。它不做任何处理，直接把接收到的输入（用户的问题）原封不动地传下去。
结果：字典中的 "input" 字段值就是用户原始的问题。
"context" 键：这里有一个子管道：retriever | format_document。
retriever：它接收用户的问题，去向量数据库中查找相关的文档片段，返回一个文档列表。
format_document：这是一个函数（或 Runnable），它接收上一步 retriever 返回的文档列表，并将其格式化为一个易读的字符串。
结果：字典中的 "context" 字段值是格式化后的检索内容。
{
    "input": "用户的原始问题",
    "context": "检索到的相关文档内容拼接成的字符串"
}传递给prompt_template
LangChain 会自动利用字典中的键值对来填充模板中的占位符 {context} 和 {input}，输出一个PromptValue 对象（包含完整的提示词字符串）
print_prompt它接收上一步生成的完整 Prompt，将其打印到控制台便于查看信息，然后原样输出给下一步。
大模型接受的字符串回答处理之后返回一个 ChatMessage 或 ChatResult 对象（包含模型回复的原始对象）
StrOutputParser()：LLM 返回的对象通常包含很多元数据（如 token 使用量、finish_reason 等）。
StrOutputParser() 的作用是提取出消息中的纯文本内容。
结果：最终输出一个干净的字符串，即模型的回答。
"""
if __name__ == '__main__':
    #session id配置

    res=RagService().chain.invoke({"input":"我的身高175cm，尺码推荐？"},config.session_config)
    print(res)
