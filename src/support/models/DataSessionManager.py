import datetime
from typing import Dict, Any, Optional, Union, List

# Type Hint for the inner data store structure
# { session_id: { data_key_1: data_value_1, data_key_2: data_value_2, ... } }
SessionDataStore = Dict[str, Dict[str, Any]]

class DataSessionManager:
    """
    用于管理多个用户的 Web 交互过程中的数据，以 key/value 方式存储。
    适用于存储用户偏好、临时计算结果、交互状态等非对话列表数据。
    """
    
    # 类属性，用于内存存储
    sessions: SessionDataStore = {}

    def __init__(self, use_postgres: bool = False):
        """
        初始化 DataSessionManager。
        
        :param use_postgres: 是否启用 PostgreSQL 持久化。
        """
        self.use_postgres = use_postgres

        if self.use_postgres:
            # TODO: 在这里初始化 PostgreSQL 连接
            # 比如 异步的 asyncpg 或 SQLAlchemy engine
            raise NotImplementedError("PostgreSQL 持久化暂未实现")
            
        # 即使不使用数据库，也要确保内存存储被初始化 (尽管它是类属性)
        if not self.sessions:
             self.sessions = {}


    def set_data(self, session_id: str, key: str, value: Any) -> None:
        """
        为指定 session_id 存储一个键值对数据。
        
        :param session_id: 会话ID。
        :param key: 数据的键。
        :param value: 数据的任一类型值 (Any)。
        """
        if self.use_postgres:
            # TODO: 实现异步的数据库写入操作
            pass # 占位符
        
        if session_id not in self.sessions:
            # 如果是新会话，初始化一个空字典
            self.sessions[session_id] = {}
            
        # 存储数据
        self.sessions[session_id][key] = value


    def get_data(self, session_id: str, key: str, default: Optional[Any] = None) -> Any:
        """
        获取指定 session_id 下特定 key 的数据。
        
        :param session_id: 会话ID。
        :param key: 数据的键。
        :param default: 如果键不存在时返回的默认值。
        :return: 存储的值，如果不存在则返回 default。
        """
        if self.use_postgres:
            # TODO: 实现异步的数据库读取操作
            # 假设有一个 await self._db_get(session_id, key)
            pass # 占位符
        
        if session_id not in self.sessions:
            return default
            
        return self.sessions[session_id].get(key, default)


    def get_all_data(self, session_id: str) -> Dict[str, Any]:
        """
        获取指定 session_id 的所有键值对数据。
        
        :param session_id: 会话ID。
        :return: 包含所有数据的字典，如果会话不存在则返回空字典。
        """
        if self.use_postgres:
            # TODO: 实现异步的数据库读取所有数据操作
            pass # 占位符
            
        return self.sessions.get(session_id, {})


    def clean(self, session_id: str, key: Optional[str] = None) -> None:
        """
        清除指定 session 的数据。
        
        :param session_id: 会话ID。
        :param key: 如果指定，则只清除该键下的数据；如果不指定，则清除该会话的所有数据。
        """
        if self.use_postgres:
            # TODO: 实现数据库删除操作
            pass # 占位符
            
        if session_id in self.sessions:
            if key is None:
                # 清除整个会话
                del self.sessions[session_id]
            elif key in self.sessions[session_id]:
                # 清除特定的键
                del self.sessions[session_id][key]


    def dispData(self, session_id: str):
        """
        打印指定 session 的所有数据。
        """
        data = self.get_all_data(session_id)
        if not data:
            print(f"No data for session {session_id}")
            return
            
        print(f"--- Session Data for {session_id} ---")
        for key, value in data.items():
            # 使用 repr() 来更好地显示不同类型的值，例如字符串引号
            print(f"Key: {key}\nValue: {repr(value)}\n---")
            
 
if __name__ == "__main__":
           
    # 实例化管理器
    data_manager = DataSessionManager()

    user_a_id = "user-abc-123"
    user_b_id = "user-xyz-789"

    # 1. 为用户 A 存储数据
    data_manager.set_data(user_a_id, "theme_preference", "dark")
    data_manager.set_data(user_a_id, "last_page_visited", "/dashboard")
    data_manager.set_data(user_a_id, "cart_items", [101, 102])

    # 2. 为用户 B 存储数据 (隔离存储)
    data_manager.set_data(user_b_id, "theme_preference", "light")
    data_manager.set_data(user_b_id, "language", "zh-CN")

    # 3. 获取数据
    print(f"User A's theme: {data_manager.get_data(user_a_id, 'theme_preference')}")
    print(f"User B's theme: {data_manager.get_data(user_b_id, 'theme_preference')}")
    print(f"User A's cart: {data_manager.get_data(user_a_id, 'cart_items')}")

    # 4. 获取不存在的键 (使用默认值)
    print(f"User B's cart: {data_manager.get_data(user_b_id, 'cart_items', default=[])}")

    # 5. 打印所有数据
    data_manager.dispData(user_a_id)

    # 6. 清除特定键
    data_manager.clean(user_a_id, "last_page_visited")
    data_manager.dispData(user_a_id) # 检查 "last_page_visited" 是否被清除

    # 7. 清除整个会话
    data_manager.clean(user_b_id)
    data_manager.dispData(user_b_id) # 会显示 "No data for session user-xyz-789"