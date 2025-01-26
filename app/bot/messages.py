from typing import List
from ..database.models import Transaction
from ..utils.helpers import format_amount, format_timestamp

# 帮助消息
HELP_MESSAGE = """
🤖 USDT 交易跟踪机器人使用指南：

基本命令：
/start - 启动机器人
/help - 显示此帮助信息
/add <地址> [备注] - 添加监控地址
/remove <地址> - 移除监控地址
/list - 查看所有监控地址
/txs <地址> - 查看地址最近交易

示例：
添加地址：/add TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx 我的钱包
查看交易：/txs TRxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

注意：
- 地址必须是有效的TRON地址（以T开头）
- 备注是可选的，但建议添加以便识别
- 每个地址的更新间隔约为5分钟
"""

START_MESSAGE = """
👋 欢迎使用 USDT 交易跟踪机器人！

这个机器人可以帮助你监控TRON网络上的USDT交易。
使用 /help 查看完整的命令列表和使用说明。
"""

# 地址相关消息模板
ADDRESS_ADDED = "✅ 成功添加监控地址：\n地址：`{}`\n备注：{}"
ADDRESS_REMOVED = "✅ 已移除监控地址：`{}`"
ADDRESS_ALREADY_EXISTS = "❌ 该地址已在监控列表中"
ADDRESS_NOT_FOUND = "❌ 未找到该监控地址"
INVALID_ADDRESS = "❌ 无效的TRON地址格式"

def format_address_list(addresses: List[dict]) -> str:
    """格式化地址列表消息"""
    if not addresses:
        return "📝 当前没有监控的地址"
    
    message = "📝 当前监控的地址列表：\n\n"
    for i, addr in enumerate(addresses, 1):
        note = f" - {addr['note']}" if addr.get('note') else ""
        message += f"{i}. `{addr['address']}`{note}\n"
    return message

def format_transaction(tx: Transaction, watched_address: str) -> str:
    """格式化单条交易消息"""
    is_receive = tx.to_address == watched_address
    direction = "收到 ⬇️" if is_receive else "发送 ⬆️"
    other_address = tx.from_address if is_receive else tx.to_address
    
    return (
        f"💫 {direction} USDT交易\n"
        f"金额：{format_amount(tx.amount)}\n"
        f"{'来自' if is_receive else '发往'}：`{other_address}`\n"
        f"时间：{format_timestamp(tx.timestamp)}\n"
        f"交易ID：`{tx.tx_id}`"
    )

def format_transaction_list(txs: List[Transaction], address: str) -> str:
    """格式化交易列表消息"""
    if not txs:
        return f"📊 地址 `{address}` 暂无交易记录"
    
    message = f"📊 地址 `{address}` 的最近交易记录：\n\n"
    for tx in txs:
        message += f"{format_transaction(tx, address)}\n\n"
    return message

# 新交易通知消息
def format_new_transaction_alert(tx: Transaction, note: str = None) -> str:
    """格式化新交易通知消息"""
    address_info = f"({note})" if note else ""
    return (
        f"🔔 检测到新交易 {address_info}\n\n"
        f"{format_transaction(tx, tx.to_address)}"
    )

# 错误消息
GENERAL_ERROR = "❌ 操作失败，请稍后重试"
NETWORK_ERROR = "❌ 网络请求失败，请稍后重试" 