import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.bot.handlers import bot
from app.database.operations import db_manager
from app.utils.logger import setup_logger
from app.monitoring.metrics import init_metrics

logger = setup_logger('bot.starter')

async def init_database():
    """初始化数据库"""
    try:
        await db_manager.init_indexes()
        logger.info("Database indexes initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        sys.exit(1)

def main():
    """主函数"""
    logger.info("Starting Telegram bot...")
    
    # 初始化指标服务器
    init_metrics(port=8000)
    
    # 初始化数据库
    asyncio.run(init_database())
    
    try:
        # 启动机器人
        bot.run()
    except Exception as e:
        logger.error(f"Bot crashed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 