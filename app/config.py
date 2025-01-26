import os
from dotenv import load_dotenv
from typing import List

# 加载.env文件
load_dotenv()

# Telegram Bot 配置
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# 添加配置验证
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set")

# MongoDB 配置
MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://mongo:27017')
MONGODB_DB_NAME = os.getenv('MONGODB_DB_NAME', 'usdt_tracker')

# TronScan API 配置
TRONSCAN_API_KEYS = os.getenv('TRONSCAN_API_KEYS', '').split(',')
TRONSCAN_API_URL = os.getenv('TRONSCAN_API_URL', 'https://api.tronscan.org/api/transaction')

# 添加配置验证
if not TRONSCAN_API_KEYS:
    raise ValueError("TRONSCAN_API_KEYS is not set")

# 日志配置
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# 数据库集合名称
COLLECTION_ADDRESSES = 'addresses'
COLLECTION_TRANSACTIONS = 'transactions'

# 轮询间隔（秒）
POLLING_INTERVAL = 5

# API 请求配置
REQUEST_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 1 