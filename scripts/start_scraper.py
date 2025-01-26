import asyncio
import sys
import os
from datetime import datetime, timedelta
import signal

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database.operations import db_manager
from app.scraper.fetcher import TronScanFetcher
from app.scraper.processor import TransactionProcessor
from app.bot.handlers import bot
from app.config import POLLING_INTERVAL
from app.utils.logger import setup_logger
from app.monitoring.metrics import init_metrics

logger = setup_logger('scraper.starter')

class TransactionScraper:
    def __init__(self):
        self.fetcher = TronScanFetcher()
        self.processor = TransactionProcessor()
        self.running = False

    async def process_address(self, address: str, min_timestamp: int = None):
        """处理单个地址的交易"""
        try:
            # 获取交易数据
            transactions = await self.fetcher.fetch_address_transactions(
                address,
                min_timestamp=min_timestamp
            )
            
            if transactions:
                # 处理和保存交易
                saved_count, new_tx_ids = await self.processor.process_and_save(transactions)
                if saved_count > 0:
                    logger.info(f"Saved {saved_count} new transactions for address {address}")
                
                # 更新最后检查时间
                await db_manager.update_address_check_time(address)
                
        except Exception as e:
            logger.error(f"Error processing address {address}: {str(e)}")

    async def run(self):
        """运行抓取器"""
        self.running = True
        
        while self.running:
            try:
                # 获取所有活跃地址
                addresses = await db_manager.get_active_addresses()
                
                if not addresses:
                    logger.info("No addresses to monitor")
                    await asyncio.sleep(POLLING_INTERVAL)
                    continue

                # 获取一小时前的时间戳
                min_timestamp = int((datetime.now() - timedelta(hours=1)).timestamp() * 1000)
                
                # 并发处理所有地址
                tasks = [
                    self.process_address(addr.address, min_timestamp)
                    for addr in addresses
                ]
                await asyncio.gather(*tasks)
                
                logger.info(f"Completed scanning {len(addresses)} addresses")
                
            except Exception as e:
                logger.error(f"Error in main scraper loop: {str(e)}")
            
            # 等待下一次轮询
            await asyncio.sleep(POLLING_INTERVAL)

    def stop(self):
        """停止抓取器"""
        self.running = False

async def main():
    """主函数"""
    logger.info("Starting transaction scraper...")
    
    # 初始化指标服务器
    init_metrics(port=8000)
    
    try:
        # 初始化数据库
        await db_manager.init_indexes()
        logger.info("Database initialized")
        
        # 添加优雅关闭处理
        scraper = TransactionScraper()
        
        def handle_shutdown(signum, frame):
            logger.info("Received shutdown signal")
            scraper.stop()
            
        signal.signal(signal.SIGTERM, handle_shutdown)
        signal.signal(signal.SIGINT, handle_shutdown)
        
        await scraper.run()
    except KeyboardInterrupt:
        logger.info("Shutting down scraper...")
    except Exception as e:
        logger.error(f"Scraper crashed: {str(e)}")
        sys.exit(1)
    finally:
        # 确保资源被正确释放
        await db_manager.close()

if __name__ == "__main__":
    asyncio.run(main()) 