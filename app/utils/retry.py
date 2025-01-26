import asyncio
import functools
from typing import Type, Tuple, Optional, Callable, Any
from datetime import datetime
from .logger import setup_logger

logger = setup_logger('utils.retry')

class RetryError(Exception):
    """重试失败异常"""
    pass

def async_retry(
    retries: int = 3,
    delay: float = 1.0,
    max_delay: float = 10.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    异步函数重试装饰器
    
    Args:
        retries: 最大重试次数
        delay: 初始延迟时间（秒）
        max_delay: 最大延迟时间（秒）
        exponential_base: 指数退避基数
        exceptions: 需要重试的异常类型
        on_retry: 重试时的回调函数
    """
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            current_delay = delay

            for attempt in range(retries + 1):
                try:
                    return await func(*args, **kwargs)
                
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == retries:
                        logger.error(
                            f"Function {func.__name__} failed after {retries} retries. "
                            f"Last error: {str(e)}"
                        )
                        raise RetryError(f"Max retries exceeded: {str(e)}") from e
                    
                    # 计算下一次重试的延迟时间
                    wait_time = min(current_delay, max_delay)
                    
                    # 记录重试信息
                    logger.warning(
                        f"Retry {attempt + 1}/{retries} for {func.__name__} "
                        f"after {wait_time:.2f}s. Error: {str(e)}"
                    )
                    
                    # 执行重试回调
                    if on_retry:
                        try:
                            await on_retry(attempt, last_exception, *args, **kwargs)
                        except Exception as callback_error:
                            logger.error(f"Retry callback error: {str(callback_error)}")
                    
                    # 等待后重试
                    await asyncio.sleep(wait_time)
                    
                    # 更新延迟时间（指数退避）
                    current_delay *= exponential_base
            
            return None  # 不应该到达这里
        return wrapper
    return decorator

class CircuitBreaker:
    """断路器模式实现"""
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: float = 60.0,
        half_open_timeout: float = 30.0
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.half_open_timeout = half_open_timeout
        
        self.failures = 0
        self.last_failure_time = None
        self.state = "closed"  # closed, open, or half-open
    
    def can_execute(self) -> bool:
        """检查是否可以执行"""
        now = datetime.utcnow()
        
        if self.state == "closed":
            return True
            
        if self.state == "open":
            # 检查是否可以进入半开状态
            if (now - self.last_failure_time).total_seconds() >= self.reset_timeout:
                self.state = "half-open"
                return True
            return False
            
        # 半开状态
        return True
    
    def record_success(self):
        """记录成功执行"""
        self.failures = 0
        self.state = "closed"
    
    def record_failure(self):
        """记录失败执行"""
        self.failures += 1
        self.last_failure_time = datetime.utcnow()
        
        if self.failures >= self.failure_threshold:
            self.state = "open"

def circuit_breaker(
    failure_threshold: int = 5,
    reset_timeout: float = 60.0,
    half_open_timeout: float = 30.0
):
    """断路器装饰器"""
    breaker = CircuitBreaker(
        failure_threshold=failure_threshold,
        reset_timeout=reset_timeout,
        half_open_timeout=half_open_timeout
    )
    
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if not breaker.can_execute():
                raise RetryError("Circuit breaker is open")
            
            try:
                result = await func(*args, **kwargs)
                breaker.record_success()
                return result
            except Exception as e:
                breaker.record_failure()
                raise
                
        return wrapper
    return decorator 