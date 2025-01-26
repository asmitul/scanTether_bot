from datetime import datetime
from typing import Dict, List, Set, Tuple
from decimal import Decimal
import decimal

from ..database.models import Transaction
from ..database.operations import db_manager
from ..utils.logger import setup_logger
from ..monitoring.metrics import (
    TRANSACTIONS_PROCESSED,
    TRANSACTION_AMOUNT,
    track_time,
    DB_OPERATION_DURATION
)

logger = setup_logger('scraper.processor')

class TransactionProcessor:
    @staticmethod
    def _parse_timestamp(timestamp: int) -> datetime:
        """将毫秒时间戳转换为datetime对象"""
        return datetime.fromtimestamp(timestamp / 1000)

    @staticmethod
    def _parse_amount(amount: str) -> float:
        """解析USDT金额（考虑精度）"""
        try:
            # 添加额外的验证
            if not amount or float(amount) < 0:
                raise ValueError("Invalid amount")
            return float(Decimal(amount) / Decimal(10 ** 6))
        except (ValueError, TypeError, decimal.InvalidOperation) as e:
            logger.error(f"Error parsing amount {amount}: {e}")
            return 0.0

    @track_time(DB_OPERATION_DURATION, {'operation': 'process_transactions'})
    async def process_raw_transactions(
        self,
        transactions: List[Dict]
    ) -> Tuple[List[Transaction], Set[str]]:
        """
        处理原始交易数据
        
        Args:
            transactions: 原始交易数据列表
            
        Returns:
            Tuple[List[Transaction], Set[str]]: 处理后的交易对象列表和新交易ID集合
        """
        processed_transactions = []
        new_tx_ids = set()

        for tx_data in transactions:
            try:
                # 检查交易是否已存在
                tx_id = tx_data.get("transaction_id")
                if not tx_id or await db_manager.transaction_exists(tx_id):
                    continue

                # 解析交易数据
                transaction = Transaction(
                    tx_id=tx_id,
                    from_address=tx_data.get("from"),
                    to_address=tx_data.get("to"),
                    amount=self._parse_amount(tx_data.get("value", "0")),
                    timestamp=self._parse_timestamp(tx_data.get("block_timestamp", 0)),
                    block_number=tx_data.get("block"),
                    confirmed=True,
                    raw_data=tx_data
                )

                processed_transactions.append(transaction)
                new_tx_ids.add(tx_id)

            except Exception as e:
                logger.error(f"Error processing transaction: {str(e)}")
                continue

        TRANSACTIONS_PROCESSED.labels(status='success').inc()
        for tx in transactions:
            TRANSACTION_AMOUNT.observe(float(tx.get('value', 0)) / 1e6)

        return processed_transactions, new_tx_ids

    async def save_transactions(
        self,
        transactions: List[Transaction]
    ) -> int:
        """
        保存处理后的交易
        
        Args:
            transactions: 交易对象列表
            
        Returns:
            int: 成功保存的交易数量
        """
        saved_count = 0
        for tx in transactions:
            try:
                if await db_manager.save_transaction(tx):
                    saved_count += 1
            except Exception as e:
                logger.error(f"Error saving transaction {tx.tx_id}: {str(e)}")
                continue

        return saved_count

    async def process_and_save(
        self,
        raw_transactions: List[Dict]
    ) -> Tuple[int, Set[str]]:
        """
        处理并保存交易数据
        
        Args:
            raw_transactions: 原始交易数据列表
            
        Returns:
            Tuple[int, Set[str]]: 保存的交易数量和新交易ID集合
        """
        processed_txs, new_tx_ids = await self.process_raw_transactions(raw_transactions)
        saved_count = await self.save_transactions(processed_txs)
        
        logger.info(f"Processed {len(processed_txs)} transactions, saved {saved_count}")
        return saved_count, new_tx_ids 