from celery import Celery
from pymongo import MongoClient

# 配置 Celery 使用 Redis 作为消息代理
celery_app = Celery("tasks", broker="redis://redis:6379/0")

# 同步方式连接 MongoDB，用于后端任务（注意：Celery 的任务函数为同步，即无法直接调用 await）
@celery_app.task
def insert_transaction_task(tx):
    client = MongoClient("mongodb://mongodb:27017")  # Docker Compose 下服务名为 mongodb
    db = client["tron_db"]
    collection = db["transactions"]
    try:
        collection.insert_one(tx)
        print(f"Celery 写入交易成功: {tx.get('txid', '未知')}")
    except Exception as e:
        print(f"Celery 写入交易失败: {e}") 