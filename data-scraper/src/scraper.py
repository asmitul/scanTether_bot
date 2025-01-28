# How to use your API Key?
# curl -H 'TRON-PRO-API-KEY:your_api_key' 'https://apilist.tronscanapi.com/api/block'

# Get account detail information
# https://apilist.tronscanapi.com/api/accountv2?address=TSTVYwFDp7SBfZk7Hrz3tucwQVASyJdwC7

# Get a list of transactions
# https://apilist.tronscanapi.com/api/transaction?sort=-timestamp&count=true&limit=20&start=0&start_timestamp=1529856000000&end_timestamp=1680503191391


import requests
import time
from datetime import datetime
import os
from pymongo import MongoClient

class USDTMonitor:
    def __init__(self):
        self.base_url = "https://apilist.tronscanapi.com/api"
        self.mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
        self.client = MongoClient(self.mongodb_uri)
        self.db = self.client.tron_monitor
        
    def get_account_info(self, address):
        """获取账户信息"""
        endpoint = f"{self.base_url}/accountv2"
        params = {"address": address}
        response = requests.get(endpoint, params=params)
        return response.json()
    
    def get_transactions(self, address, limit=20):
        """获取最近的交易记录"""
        endpoint = f"{self.base_url}/transaction"
        current_timestamp = int(time.time() * 1000)
        params = {
            "address": address,
            "limit": limit,
            "start": 0,
            "sort": "-timestamp",
            "count": True,
            "start_timestamp": 0,
            "end_timestamp": current_timestamp
        }
        response = requests.get(endpoint, params=params)
        return response.json()
    
    def monitor_address(self, address):
        """监控指定地址"""
        while True:
            try:
                # 获取最新交易
                transactions = self.get_transactions(address)
                
                # 保存到MongoDB
                for tx in transactions.get("data", []):
                    self.db.transactions.update_one(
                        {"hash": tx["hash"]},
                        {"$setOnInsert": tx},
                        upsert=True
                    )
                
                # 每60秒检查一次
                time.sleep(60)
                
            except Exception as e:
                print(f"Error monitoring address {address}: {str(e)}")
                time.sleep(60)  # 发生错误时等待60秒后重试

def main():
    monitor = USDTMonitor()
    # 这里替换为要监控的USDT地址
    target_address = "TMqDrZa5kEebg5wi3W3wusVZ6ZF2w6JczH"
    monitor.monitor_address(target_address)

if __name__ == "__main__":
    main()

