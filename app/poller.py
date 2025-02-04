import asyncio
import aiohttp
from . import config
from . import db
from .telegram_bot import notify_new_transaction  # 导入通知函数

# 配置错误重试相关参数
MAX_RETRIES = 3       # 每次请求最大重试次数
BASE_DELAY = 1        # 初始等待时间（秒）
BACKOFF_FACTOR = 2    # 指数退避因子

# 异步请求单个地址数据（这里使用 APIKey 轮询的形式调用接口）
async def fetch_transactions(session, address, api_key):
    """
    使用给定的 APIKey 请求指定地址的交易数据，并在失败时重试。
    """
    params = {"address": address, "apikey": api_key}
    attempt = 1
    delay = BASE_DELAY

    while attempt <= MAX_RETRIES:
        try:
            async with session.get(config.TRONSCAN_API_URL, params=params, timeout=10) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    print(f"[{address}] 请求失败，状态码: {response.status}. 正在重试 {attempt}/{MAX_RETRIES}...")
        except Exception as e:
            print(f"[{address}] 请求异常: {e}. 正在重试 {attempt}/{MAX_RETRIES}...")
        await asyncio.sleep(delay)
        delay *= BACKOFF_FACTOR
        attempt += 1

    print(f"[{address}] 达到最大重试次数 {MAX_RETRIES}, 放弃请求。")
    return None

# 对单个地址进行轮询，根据指定轮询间隔持续采集数据
async def poll_address(address, interval):
    """
    对某个地址进行轮询，每个轮询周期内尝试使用所有 APIKey。
    """
    async with aiohttp.ClientSession() as session:
        while True:
            for api_key in config.API_KEYS:
                data = await fetch_transactions(session, address, api_key)
                if data:
                    # 假设 API 返回的数据中存在一个 'transactions' 字段
                    tx_list = data.get("transactions", [])
                    for tx in tx_list:
                        # 数据处理与去重请在这里进一步实现
                        try:
                            # 将交易数据写入 MongoDB数据库
                            await db.collection.insert_one(tx)
                            print(f"[{address}] 成功写入交易：{tx.get('txid', '未知')}")
                            # 通过 Telegram 发送通知
                            notify_new_transaction(f"[{address}] 新交易：{tx.get('txid', '未知')}")
                        except Exception as e:
                            print(f"[{address}] 数据写入失败：{e}")
                    # 当某个 APIKey 成功返回数据后，不再尝试后续 key
                    break
            await asyncio.sleep(interval)

# 主入口，启动所有地址的轮询任务
async def main():
    # 为每个待监控地址创建一个任务
    tasks = []
    for item in config.ADDRESSES:
        address = item["address"]
        interval = item.get("interval", 5)
        tasks.append(asyncio.create_task(poll_address(address, interval)))
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main()) 