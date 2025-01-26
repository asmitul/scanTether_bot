import asyncio
from datetime import datetime
from typing import Any, Callable, TypeVar, Optional
from functools import wraps
import aiohttp
from ..config import REQUEST_TIMEOUT, MAX_RETRIES, RETRY_DELAY
from .logger import logger

T = TypeVar('T')

def format_amount(amount: float, decimals: int = 6) -> str:
    """
    格式化USDT金额
    
    Args:
        amount: USDT金额
        decimals: 小数位数
    
    Returns:
        str: 格式化后的金额字符串
    """
    return f"{amount:,.{decimals}f} USDT"

def format_timestamp(timestamp: datetime) -> str:
    """
    格式化时间戳为人类可读格式
    
    Args:
        timestamp: datetime对象
    
    Returns:
        str: 格式化后的时间字符串
    """
    return timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")

async def make_request(
    url: str,
    method: str = "GET",
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    json: Optional[dict] = None,
) -> dict:
    """
    发送HTTP请求，带有重试机制
    
    Args:
        url: 请求URL
        method: HTTP方法
        headers: 请求头
        params: URL参数
        json: JSON数据
    
    Returns:
        dict: 响应数据
    
    Raises:
        Exception: 请求失败
    """
    async with aiohttp.ClientSession() as session:
        for attempt in range(MAX_RETRIES):
            try:
                async with session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=json,
                    timeout=REQUEST_TIMEOUT
                ) as response:
                    response.raise_for_status()
                    return await response.json()
            except Exception as e:
                if attempt == MAX_RETRIES - 1:
                    logger.error(f"Request failed after {MAX_RETRIES} attempts: {str(e)}")
                    raise
                logger.warning(f"Request attempt {attempt + 1} failed: {str(e)}")
                await asyncio.sleep(RETRY_DELAY)

def async_retry(
    retries: int = MAX_RETRIES,
    delay: float = RETRY_DELAY
) -> Callable:
    """
    异步函数重试装饰器
    
    Args:
        retries: 重试次数
        delay: 重试延迟（秒）
    
    Returns:
        Callable: 装饰器函数
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == retries - 1:
                        logger.error(f"Function {func.__name__} failed after {retries} attempts: {str(e)}")
                        raise
                    logger.warning(f"Function {func.__name__} attempt {attempt + 1} failed: {str(e)}")
                    await asyncio.sleep(delay)
        return wrapper
    return decorator

def validate_tron_address(address: str) -> bool:
    """
    验证TRON地址格式
    
    Args:
        address: TRON地址
    
    Returns:
        bool: 是否是有效的TRON地址
    """
    # TRON地址以T开头，长度为34个字符
    if not address.startswith('T') or len(address) != 34:
        return False
    
    # 可以添加更多的验证逻辑
    return True 