from __future__ import annotations
import os
from typing import Sequence, List
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.messages import BaseMessage, message_to_dict, messages_from_dict
import json
def get_history(session_id):
    return FileChatMessageHistory(session_id,storage_path='./chat_history')
'''message_to_dict:  单个消息对象（BaseMessage类实例）->字典'''
'''messages_from_dict [字典，字典...]->消息对象列表（BaseMessage类实例列表）'''
'''AIMessage,HumanMessage,SystemMessage都是BaseMessage的子类'''
class FileChatMessageHistory(BaseChatMessageHistory):
    def __init__(self,session_id,storage_path):
        self.session_id = session_id  #会话id
        self.storage_path = storage_path  #不同会话Id的存储文件  所在文件夹路径
        self.file_path=os.path.join(self.storage_path,self.session_id)
        #确保文件存在
        os.makedirs(self.storage_path,exist_ok=True)

    def add_message(self, message: BaseMessage | Sequence[BaseMessage]) -> None:
        all_messages = list(self.messages)  # 已有的消息列表
        if isinstance(message, BaseMessage):
            all_messages.append(message)  # 单个消息直接追加
        else:
            all_messages.extend(message)  # 序列消息扩展

        #将数据同步写入到本地文件中
        #类对象写入文件 -》一堆二进制
        #为了方便，可以将BaseMessage消息转为字典（借助JSON模块以json字符串写入文件）
        # new_messages=[]
        # for message in all_messages:
        #     d=message_to_dict(message)
        #     new_messages.append(d)

        new_messages=[message_to_dict(message) for message in all_messages]

        #将数据写入文件
        with open(self.file_path,'w',encoding='utf-8') as f:
            json.dump(new_messages,f)



    def clear(self)-> None:
        with open(self.file_path,'w',encoding='utf-8') as f:
            f.write('')

    @property
    def messages(self) -> List[BaseMessage]:
        """
        从文件加载历史消息记录。

        Returns:
            list[BaseMessage]: 包含历史消息的列表。如果文件不存在或为空，返回空列表。
        """
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                messages_data = json.load(f)
                return messages_from_dict(messages_data)
        except FileNotFoundError:
            return []
        except json.JSONDecodeError:
            return []
'''@property 是一个装饰器，用于将类中的方法转换为只读属性。它的主要作用是让开发者可以像访问类的属性一样访问方法，而不需要显式地调用括号 ()'''