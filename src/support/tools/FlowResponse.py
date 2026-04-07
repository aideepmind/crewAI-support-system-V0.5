from pydantic import BaseModel
from typing import Any, Optional

class FlowResponse(BaseModel):
    type: str                 # 业务类型
    success: bool             # 是否成功
    message: Optional[str]    # 给用户看的自然语言
    data: Optional[Any] = None
    