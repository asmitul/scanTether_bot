import pytest
from datetime import datetime
from app.database.models import Address, Transaction

@pytest.mark.asyncio
async def test_add_address(db_manager):
    """测试添加地址"""
    address = "TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    chat_id = 123456789
    note = "Test address"
    
    # 测试添加地址
    success = await db_manager.add_address(address, chat_id, note)
    assert success is True
    
    # 验证地址是否已添加
    cursor = db_manager.addresses.find({"address": address})
    addresses = await cursor.to_list(length=1)
    assert len(addresses) == 1
    assert addresses[0]["chat_id"] == chat_id
    assert addresses[0]["note"] == note

@pytest.mark.asyncio
async def test_remove_address(db_manager):
    """测试移除地址"""
    # 先添加一个地址
    address = "TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
    chat_id = 123456789
    await db_manager.add_address(address, chat_id)
    
    # 测试移除地址
    success = await db_manager.remove_address(address, chat_id)
    assert success is True
    
    # 验证地址是否已被标记为非活跃
    cursor = db_manager.addresses.find({"address": address})
    addresses = await cursor.to_list(length=1)
    assert len(addresses) == 1
    assert addresses[0]["is_active"] is False

@pytest.mark.asyncio
async def test_save_transaction(db_manager):
    """测试保存交易"""
    tx = Transaction(
        tx_id="test_tx_id",
        from_address="TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
        to_address="TRyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
        amount=100.0,
        timestamp=datetime.utcnow(),
        block_number=12345
    )
    
    # 测试保存交易
    success = await db_manager.save_transaction(tx)
    assert success is True
    
    # 验证交易是否已保存
    saved_tx = await db_manager.transactions.find_one({"tx_id": tx.tx_id})
    assert saved_tx is not None
    assert saved_tx["amount"] == tx.amount 