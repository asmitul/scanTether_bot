import pytest
from unittest.mock import patch, MagicMock
from app.scraper.fetcher import TronScanFetcher
from app.scraper.processor import TransactionProcessor

@pytest.mark.asyncio
async def test_fetch_transactions():
    """测试获取交易数据"""
    with patch('app.scraper.fetcher.make_request') as mock_request:
        # 模拟API响应
        mock_request.return_value = {
            "data": [
                {
                    "transaction_id": "test_tx_id",
                    "from": "TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
                    "to": "TRyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
                    "value": "100000000",  # 100 USDT
                    "block_timestamp": 1234567890000,
                    "block": 12345
                }
            ]
        }
        
        fetcher = TronScanFetcher()
        transactions = await fetcher.fetch_address_transactions(
            "TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
        )
        
        assert len(transactions) == 1
        assert transactions[0]["transaction_id"] == "test_tx_id"

@pytest.mark.asyncio
async def test_process_transactions():
    """测试交易处理"""
    processor = TransactionProcessor()
    raw_transactions = [
        {
            "transaction_id": "test_tx_id",
            "from": "TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            "to": "TRyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy",
            "value": "100000000",
            "block_timestamp": 1234567890000,
            "block": 12345
        }
    ]
    
    processed_txs, new_tx_ids = await processor.process_raw_transactions(raw_transactions)
    
    assert len(processed_txs) == 1
    assert len(new_tx_ids) == 1
    assert processed_txs[0].amount == 100.0 