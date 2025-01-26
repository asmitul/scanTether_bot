import pytest
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from telegram import Update
from telegram.ext import CallbackContext

from app.config import MONGODB_URI
from app.database.operations import DatabaseManager
from app.bot.handlers import TronBot

@pytest.fixture
def event_loop():
    """创建一个新的事件循环"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def test_db():
    """创建测试数据库连接"""
    client = AsyncIOMotorClient(MONGODB_URI)
    db_name = "test_usdt_tracker"
    db = client[db_name]
    
    yield db
    
    # 清理测试数据库
    await client.drop_database(db_name)
    client.close()

@pytest.fixture
async def db_manager(test_db):
    """创建测试数据库管理器"""
    manager = DatabaseManager()
    manager.db = test_db
    manager.addresses = test_db.addresses
    manager.transactions = test_db.transactions
    
    await manager.init_indexes()
    
    yield manager
    
    await manager.close()

@pytest.fixture
def mock_update():
    """模拟Telegram更新对象"""
    update = Update(update_id=1)
    update.message = type('obj', (object,), {
        'message_id': 1,
        'text': '',
        'chat': type('obj', (object,), {'id': 123456789}),
        'reply_text': lambda *args, **kwargs: None
    })
    return update

@pytest.fixture
def mock_context():
    """模拟Telegram上下文对象"""
    context = CallbackContext(None)
    context.args = []
    return context 