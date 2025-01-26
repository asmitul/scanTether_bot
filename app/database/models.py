from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

class Address(BaseModel):
    """监控的地址模型"""
    address: str
    chat_id: int
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_checked: Optional[datetime] = None
    is_active: bool = True
    note: Optional[str] = None

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class Transaction(BaseModel):
    """USDT交易记录模型"""
    tx_id: str
    from_address: str
    to_address: str
    amount: float
    timestamp: datetime
    block_number: int
    confirmed: bool = True
    raw_data: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        } 