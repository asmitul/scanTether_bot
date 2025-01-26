import asyncio
import random
from datetime import datetime
from typing import Dict, List, Optional

from ..config import TRONSCAN_API_KEYS, TRONSCAN_API_URL
from ..utils.helpers import make_request
from ..utils.logger import setup_logger
from ..utils.retry import async_retry, circuit_breaker
from aiohttp import ClientError

logger = setup_logger('scraper.fetcher')

class TronScanFetcher:
    def __init__(self):
        self.api_keys = TRONSCAN_API_KEYS
        self.base_url = TRONSCAN_API_URL
        
    def _get_random_api_key(self) -> str:
        """随机选择一个API密钥以实现负载均衡"""
        return random.choice(self.api_keys)

    def _get_headers(self) -> Dict[str, str]:
        """生成请求头"""
        return {
            "TRON-PRO-API-KEY": self._get_random_api_key(),
            "Accept": "application/json"
        }

    @async_retry(
        retries=3,
        delay=1.0,
        exponential_base=2.0,
        exceptions=(ClientError, TimeoutError)
    )
    @circuit_breaker(failure_threshold=5)
    async def fetch_address_transactions(
        self,
        address: str,
        min_timestamp: Optional[int] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        获取地址的USDT交易记录
        
        Args:
            address: TRON地址
            min_timestamp: 最小时间戳（毫秒）
            limit: 返回记录数量限制
            
        Returns:
            List[Dict]: 交易记录列表
        """
        params = {
            "address": address,
            "limit": limit,
            "contract_address": "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t",  # USDT合约地址
            "only_confirmed": True,
            "only_trc20": True,
        }
        
        if min_timestamp:
            params["min_timestamp"] = min_timestamp

        try:
            response = await make_request(
                url=self.base_url,
                params=params,
                headers=self._get_headers()
            )
            
            if not response.get("data"):
                return []
                
            return response["data"]
            
        except Exception as e:
            logger.error(f"Error fetching transactions for address {address}: {str(e)}")
            raise

    async def fetch_multiple_addresses(
        self,
        addresses: List[str],
        min_timestamp: Optional[int] = None
    ) -> Dict[str, List[Dict]]:
        """
        批量获取多个地址的交易记录
        
        Args:
            addresses: 地址列表
            min_timestamp: 最小时间戳
            
        Returns:
            Dict[str, List[Dict]]: 地址到交易记录的映射
        """
        tasks = []
        for address in addresses:
            task = self.fetch_address_transactions(address, min_timestamp)
            tasks.append(task)
            
        # 使用gather并发获取数据
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        transactions_map = {}
        for address, result in zip(addresses, results):
            if isinstance(result, Exception):
                logger.error(f"Failed to fetch transactions for {address}: {str(result)}")
                transactions_map[address] = []
            else:
                transactions_map[address] = result
                
        return transactions_map 