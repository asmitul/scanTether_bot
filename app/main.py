from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect, BackgroundTasks
import asyncio
import json
from app import db
from bson.objectid import ObjectId

app = FastAPI(title="TRC20 USDT 交易数据查询 API")

# 查询指定地址的交易记录（默认返回最近 100 条，按时间倒序排列）
@app.get("/transactions/{address}")
async def get_transactions(address: str, limit: int = 100):
    cursor = db.collection.find({"from": address})  # 这里假设交易数据中"from"字段存储发送地址，可以根据实际情况修改查询条件
    cursor = cursor.sort("timestamp", -1).limit(limit)
    transactions = []
    async for tx in cursor:
        tx["_id"] = str(tx["_id"])  # 转换 ObjectId 为字符串
        transactions.append(tx)
    return transactions

# 健康检查接口
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# WebSocket 连接管理器
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        print("WebSocket客户端已连接，当前连接数：", len(self.active_connections))

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        print("WebSocket客户端已断开，当前连接数：", len(self.active_connections))

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# WebSocket 接口，客户端通过 /ws 路径建立连接
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # 接收客户端发送的消息（此处仅实现简单的回显功能）
            data = await websocket.receive_text()
            await manager.send_personal_message(f"你发送的消息: {data}", websocket)
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 后台任务：模拟实时推送新交易数据
async def push_new_transactions():
    while True:
        # 模拟数据，可替换为实际交易数据的推送逻辑，例如通过订阅任务队列或数据库变化流
        dummy_transaction = {
            "txid": "dummy_tx_id",
            "amount": 100,
            "status": "new"
        }
        message = json.dumps(dummy_transaction)
        print("Broadcasting new transaction:", message)
        await manager.broadcast(message)
        await asyncio.sleep(10)  # 每隔10秒推送一次

# 服务启动时启动后台任务
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(push_new_transactions()) 