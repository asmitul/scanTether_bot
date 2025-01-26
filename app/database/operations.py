from typing import List, Optional
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING, DESCENDING
import asyncio
import logging

from ..config import MONGODB_URI, MONGODB_DB_NAME, COLLECTION_ADDRESSES, COLLECTION_TRANSACTIONS
from .models import Address, Transaction
from ..utils.retry import async_retry
from pymongo.errors import PyMongoError
from ..monitoring.metrics import (
    DB_OPERATIONS,
    DB_OPERATION_DURATION,
    ACTIVE_ADDRESSES,
    track_time
)

logger = logging.getLogger(__name__)

class DatabaseManager:
    def __init__(self):
        # 添加连接错误处理
        try:
            self.client = AsyncIOMotorClient(MONGODB_URI)
            # 验证连接
            asyncio.get_event_loop().run_until_complete(
                self.client.admin.command('ismaster')
            )
            self.db = self.client[MONGODB_DB_NAME]
            self.addresses = self.db[COLLECTION_ADDRESSES]
            self.transactions = self.db[COLLECTION_TRANSACTIONS]
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise

    async def init_indexes(self):
        """初始化数据库索引"""
        # 地址集合索引
        await self.addresses.create_index([("address", ASCENDING), ("chat_id", ASCENDING)], unique=True)
        await self.addresses.create_index([("last_checked", ASCENDING)])

        # 交易集合索引
        await self.transactions.create_index([("tx_id", ASCENDING)], unique=True)
        await self.transactions.create_index([("from_address", ASCENDING)])
        await self.transactions.create_index([("to_address", ASCENDING)])
        await self.transactions.create_index([("timestamp", DESCENDING)])

    # 地址相关操作
    @async_retry(
        retries=3,
        delay=0.5,
        exceptions=(PyMongoError,)
    )
    async def add_address(self, address: str, chat_id: int, note: Optional[str] = None) -> bool:
        """添加新的监控地址"""
        try:
            address_doc = Address(
                address=address,
                chat_id=chat_id,
                note=note
            )
            await self.addresses.insert_one(address_doc.dict())
            return True
        except Exception:
            return False

    async def remove_address(self, address: str, chat_id: int) -> bool:
        """移除监控地址"""
        result = await self.addresses.update_one(
            {"address": address, "chat_id": chat_id},
            {"$set": {"is_active": False}}
        )
        return result.modified_count > 0

    async def get_active_addresses(self) -> List[Address]:
        """获取所有活跃的监控地址"""
        cursor = self.addresses.find({"is_active": True})
        return [Address(**doc) async for doc in cursor]

    async def update_address_check_time(self, address: str):
        """更新地址最后检查时间"""
        await self.addresses.update_many(
            {"address": address},
            {"$set": {"last_checked": datetime.utcnow()}}
        )

    # 交易相关操作
    @track_time(DB_OPERATION_DURATION, {'operation': 'save_transaction'})
    async def save_transaction(self, transaction: Transaction) -> bool:
        """保存新的交易记录"""
        try:
            await self.transactions.insert_one(transaction.dict())
            DB_OPERATIONS.labels(operation='save_transaction', status='success').inc()
            return True
        except Exception as e:
            DB_OPERATIONS.labels(operation='save_transaction', status='failed').inc()
            raise

    async def get_address_transactions(
        self,
        address: str,
        limit: int = 10,
        skip: int = 0
    ) -> List[Transaction]:
        """获取地址的交易历史"""
        cursor = self.transactions.find({
            "$or": [
                {"from_address": address},
                {"to_address": address}
            ]
        }).sort("timestamp", DESCENDING).skip(skip).limit(limit)
        
        return [Transaction(**doc) async for doc in cursor]

    async def transaction_exists(self, tx_id: str) -> bool:
        """检查交易是否已存在"""
        return await self.transactions.count_documents({"tx_id": tx_id}) > 0

    # 添加关闭方法
    async def close(self):
        if hasattr(self, 'client'):
            self.client.close()

    async def update_active_addresses_metric(self):
        """更新活跃地址数量指标"""
        count = await self.addresses.count_documents({"is_active": True})
        ACTIVE_ADDRESSES.set(count)

db_manager = DatabaseManager() 