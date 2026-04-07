# sessionManager 管理用户的历史信息
from typing import List, Dict, Optional
import datetime


class SessionManager:
    """
    用于管理多个用户的对话历史 (state["messages"])
    """
    sessions: Dict[str, List[Dict[str, str]]] = {}

    def __init__(self, use_postgres: bool = False):
        # 内存存储 {session_id: [{"role": "user/assistant", "content": "..."}]}
        ##self.sessions: Dict[str, List[Dict[str, str]]] = {}
        self.use_postgres = use_postgres

        if self.use_postgres:
            # TODO: 在这里初始化 PostgreSQL 连接
            # 比如 psycopg2.connect(...) 或 SQLAlchemy engine
            raise NotImplementedError("PostgreSQL 持久化暂未实现")

    def add_message(self, session_id: str, role: str, content: str):
        """
        向 session 对话历史中添加一条消息
        """
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(
            {"role": role, "content": content, "timestamp": datetime.datetime.now().isoformat()}
        )

    def getHistory(self, session_id: str, n: int = -1, include_timestamp: bool = False) -> str:
        """
        获取 session 的最近 n 条消息，拼接为一个字符串。
        如果 n <= 0，则获取所有历史记录。
        
        :param session_id: 会话ID
        :param n: 最近消息的数量。如果 n <= 0，则返回所有消息。
        :param include_timestamp: 是否在历史记录中包含消息的时间戳。
        :return: 格式化后的历史记录字符串。
        """
        if session_id not in self.sessions:
            return ""
        
        if n <= 0:
            history = self.sessions[session_id]
        else:
            history = self.sessions[session_id][-n:]
            
        
        if include_timestamp:
            # 包含时间戳的格式：[timestamp] role: content
            history_text = "\n".join([f"[{msg['timestamp']}] {msg['role']}: {msg['content']}" for msg in history])
        else:
            # 不包含时间戳的格式：role: content
            history_text = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
            
        return history_text

    def getLatestUserInput(self, session_id: str) -> Optional[str]:
        """
        获取该 session 用户最新的输入
        """
        if session_id not in self.sessions:
            return None
        for msg in reversed(self.sessions[session_id]):
            if msg["role"] == "user":
                return msg["content"]
        return None

    def clean(self, session_id: str):
        """
        清除指定 session 的所有历史
        """
        if session_id in self.sessions:
            del self.sessions[session_id]

    def dispHistory(self, session_id: str):
        """
        打印指定 session 的对话历史
        """
        if session_id not in self.sessions:
            print(f"No history for session {session_id}")
            return
        for msg in self.sessions[session_id]:
            print(f"[{msg['timestamp']}] {msg['role']}: {msg['content']}")


# ==== 使用示例 ====
if __name__ == "__main__":
    manager = SessionManager()

    # 模拟添加消息
    manager.add_message("user123", "user", "中国的首都是哪里？")
    manager.add_message("user123", "assistant", "北京")
    manager.add_message("user123", "user", "我觉得是上海")
    manager.add_message("user123", "assistant", "不是")

    # 获取最近 2 条
    print("最近2条对话:\n", manager.getHistory("user123", 2))

    # 获取最新用户输入
    print("最新用户输入:", manager.getLatestUserInput("user123"))

    # 打印所有历史
    print("完整历史:")
    manager.dispHistory("user123")

    history = manager.getHistory("user123", 10) 
    print ("history is :",history)

    # 清空历史
    manager.clean("user123")
    print("清空后:")
    manager.dispHistory("user123")
