# app/config.py

# TRC20 数据源 API（以 Tronscan API 为例，实际接口地址根据需求更改）
TRONSCAN_API_URL = "https://api.tronscan.org/api/transaction"  

# 多个 APIKey（使用多个账户规避单个 APIKey 限制）
API_KEYS = [
    "API_KEY_1",
    "API_KEY_2",
    "API_KEY_3",
    # ...
]

# 待监控的地址及其轮询间隔（单位：秒）
ADDRESSES = [
    {"address": "TExampleAddress1", "interval": 5},
    {"address": "TExampleAddress2", "interval": 7},
    # 可以添加更多地址…
]

# Telegram Bot 配置
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID" 