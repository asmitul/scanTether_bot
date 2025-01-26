from prometheus_client import Counter, Histogram, Gauge, Info
from prometheus_client import start_http_server
from functools import wraps
import time

# 交易相关指标
TRANSACTIONS_PROCESSED = Counter(
    'usdt_transactions_processed_total',
    'Total number of USDT transactions processed',
    ['status']  # success, failed
)

TRANSACTION_AMOUNT = Histogram(
    'usdt_transaction_amount',
    'USDT transaction amounts',
    buckets=[1, 10, 100, 1000, 10000, 100000]
)

# API 请求指标
API_REQUESTS = Counter(
    'api_requests_total',
    'Total API requests made',
    ['endpoint', 'method', 'status']
)

API_REQUEST_DURATION = Histogram(
    'api_request_duration_seconds',
    'API request duration in seconds',
    ['endpoint'],
    buckets=[0.1, 0.5, 1.0, 2.0, 5.0]
)

# 数据库指标
DB_OPERATIONS = Counter(
    'db_operations_total',
    'Total database operations',
    ['operation', 'status']
)

DB_OPERATION_DURATION = Histogram(
    'db_operation_duration_seconds',
    'Database operation duration in seconds',
    ['operation'],
    buckets=[0.01, 0.05, 0.1, 0.5, 1.0]
)

# 系统指标
ACTIVE_ADDRESSES = Gauge(
    'active_addresses',
    'Number of active addresses being monitored'
)

BOT_INFO = Info('telegram_bot', 'Telegram bot information')

# 重试指标
RETRY_ATTEMPTS = Counter(
    'retry_attempts_total',
    'Total number of retry attempts',
    ['operation']
)

CIRCUIT_BREAKER_STATE = Gauge(
    'circuit_breaker_state',
    'Circuit breaker state (0=closed, 1=half-open, 2=open)',
    ['operation']
)

def track_time(metric, labels=None):
    """
    装饰器：跟踪函数执行时间
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)
                return result
            except Exception as e:
                if labels:
                    metric.labels(**labels).observe(time.time() - start_time)
                else:
                    metric.observe(time.time() - start_time)
                raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                if labels:
                    metric.labels(**labels).observe(duration)
                else:
                    metric.observe(duration)
                return result
            except Exception as e:
                if labels:
                    metric.labels(**labels).observe(time.time() - start_time)
                else:
                    metric.observe(time.time() - start_time)
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator

def init_metrics(port=8000):
    """
    初始化并启动指标服务器
    """
    start_http_server(port)
    BOT_INFO.info({'version': '1.0.0'}) 