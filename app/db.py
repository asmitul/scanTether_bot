import motor.motor_asyncio
import asyncio

MONGO_URL = "mongodb://mongodb_scantether:27017"
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URL)
database = client["tron_db"]

# 交易记录集合
collection = database["transactions"]

async def init_indexes():
    """
    为交易记录集合创建必要的索引：
    1. txid的唯一索引，确保每笔交易唯一。
    2. from字段的索引，便于根据发送地址查询。
    3. to字段的索引，便于根据接收地址查询。
    4. timestamp字段的索引，便于按时间排序查询。
    """
    try:
        # 建立txid唯一索引
        await collection.create_index("txid", unique=True)
        print("索引创建成功：txid (唯一索引)")

        # 建立发送地址索引
        await collection.create_index("from")
        print("索引创建成功：from")

        # 建立接收地址索引（如果数据中包含该字段）
        await collection.create_index("to")
        print("索引创建成功：to")

        # 建立按时间戳排序的索引（假设字段名为timestamp）
        await collection.create_index("timestamp")
        print("索引创建成功：timestamp")
    except Exception as e:
        print(f"创建索引过程中出现异常: {e}")

# 当直接执行此文件时，初始化索引
if __name__ == '__main__':
    asyncio.run(init_indexes()) 