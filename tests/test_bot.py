import pytest
from unittest.mock import patch
from app.bot.handlers import TronBot

@pytest.mark.asyncio
async def test_start_command(mock_update, mock_context):
    """测试开始命令"""
    with patch('telegram.Message.reply_text') as mock_reply:
        bot = TronBot()
        await bot.start_command(mock_update, mock_context)
        mock_reply.assert_called_once()

@pytest.mark.asyncio
async def test_add_address_command(mock_update, mock_context, db_manager):
    """测试添加地址命令"""
    with patch('telegram.Message.reply_text') as mock_reply:
        bot = TronBot()
        
        # 测试无效地址
        mock_context.args = ["invalid_address"]
        await bot.add_address(mock_update, mock_context)
        mock_reply.assert_called_with("❌ 无效的TRON地址格式", parse_mode='Markdown')
        
        # 测试有效地址
        mock_context.args = ["TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"]
        await bot.add_address(mock_update, mock_context)
        assert mock_reply.call_count == 2

@pytest.mark.asyncio
async def test_list_addresses(mock_update, mock_context, db_manager):
    """测试列出地址命令"""
    with patch('telegram.Message.reply_text') as mock_reply:
        bot = TronBot()
        
        # 添加测试地址
        await db_manager.add_address(
            "TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            mock_update.message.chat.id,
            "Test address"
        )
        
        await bot.list_addresses(mock_update, mock_context)
        mock_reply.assert_called_once() 